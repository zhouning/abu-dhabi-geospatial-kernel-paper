#!/usr/bin/env python3
"""Train ArcGIS-label GeoFM-LDN checkpoints without touching v1 artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import torch

import run_paper58_abu_dhabi as runner


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seeds", default="31,47,73")
    parser.add_argument("--epochs", type=int, default=8)
    parser.add_argument("--batch-size", type=int, default=2)
    parser.add_argument("--learning-rate", type=float, default=3e-4)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--output", type=Path, default=HERE / "artifacts/predictions/geofm_ldn_arcgis")
    args = parser.parse_args()
    data = runner.BenchmarkData(HERE)
    device = runner.choose_device(args.device)
    reports = []
    for seed in tuple(int(value) for value in args.seeds.split(",") if value.strip()):
        decoder, decoder_report = runner.train_decoder(data, seed=seed)
        model, training = runner.train_ldn(
            data,
            decoder=decoder,
            seed=seed,
            epochs=args.epochs,
            batch_size=args.batch_size,
            learning_rate=args.learning_rate,
            device=device,
        )
        checkpoint = args.output / f"seed_{seed}" / "geofm_ldn_arcgis.pt"
        checkpoint.parent.mkdir(parents=True, exist_ok=True)
        torch.save(model.state_dict(), checkpoint)
        reports.append({
            "seed": seed,
            "decoder": decoder_report,
            "training": training,
            "checkpoint": str(checkpoint),
            "checkpoint_sha256": hashlib.sha256(checkpoint.read_bytes()).hexdigest(),
        })
        print(f"geofm_ldn_arcgis:seed_{seed}:complete", flush=True)
    report = {"schema": "gwm.abu_dhabi_geofm_ldn_arcgis_training.v1", "status": "complete", "device": str(device), "epochs": args.epochs, "seeds": reports}
    report_path = args.output / "training_report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "complete", "report": str(report_path.resolve())}))


if __name__ == "__main__":
    main()
