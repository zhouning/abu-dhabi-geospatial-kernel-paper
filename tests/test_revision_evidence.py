"""Checks for mathematical evidence bounds and portable integrity semantics."""
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


def load(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


limits = load("limits", "benchmarks/abu_dhabi_land_use_v2/analyze_allocation_limits.py")
builder = load("manifest_builder", "benchmarks/abu_dhabi_land_use_v2/reproducibility/build_reproducibility_manifest.py")
checker = load("manifest_checker", "benchmarks/abu_dhabi_land_use_v2/reproducibility/reproducibility_check.py")


def normalized_text_bytes(path: Path) -> bytes:
    """Compare deterministic text outputs independently of checkout line endings."""

    return path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")


class RevisionEvidenceTests(unittest.TestCase):
    def test_bound_covers_all_three_class_three_cell_maps(self):
        maps = list(itertools.product(range(3), repeat=3))
        for origin, target, prediction in itertools.product(maps, repeat=3):
            actual = {i for i in range(3) if target[i] != origin[i]}
            predicted = {i for i in range(3) if prediction[i] != origin[i]}
            union = actual | predicted
            if union:
                hits = sum(target[i] == prediction[i] for i in actual & predicted)
                self.assertLessEqual(hits / len(union), limits.count_bound(len(predicted), len(actual)))
        self.assertIsNone(limits.count_bound(0, 0))
        with self.assertRaises(ValueError):
            limits.count_bound(-1, 1)

    def test_portable_text_hashes_and_fail_closed_content_checks(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            previous = checker.REPO
            checker.REPO = root
            try:
                for suffix in (".csv", ".tsv", ".geojson", ".svg"):
                    path = root / ("sample" + suffix)
                    path.write_bytes(b"first\nsecond\n")
                    sha, mode, size = builder.hash_file(path)
                    path.write_bytes(b"first\r\nsecond\r\n")
                    self.assertEqual(builder.hash_file(path), (sha, mode, size))
                    record = {"path": path.name, "role": "test", "bytes": size, "sha256": sha, "hash_mode": mode}
                    manifest = root / "manifest.json"
                    manifest.write_text(json.dumps({"records": [record]}))
                    self.assertTrue(checker.verify_manifest(manifest)["ok"])
                    path.write_bytes(b"edited\r\nsecond\r\n")
                    self.assertFalse(checker.verify_manifest(manifest)["ok"])
                    path.unlink()
                    self.assertFalse(checker.verify_manifest(manifest)["ok"])
                binary = root / "sample.tif"
                binary.write_bytes(b"a\r\nb")
                sha, mode, size = builder.hash_file(binary)
                self.assertEqual(mode, "raw")
                self.assertEqual((sha, size), (hashlib.sha256(b"a\r\nb").hexdigest(), 4))
            finally:
                checker.REPO = previous

    def test_frozen_report_analysis_regenerates_committed_outputs(self):
        source_dir = ROOT / "benchmarks" / "abu_dhabi_land_use_v2" / "results_arcgis_v2" / "allocation_limits"
        source_table = ROOT / "manuscript" / "supplementary_table_S7_allocation_limits.md"
        with tempfile.TemporaryDirectory() as folder:
            generated_dir = Path(folder) / "allocation_limits"
            generated_table = Path(folder) / "supplementary_table_S7_allocation_limits.md"
            self.assertEqual(limits.analyze(generated_dir, generated_table)["status"], "PASS")
            for name in ("count_limits.csv", "model_change_counts.csv", "paired_intervals.csv", "sources.json"):
                self.assertEqual(normalized_text_bytes(generated_dir / name), normalized_text_bytes(source_dir / name), name)
            self.assertEqual(normalized_text_bytes(generated_table), normalized_text_bytes(source_table))

    def test_analysis_invariants_are_explicit_exceptions(self):
        with self.assertRaisesRegex(ValueError, "inconsistent_report"):
            limits.require(False, "inconsistent_report")

    def test_dynamic_world_quality_semantics_remain_consistent(self):
        expected = "maximum temporal-mean probability"
        paths = [
            ROOT / "benchmarks/abu_dhabi_land_use_v2/run_arcgis_historical_backtest.py",
            ROOT / "benchmarks/abu_dhabi_land_use_v2/compile_comparison.py",
            ROOT / "benchmarks/abu_dhabi_land_use_v2/analyze_product_robustness.py",
            ROOT / "benchmarks/abu_dhabi_land_use_v2/artifacts/dynamic_world_matched_backtest/report.json",
            ROOT / "benchmarks/abu_dhabi_land_use_v2/results_arcgis_v2/paper_refresh/product_robustness_summary.md",
        ]
        for path in paths:
            content = path.read_text(encoding="utf-8")
            self.assertIn(expected, content, path)
            self.assertNotIn("mean top-class probability", content, path)
        for name in (
            "figS02_input_label_quality.svg",
            "figS04_driver_layers_and_experiment_design.svg",
        ):
            content = (ROOT / "figures" / name).read_text(encoding="utf-8")
            self.assertIn("quality proxy", content, name)


if __name__ == "__main__":
    unittest.main()
