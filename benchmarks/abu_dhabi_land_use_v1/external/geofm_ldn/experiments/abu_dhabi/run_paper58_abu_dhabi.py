"""Train and evaluate Paper58 on the unified Abu Dhabi land-use benchmark."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from copy import deepcopy
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np
import rasterio
import torch
import torch.nn.functional as F
from sklearn.linear_model import LogisticRegression

REPO_ROOT = Path(__file__).resolve().parents[2]
PAPER8_ROOT = REPO_ROOT / "experiments/paper8"
# This runner is vendored below the benchmark itself.  Deriving the default
# from the file location keeps a clean checkout independent of the original
# workstation path (the upstream project used ``/Users/.../gisdataagent``).
DEFAULT_BENCHMARK_ROOT = Path(__file__).resolve().parents[4]
for path in (PAPER8_ROOT,):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from paper58_runtime import build_demand_conditioned_model

FIT_TRANSITIONS = ((2017, 2018), (2018, 2019), (2019, 2020), (2020, 2021))
VALIDATION_TRANSITION = (2021, 2022)
CLASSES = tuple(range(1, 7))
SEEDS = (31, 47, 73)
PATCH_SIZE = 64


def choose_device(requested: str) -> torch.device:
    if requested != "auto":
        return torch.device(requested)
    if torch.backends.mps.is_available():
        return torch.device("mps")
    if torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


def _read(path: Path) -> tuple[np.ndarray, dict[str, Any], float | int | None]:
    with rasterio.open(path) as dataset:
        return dataset.read(), dataset.profile.copy(), dataset.nodata


def _write_state(
    path: Path,
    values: np.ndarray,
    reference: dict[str, Any],
    *,
    valid_mask: np.ndarray,
) -> None:
    profile = reference.copy()
    profile.update(
        count=1,
        dtype="uint8",
        nodata=0,
        compress="deflate",
        tiled=True,
        blockxsize=256,
        blockysize=256,
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(f".partial.{os.getpid()}.tif")
    output = values.astype(np.uint8, copy=True)
    output[~valid_mask] = 0
    with rasterio.open(temp, "w", **profile) as dataset:
        dataset.write(output, 1)
        dataset.set_band_description(1, "paper58_predicted_land_cover")
    os.replace(temp, path)


def patch_starts(length: int, size: int) -> tuple[int, ...]:
    values = list(range(0, max(1, length - size + 1), size))
    final = max(0, length - size)
    if not values or values[-1] != final:
        values.append(final)
    return tuple(values)


class BenchmarkData:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.input_root = root / "artifacts/gee"
        self.bundle_root = root / "artifacts/bundle"
        city, self.reference, _ = _read(root / "artifacts/abu_dhabi_city_100m_mask.tif")
        common, _, _ = _read(self.bundle_root / "common_valid_mask_100m.tif")
        hard, _, _ = _read(self.bundle_root / "hard_exclusion_2022_100m.tif")
        self.city = city[0].astype(bool)
        self.valid = common[0].astype(bool)
        self.hard = hard[0].astype(bool)
        self.states = {
            year: _read(
                self.input_root / "land_cover" / f"land_cover_{year}_100m.tif"
            )[0][0]
            for year in range(2017, 2025)
        }
        self.embeddings: dict[int, np.ndarray] = {}

    def embedding(self, year: int) -> np.ndarray:
        if year not in self.embeddings:
            values, _, nodata = _read(
                self.input_root / "alphaearth" / f"alphaearth_{year}_100m.tif"
            )
            values = values.astype(np.float32)
            values[values == nodata] = 0.0
            self.embeddings[year] = values
        return self.embeddings[year]

    def action_vector(self, start_year: int, target_year: int) -> np.ndarray:
        start = np.array(
            [np.count_nonzero(self.valid & (self.states[start_year] == value)) for value in CLASSES],
            dtype=np.float32,
        )
        target = np.array(
            [np.count_nonzero(self.valid & (self.states[target_year] == value)) for value in CLASSES],
            dtype=np.float32,
        )
        total = float(self.valid.sum())
        return np.concatenate([target / total, (target - start) / total]).astype(np.float32)

    def training_patches(self) -> list[tuple[int, int, int, int]]:
        patches = []
        for start_year, target_year in FIT_TRANSITIONS:
            for row in patch_starts(self.valid.shape[0], PATCH_SIZE):
                for column in patch_starts(self.valid.shape[1], PATCH_SIZE):
                    valid = self.valid[row : row + PATCH_SIZE, column : column + PATCH_SIZE]
                    if int(valid.sum()) >= 64:
                        patches.append((start_year, target_year, row, column))
        return patches


def train_decoder(
    data: BenchmarkData,
    *,
    seed: int,
    samples_per_class_year: int = 2000,
) -> tuple[LogisticRegression, dict[str, Any]]:
    rng = np.random.default_rng(seed)
    rows = []
    labels = []
    for year in range(2017, 2022):
        embedding = data.embedding(year)
        state = data.states[year]
        for value in CLASSES:
            candidates = np.flatnonzero(data.valid.ravel() & (state.ravel() == value))
            selected = rng.choice(
                candidates,
                size=min(samples_per_class_year, len(candidates)),
                replace=False,
            )
            rows.append(embedding.reshape(64, -1)[:, selected].T)
            labels.append(np.full(len(selected), value - 1, dtype=np.int64))
    x = np.concatenate(rows)
    y = np.concatenate(labels)
    decoder = LogisticRegression(
        C=1.0,
        class_weight="balanced",
        max_iter=300,
        random_state=seed,
        solver="lbfgs",
    )
    started = time.perf_counter()
    decoder.fit(x, y)
    validation_embedding = data.embedding(2022).reshape(64, -1)[:, data.valid.ravel()].T
    validation_label = data.states[2022][data.valid] - 1
    return decoder, {
        "training_samples": len(x),
        "training_accuracy": float(decoder.score(x, y)),
        "validation_2022_accuracy": float(decoder.score(validation_embedding, validation_label)),
        "fit_seconds": time.perf_counter() - started,
        "label_years": list(range(2017, 2022)),
    }


def decoder_tensors(
    decoder: LogisticRegression,
    device: torch.device,
) -> tuple[torch.Tensor, torch.Tensor]:
    weight = torch.tensor(decoder.coef_, dtype=torch.float32, device=device).view(6, 64, 1, 1)
    bias = torch.tensor(decoder.intercept_, dtype=torch.float32, device=device)
    return weight, bias


def semantic_logits(
    state: torch.Tensor,
    decoder_weight: torch.Tensor,
    decoder_bias: torch.Tensor,
) -> torch.Tensor:
    return F.conv2d(state, decoder_weight, decoder_bias)


def train_ldn(
    data: BenchmarkData,
    *,
    decoder: LogisticRegression,
    seed: int,
    epochs: int,
    batch_size: int,
    learning_rate: float,
    device: torch.device,
) -> tuple[torch.nn.Module, dict[str, Any]]:
    torch.manual_seed(seed)
    np.random.seed(seed)
    model = build_demand_conditioned_model(6, z_dim=64, n_context=0).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate, weight_decay=1e-4)
    decoder_weight, decoder_bias = decoder_tensors(decoder, device)
    patches = data.training_patches()
    rng = np.random.default_rng(seed)
    best_score = float("-inf")
    best_state = deepcopy(model.state_dict())
    history = []
    started = time.perf_counter()
    for epoch in range(epochs):
        model.train()
        order = rng.permutation(len(patches))
        losses = []
        for offset in range(0, len(order), batch_size):
            batch_records = [patches[int(index)] for index in order[offset : offset + batch_size]]
            starts = []
            targets = []
            labels = []
            masks = []
            changes = []
            actions = []
            hard_masks = []
            for start_year, target_year, row, column in batch_records:
                rows = slice(row, row + PATCH_SIZE)
                columns = slice(column, column + PATCH_SIZE)
                starts.append(data.embedding(start_year)[:, rows, columns])
                targets.append(data.embedding(target_year)[:, rows, columns])
                target_label = data.states[target_year][rows, columns]
                start_label = data.states[start_year][rows, columns]
                labels.append(target_label.astype(np.int64) - 1)
                valid = data.valid[rows, columns]
                masks.append(valid)
                changes.append(valid & (start_label != target_label))
                actions.append(data.action_vector(start_year, target_year))
                hard_masks.append(
                    valid & np.isin(start_label, (1, 4))
                )
            start_tensor = torch.tensor(np.stack(starts), device=device)
            target_tensor = F.normalize(torch.tensor(np.stack(targets), device=device), p=2, dim=1)
            label_tensor = torch.tensor(np.stack(labels), device=device, dtype=torch.long)
            mask_tensor = torch.tensor(np.stack(masks), device=device, dtype=torch.bool)
            change_tensor = torch.tensor(np.stack(changes), device=device, dtype=torch.bool)
            action_tensor = torch.tensor(np.stack(actions), device=device)
            hard_tensor = torch.tensor(np.stack(hard_masks), device=device, dtype=torch.bool)
            prediction = F.normalize(model(start_tensor, action_tensor), p=2, dim=1)
            cosine = F.cosine_similarity(prediction, target_tensor, dim=1)
            pixel_weight = 1.0 + 5.0 * change_tensor.float()
            embedding_loss = ((1.0 - cosine) * pixel_weight)[mask_tensor].mean()
            logits = semantic_logits(prediction, decoder_weight, decoder_bias)
            semantic = F.cross_entropy(
                logits,
                label_tensor,
                reduction="none",
                ignore_index=-1,
            )
            semantic_loss = (semantic * pixel_weight)[mask_tensor].mean()
            probabilities = torch.softmax(logits, dim=1)
            predicted_fractions = []
            target_fractions = []
            for batch_index in range(len(batch_records)):
                valid = mask_tensor[batch_index]
                predicted_fractions.append(
                    probabilities[batch_index, :, valid].mean(dim=1)
                )
                one_hot = F.one_hot(
                    label_tensor[batch_index, valid], num_classes=6
                ).float()
                target_fractions.append(one_hot.mean(dim=0))
            demand_loss = F.mse_loss(
                torch.stack(predicted_fractions), torch.stack(target_fractions)
            )
            if hard_tensor.any():
                constraint_loss = (
                    1.0
                    - F.cosine_similarity(prediction, start_tensor, dim=1)[hard_tensor]
                ).mean()
            else:
                constraint_loss = torch.zeros((), device=device)
            loss = (
                embedding_loss
                + 0.5 * semantic_loss
                + 0.1 * demand_loss
                + 0.2 * constraint_loss
            )
            optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            losses.append(float(loss.detach().cpu()))
        validation = validate_ldn(
            model,
            data,
            decoder_weight=decoder_weight,
            decoder_bias=decoder_bias,
            device=device,
        )
        score = validation["mean_cosine"] + 0.05 * validation["semantic_accuracy"]
        if score > best_score:
            best_score = score
            best_state = deepcopy(model.state_dict())
        history.append(
            {
                "epoch": epoch + 1,
                "train_loss": float(np.mean(losses)),
                **validation,
            }
        )
        print(
            f"paper58:seed_{seed}:epoch_{epoch + 1}:"
            f"loss={np.mean(losses):.6f}:val_cos={validation['mean_cosine']:.6f}",
            flush=True,
        )
    model.load_state_dict(best_state)
    model.eval()
    return model, {
        "training_patch_count": len(patches),
        "epochs": epochs,
        "batch_size": batch_size,
        "best_selection_score": best_score,
        "history": history,
        "fit_seconds": time.perf_counter() - started,
    }


def predict_tiled(
    model: torch.nn.Module,
    embedding: np.ndarray,
    action: np.ndarray,
    *,
    device: torch.device,
) -> np.ndarray:
    output = np.zeros_like(embedding, dtype=np.float32)
    weight = np.zeros(embedding.shape[1:], dtype=np.float32)
    model.eval()
    with torch.no_grad():
        for row in patch_starts(embedding.shape[1], PATCH_SIZE):
            for column in patch_starts(embedding.shape[2], PATCH_SIZE):
                patch = torch.tensor(
                    embedding[:, row : row + PATCH_SIZE, column : column + PATCH_SIZE],
                    device=device,
                ).unsqueeze(0)
                action_tensor = torch.tensor(action, device=device).unsqueeze(0)
                prediction = F.normalize(model(patch, action_tensor), p=2, dim=1)
                values = prediction.squeeze(0).cpu().numpy()
                output[:, row : row + PATCH_SIZE, column : column + PATCH_SIZE] += values
                weight[row : row + PATCH_SIZE, column : column + PATCH_SIZE] += 1
    output /= np.maximum(weight, 1e-6)[None, ...]
    norm = np.linalg.norm(output, axis=0, keepdims=True)
    return np.divide(output, norm, out=np.zeros_like(output), where=norm > 1e-8)


def validate_ldn(
    model: torch.nn.Module,
    data: BenchmarkData,
    *,
    decoder_weight: torch.Tensor,
    decoder_bias: torch.Tensor,
    device: torch.device,
) -> dict[str, float]:
    start_year, target_year = VALIDATION_TRANSITION
    prediction = predict_tiled(
        model,
        data.embedding(start_year),
        data.action_vector(start_year, target_year),
        device=device,
    )
    valid = data.valid
    target = data.embedding(target_year)
    cosine = np.sum(prediction[:, valid] * target[:, valid], axis=0)
    logits = (
        decoder_weight.detach().cpu().numpy()[:, :, 0, 0] @ prediction.reshape(64, -1)
        + decoder_bias.detach().cpu().numpy()[:, None]
    )
    semantic = np.argmax(logits, axis=0).reshape(valid.shape) + 1
    return {
        "mean_cosine": float(np.mean(cosine)),
        "semantic_accuracy": float(np.mean(semantic[valid] == data.states[target_year][valid])),
    }


def action_from_record(record: dict[str, Any], start_counts: dict[int, int]) -> np.ndarray:
    target = np.array(
        [int(record["feasible_target_counts"][str(value)]) for value in CLASSES],
        dtype=np.float32,
    )
    start = np.array([start_counts[value] for value in CLASSES], dtype=np.float32)
    total = float(target.sum())
    return np.concatenate([target / total, (target - start) / total]).astype(np.float32)


def run_seed(
    data: BenchmarkData,
    *,
    benchmark_root: Path,
    output_root: Path,
    seed: int,
    epochs: int,
    batch_size: int,
    learning_rate: float,
    device: torch.device,
    checkpoint_root: Path | None = None,
    use_checkpoint: bool = False,
) -> dict[str, Any]:
    decoder, decoder_report = train_decoder(data, seed=seed)
    model = build_demand_conditioned_model(6, z_dim=64, n_context=0).to(device)
    checkpoint_path = (checkpoint_root or output_root) / f"seed_{seed}" / "paper58_ldn.pt"
    if use_checkpoint:
        if not checkpoint_path.is_file():
            raise FileNotFoundError(f"paper58_checkpoint_missing:{checkpoint_path}")
        model.load_state_dict(torch.load(checkpoint_path, map_location=device, weights_only=True))
        model.eval()
        training = {
            "loaded_checkpoint": str(checkpoint_path.relative_to(benchmark_root)),
            "epochs": 0,
            "checkpoint_sha256": hashlib.sha256(checkpoint_path.read_bytes()).hexdigest(),
        }
    else:
        model, training = train_ldn(
            data,
            decoder=decoder,
            seed=seed,
            epochs=epochs,
            batch_size=batch_size,
            learning_rate=learning_rate,
            device=device,
        )
    benchmark_module_path = str(benchmark_root)
    if benchmark_module_path not in sys.path:
        sys.path.insert(0, benchmark_module_path)
    from run_geospatial_kernel import allocate_action
    from shared import class_counts, evaluate_prediction

    action_records = json.loads(
        (data.bundle_root / "allocation_actions.json").read_text(encoding="utf-8")
    )["actions"]
    current_embedding = data.embedding(2022).copy()
    current_state = data.states[2022].copy()
    year_rows = []
    for record in action_records:
        target_year = int(record["target_year"])
        target_counts = {
            int(key): int(value) for key, value in record["feasible_target_counts"].items()
        }
        action = action_from_record(record, class_counts(current_state, data.valid))
        predicted_embedding = predict_tiled(
            model,
            current_embedding,
            action,
            device=device,
        )
        predicted_embedding[:, data.hard & data.valid] = current_embedding[
            :, data.hard & data.valid
        ]
        logits = (
            decoder.coef_ @ predicted_embedding.reshape(64, -1)
            + decoder.intercept_[:, None]
        )
        logits -= logits.max(axis=0, keepdims=True)
        probability = np.exp(logits)
        probability /= probability.sum(axis=0, keepdims=True)
        probability = probability.reshape(6, *data.valid.shape).astype(np.float32)
        current_state, allocation = allocate_action(
            current_state,
            probability,
            valid=data.valid,
            hard=data.hard,
            target_counts=target_counts,
        )
        current_embedding = predicted_embedding
        output_path = output_root / f"seed_{seed}" / f"prediction_{target_year}.tif"
        _write_state(
            output_path,
            current_state,
            data.reference,
            valid_mask=data.valid,
        )
        reliability, _, _ = _read(benchmark_root / record["reliability_mask"])
        evaluation = evaluate_prediction(
            current_state,
            origin_state=data.states[2022],
            observed_target=data.states[target_year],
            valid_mask=data.valid,
            hard_exclusion_mask=data.hard,
            requested_counts=target_counts,
            reliability_mask=reliability[0].astype(bool),
        )
        year_rows.append(
            {
                "target_year": target_year,
                "prediction_path": str(output_path.relative_to(benchmark_root)),
                "allocation": allocation,
                "evaluation": evaluation,
            }
        )
    output_checkpoint_path = output_root / f"seed_{seed}" / "paper58_ldn.pt"
    if not use_checkpoint:
        output_checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
        torch.save(model.state_dict(), output_checkpoint_path)
    return {
        "seed": seed,
        "decoder": decoder_report,
        "training": training,
        "years": year_rows,
        "checkpoint_path": str((checkpoint_path if use_checkpoint else output_checkpoint_path).relative_to(benchmark_root)),
    }


def run(
    *,
    benchmark_root: Path,
    output_root: Path,
    seeds: tuple[int, ...],
    epochs: int,
    batch_size: int,
    learning_rate: float,
    requested_device: str,
    checkpoint_root: Path | None = None,
    use_checkpoint: bool = False,
) -> dict[str, Any]:
    benchmark_root = benchmark_root.resolve()
    output_root = output_root.resolve()
    if checkpoint_root is not None:
        checkpoint_root = checkpoint_root.resolve()
    started = time.perf_counter()
    device = choose_device(requested_device)
    data = BenchmarkData(benchmark_root)
    reports = []
    for seed in seeds:
        reports.append(
            run_seed(
                data,
                benchmark_root=benchmark_root,
                output_root=output_root,
                seed=seed,
                epochs=epochs,
                batch_size=batch_size,
                learning_rate=learning_rate,
                device=device,
                checkpoint_root=checkpoint_root,
                use_checkpoint=use_checkpoint,
            )
        )
        print(f"paper58:seed_{seed}:complete", flush=True)
    report = {
        "schema": "paper58.abu_dhabi_land_use_run.v1",
        "benchmark_id": "abu-dhabi-land-use-v1",
        "model_id": "paper58",
        "revision_status": "current_protocol_run",
        "created_at": datetime.now(UTC).isoformat(),
        "status": "complete",
        "device": str(device),
        "epochs": epochs,
        "state_writeback": True,
        "test_label_access_during_fit": False,
        "losses": [
            "change_weighted_embedding_cosine",
            "semantic_cross_entropy",
            "patch_demand_consistency",
            "hard_constraint_state_consistency",
        ],
        "seeds": reports,
        "wall_seconds": time.perf_counter() - started,
    }
    output_root.mkdir(parents=True, exist_ok=True)
    (output_root / "report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--benchmark-root", type=Path, default=DEFAULT_BENCHMARK_ROOT)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--seeds", default=",".join(str(value) for value in SEEDS))
    parser.add_argument("--epochs", type=int, default=8)
    parser.add_argument("--batch-size", type=int, default=2)
    parser.add_argument("--learning-rate", type=float, default=3e-4)
    parser.add_argument("--device", default="auto")
    parser.add_argument("--checkpoint-root", type=Path, default=None)
    parser.add_argument(
        "--use-checkpoints",
        action="store_true",
        help="Load the declared checkpoints and regenerate historical rasters without modifying them.",
    )
    args = parser.parse_args()
    benchmark_root = args.benchmark_root.resolve()
    output = args.output or benchmark_root / "artifacts/predictions/paper58"
    report = run(
        benchmark_root=benchmark_root,
        output_root=output,
        seeds=tuple(int(value) for value in args.seeds.split(",") if value.strip()),
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.learning_rate,
        requested_device=args.device,
        checkpoint_root=args.checkpoint_root.resolve() if args.checkpoint_root else None,
        use_checkpoint=args.use_checkpoints,
    )
    print(json.dumps({"status": report["status"], "wall_seconds": report["wall_seconds"]}))


if __name__ == "__main__":
    main()
