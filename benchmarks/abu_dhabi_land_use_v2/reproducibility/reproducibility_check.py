#!/usr/bin/env python3
"""Fail closed when a v2 archive does not match its declared evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parents[1]
REPO = HERE.parents[1]
MANIFESTS = (
    HERE / "reproducibility" / "MANIFEST.json",
    HERE / "reproducibility" / "PUBLICATION_OUTPUTS.json",
)


def digest(path: Path, hash_mode: str) -> tuple[str, int]:
    raw = path.read_bytes()
    if hash_mode == "text_lf_normalized":
        raw = raw.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    elif hash_mode != "raw":
        raise ValueError(f"unknown_hash_mode:{hash_mode}")
    return hashlib.sha256(raw).hexdigest(), len(raw)


def verify_manifest(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {"path": path.name, "exists": False, "records": [], "ok": False}
    document = json.loads(path.read_text(encoding="utf-8"))
    rows = []
    for record in document.get("records", []):
        target = REPO / str(record["path"])
        exists = target.is_file()
        actual_hash, actual_bytes = digest(target, str(record["hash_mode"])) if exists else (None, None)
        rows.append(
            {
                "path": record["path"],
                "role": record["role"],
                "exists": exists,
                "bytes_ok": exists and actual_bytes == int(record["bytes"]),
                "sha256_ok": exists and actual_hash == record["sha256"],
            }
        )
    ok = bool(rows) and all(row["exists"] and row["bytes_ok"] and row["sha256_ok"] for row in rows)
    return {
        "path": path.relative_to(REPO).as_posix(),
        "exists": True,
        "schema": document.get("schema"),
        "record_count": len(rows),
        "records": rows,
        "ok": ok,
    }


def check(manifest_paths: tuple[Path, ...] = MANIFESTS) -> dict[str, Any]:
    manifests = [verify_manifest(path) for path in manifest_paths]
    report_paths = {
        "arcgis_backtest": HERE / "artifacts" / "arcgis_v2_historical_backtest" / "report.json",
        "dynamic_world_matched_backtest": HERE / "artifacts" / "dynamic_world_matched_backtest" / "report.json",
        "cross_product_summary": HERE / "results_arcgis_v2" / "paper_refresh" / "product_robustness_summary.json",
    }
    report_status = {}
    for label, path in report_paths.items():
        exists = path.is_file()
        content = json.loads(path.read_text(encoding="utf-8")) if exists else {}
        report_status[label] = {
            "exists": exists,
            "status": content.get("status"),
            "complete": content.get("status") == "complete",
        }
    complete = all(item["ok"] for item in manifests) and all(item["complete"] for item in report_status.values())
    return {
        "schema": "gwm.abu_dhabi_v2.reproducibility_check.v1",
        "benchmark_id": "abu-dhabi-land-use-v2",
        "created_at": datetime.now(UTC).isoformat(),
        "status": "PASS" if complete else "BLOCKED",
        "python": sys.version.split()[0],
        "manifests": manifests,
        "core_reports": report_status,
        "claim_boundary": "PASS verifies the declared public-data v2 archive and frozen outputs. It does not assert that either public land-cover product is authoritative Abu Dhabi land-use truth.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--working", action="store_true", help="Check working revision manifests, not the published release")
    args = parser.parse_args()
    paths = tuple(HERE / "reproducibility" / "working" / p.name for p in MANIFESTS) if args.working else MANIFESTS
    report = check(paths)
    report["revision_scope"] = "working_revision" if args.working else "published_release"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "manifest_records": sum(item.get("record_count", 0) for item in report["manifests"])}))
    raise SystemExit(0 if report["status"] == "PASS" else 2)


if __name__ == "__main__":
    main()
