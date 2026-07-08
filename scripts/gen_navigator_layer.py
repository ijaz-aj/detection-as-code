#!/usr/bin/env python3
"""
Generate a MITRE ATT&CK Navigator layer from this repo's Sigma rules.

WHY: the layer highlights every technique this project detects. Instead of
hand-maintaining that list (which drifts the moment you add a rule), we read the
`attack.tXXXX[.YYY]` tags straight off the rules -- the SAME tags the rules and
the pytest suite already use. One source of truth, zero drift.

RUN:     python scripts/gen_navigator_layer.py
OUTPUT:  docs/attack-navigator/coverage-layer.json
VIEW:    https://mitre-attack.github.io/attack-navigator/
         -> "Open Existing Layer" -> "Upload from local" -> pick the JSON
"""
from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path

import yaml

# --- Paths (relative to this file, so it works locally and in CI) -----------
REPO_ROOT = Path(__file__).resolve().parents[1]
DETECTIONS_DIR = REPO_ROOT / "detections"
OUTPUT_FILE = REPO_ROOT / "docs" / "attack-navigator" / "coverage-layer.json"

# Matches attack.t1003 OR attack.t1003.001 and captures the "t1003[.001]" part.
TECHNIQUE_TAG = re.compile(r"^attack\.(t\d{4}(?:\.\d{3})?)$", re.IGNORECASE)

COVERED_COLOR = "#2e7d32"  # green = a detection exists for this technique


def load_rule_documents():
    """Every YAML document under detections/ (handles multi-doc correlation files)."""
    docs = []
    for path in sorted(DETECTIONS_DIR.rglob("*.yml")):
        with path.open(encoding="utf-8") as fh:
            for doc in yaml.safe_load_all(fh):
                if doc:
                    docs.append(doc)
    return docs


def build_coverage(docs):
    """Map each ATT&CK technique ID -> the set of rule titles that cover it."""
    coverage = defaultdict(set)
    for doc in docs:
        title = doc.get("title", "(untitled)")
        for tag in doc.get("tags", []):
            match = TECHNIQUE_TAG.match(str(tag))
            if match:
                technique_id = match.group(1).upper()  # t1003.001 -> T1003.001
                coverage[technique_id].add(title)
    return coverage


def build_layer(coverage):
    """Assemble a Navigator layer JSON dict from the coverage map."""
    # Parents of any covered SUB-technique (e.g. T1003 for T1003.001). Navigator
    # hides sub-techniques under a collapsed parent by default, so we must mark
    # those parents `showSubtechniques: true` or the sub-technique greens won't show.
    parents_to_expand = {tid.split(".")[0] for tid in coverage if "." in tid}

    techniques = []
    for technique_id, titles in sorted(coverage.items()):
        entry = {
            "techniqueID": technique_id,
            "score": len(titles),                       # how many rules hit this technique
            "color": COVERED_COLOR,
            "comment": "Detected by: " + "; ".join(sorted(titles)),
            "enabled": True,
        }
        # If this covered technique is itself a parent whose sub we also cover
        # (e.g. T1059 + T1059.001), expand it too.
        if technique_id in parents_to_expand:
            entry["showSubtechniques"] = True
        techniques.append(entry)

    # Add expand-only entries for parents we DON'T cover directly, so their
    # covered sub-techniques become visible (uncolored parent, expanded).
    covered_ids = {t["techniqueID"] for t in techniques}
    for parent in sorted(parents_to_expand - covered_ids):
        techniques.append({
            "techniqueID": parent,
            "enabled": True,
            "showSubtechniques": True,
        })

    return {
        "name": "Detection-as-Code - Coverage",
        "versions": {"attack": "19", "navigator": "5.1.0", "layer": "4.5"},
        "domain": "enterprise-attack",
        "description": (
            "Techniques covered by the Sigma rules in this repository. "
            "Auto-generated from rule ATT&CK tags by scripts/gen_navigator_layer.py."
        ),
        "techniques": techniques,
        "gradient": {
            "colors": ["#ffffff", COVERED_COLOR],
            "minValue": 0,
            "maxValue": max((t.get("score", 0) for t in techniques), default=1),
        },
        "legendItems": [{"label": "Covered by >= 1 rule", "color": COVERED_COLOR}],
        "showTacticRowBackground": True,
        "tacticRowBackground": "#205b8f",
        "selectTechniquesAcrossTactics": True,
        "sorting": 0,
    }


def main():
    docs = load_rule_documents()
    coverage = build_coverage(docs)
    layer = build_layer(coverage)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_FILE.open("w", encoding="utf-8") as fh:
        json.dump(layer, fh, indent=2)

    # Human-readable summary so you can eyeball what got generated.
    print(f"Wrote {OUTPUT_FILE.relative_to(REPO_ROOT).as_posix()}")
    print(f"Techniques covered: {len(coverage)}\n")
    for technique_id in sorted(coverage):
        titles = "; ".join(sorted(coverage[technique_id]))
        print(f"  {technique_id:12} {titles}")


if __name__ == "__main__":
    main()
