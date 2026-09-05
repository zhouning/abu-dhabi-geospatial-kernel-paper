#!/usr/bin/env python3
"""Create the immutable input/code manifest used by the rerun gate.

The manifest deliberately excludes generated predictions and figures.  Those
are outputs of ``reproduce.py``; the files below are the fixed inputs and
model assets required to regenerate them.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Iterable


HERE = Path(__file__).resolve().parents[1]
REPO = HERE.parents[1]
OUT = HERE / "reproducibility"


TEXT_SUFFIXES = {
    ".c", ".cc", ".cpp", ".h", ".hpp", ".ini", ".json", ".md", ".py",
    ".rst", ".toml", ".txt", ".yaml", ".yml",
}


def _hash_bytes(path: Path) -> tuple[str, str, int]:
    """Hash text with canonical LF endings so Windows checkouts verify identically."""

    raw = path.read_bytes()
    if path.suffix.lower() in TEXT_SUFFIXES:
        raw = raw.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
        mode = "text_lf_normalized"
    else:
        mode = "raw"
    digest = hashlib.sha256()
    digest.update(raw)
    return digest.hexdigest(), mode, len(raw)


def _add(paths: set[Path], candidates: Iterable[Path]) -> None:
    for path in candidates:
        if path.is_file():
            paths.add(path)


def required_paths() -> dict[str, set[Path]]:
    data: set[Path] = set()
    _add(data, [HERE / "artifacts/abu_dhabi_city_100m_mask.tif"])
    _add(data, (HERE / "artifacts/bundle").glob("*.tif"))
    _add(data, (HERE / "artifacts/bundle").glob("*.json"))
    _add(data, (HERE / "artifacts/gee/alphaearth").glob("alphaearth_[0-9][0-9][0-9][0-9]_100m.tif"))
    _add(data, (HERE / "artifacts/gee/land_cover").glob("*.tif"))
    _add(data, (HERE / "artifacts/gee/viirs").glob("*.tif"))
    _add(data, [HERE / "artifacts/gee/terrain/copernicus_dem_2024_1_slope_100m.tif"])
    _add(data, (HERE / "artifacts/gee/constraints").glob("*.tif"))
    _add(data, [HERE / "artifacts/osm/road_accessibility_100m.tif"])

    models: set[Path] = {
        HERE / "vendor/flus_console",
        HERE / "external/geofm_ldn/experiments/abu_dhabi/run_paper58_abu_dhabi.py",
        HERE / "external/geofm_ldn/experiments/paper8/paper58_runtime.py",
    }
    _add(models, (HERE / "artifacts/predictions/paper58").glob("seed_*/paper58_ldn.pt"))

    config: set[Path] = {
        HERE / "protocol.json",
        HERE / "boundary_manifest.json",
        HERE / "grid_profile.json",
        HERE / "planning_scenarios_public_2025_2031.json",
        HERE / "reproducibility/requirements.lock.txt",
        HERE / "reproducibility/environment.json",
    }
    _add(config, (HERE / "reproducibility").glob("*.py"))

    code: set[Path] = set()
    _add(code, (HERE).glob("*.py"))
    _add(code, (REPO / "data_agent/uwm/geospatial_kernel").glob("*.py"))
    return {"data": data, "model_assets": models, "configuration": config, "code": code}


def build() -> dict[str, object]:
    groups = required_paths()
    missing = [str(path.relative_to(REPO)) for paths in groups.values() for path in sorted(paths) if not path.is_file()]
    if missing:
        raise FileNotFoundError("manifest_missing:" + ",".join(missing))
    records: list[dict[str, object]] = []
    for role, paths in groups.items():
        for path in sorted(paths):
            rel = path.relative_to(REPO).as_posix()
            sha256, hash_mode, canonical_bytes = _hash_bytes(path)
            records.append(
                {
                    "path": rel,
                    "role": role,
                    "bytes": canonical_bytes,
                    "sha256": sha256,
                    "hash_mode": hash_mode,
                }
            )
    records.sort(key=lambda row: str(row["path"]))
    manifest = {
        "schema": "gwm.abu_dhabi_reproducibility_manifest.v2",
        "benchmark_id": "abu-dhabi-land-use-v1",
        "repository_root": ".",
        "generated_by": "benchmarks/abu_dhabi_land_use_v1/reproducibility/build_reproducibility_manifest.py",
        "generated_files_are_not_inputs": True,
        "records": records,
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "MANIFEST.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    sums = "# Text files are hashed after CRLF/CR -> LF normalization; see MANIFEST.json.\n"
    sums += "\n".join(f"{row['sha256']}  {row['path']}" for row in records) + "\n"
    (OUT / "SHA256SUMS").write_text(sums, encoding="utf-8")
    return manifest


if __name__ == "__main__":
    result = build()
    print(json.dumps({"status": "complete", "record_count": len(result["records"])}, ensure_ascii=False))
