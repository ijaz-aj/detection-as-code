"""
Validate every Sigma rule against docs/detection-standard.md.

Run locally:   pytest -v
In CI:         runs automatically on every push (.github/workflows/validate.yml).

HOW IT WORKS
------------
Every YAML *document* under detections/ becomes its own parametrized test case.
That matters because some files are multi-document (the brute-force rule is a
base rule + a correlation block in one file, separated by `---`). Parametrizing
per-document means a failure names the exact rule AND the exact field that broke,
e.g.  test_status_valid[credential-access/failed-logon-bruteforce/...yml[doc1]].

We check two things Sigma's own linter does NOT: our project-specific *metadata
standard* (required fields, enums, ATT&CK tag pairing). Sigma validity itself is
checked separately by `sigma check` in the CI workflow.
"""
from __future__ import annotations

import datetime
import re
import uuid
from pathlib import Path

import pytest
import yaml

# --- Where the rules live ---------------------------------------------------
# tests/ sits at the repo root, so the repo root is this file's grandparent.
REPO_ROOT = Path(__file__).resolve().parents[1]
DETECTIONS_DIR = REPO_ROOT / "detections"

# --- Allowed values, taken straight from docs/detection-standard.md ----------
VALID_STATUS = {"experimental", "test", "stable"}
VALID_LEVEL = {"informational", "low", "medium", "high", "critical"}

# Metadata every rule document must carry (standard rules AND correlation rules).
REQUIRED_METADATA = [
    "title", "id", "status", "description", "references",
    "author", "date", "tags", "falsepositives", "level",
]

# A technique tag looks like  attack.t1003  or  attack.t1003.001
TECHNIQUE_TAG = re.compile(r"^attack\.t\d{4}(\.\d{3})?$")
# Any ATT&CK tag starts with  attack.
ANY_ATTACK_TAG = re.compile(r"^attack\.")

# Placeholders that must never appear in falsepositives.
FP_PLACEHOLDERS = {"none", "n/a", "na", "unknown", ""}


def _load_rule_documents():
    """Yield one pytest param per YAML document found under detections/."""
    params = []
    for path in sorted(DETECTIONS_DIR.rglob("*.yml")):
        with path.open(encoding="utf-8") as fh:
            for index, doc in enumerate(yaml.safe_load_all(fh)):
                if not doc:  # skip empty documents
                    continue
                rel = path.relative_to(REPO_ROOT).as_posix()
                params.append(pytest.param(doc, id=f"{rel}[doc{index}]"))
    return params


RULE_DOCS = _load_rule_documents()


def test_rules_were_discovered():
    """Guardrail: if the glob finds nothing, every other test would pass vacuously."""
    assert RULE_DOCS, f"No rule .yml files found under {DETECTIONS_DIR}"


@pytest.mark.parametrize("doc", RULE_DOCS)
def test_required_metadata_present(doc):
    """Standard §2: every rule must include all required top-level fields, non-empty."""
    missing = [f for f in REQUIRED_METADATA if not doc.get(f)]
    assert not missing, f"missing or empty required field(s): {missing}"


@pytest.mark.parametrize("doc", RULE_DOCS)
def test_id_is_uuid(doc):
    """Standard §2: `id` must be a globally unique UUID."""
    uuid.UUID(str(doc["id"]))  # raises ValueError if malformed


@pytest.mark.parametrize("doc", RULE_DOCS)
def test_status_valid(doc):
    assert doc["status"] in VALID_STATUS, f"status '{doc['status']}' not one of {sorted(VALID_STATUS)}"


@pytest.mark.parametrize("doc", RULE_DOCS)
def test_level_valid(doc):
    assert doc["level"] in VALID_LEVEL, f"level '{doc['level']}' not one of {sorted(VALID_LEVEL)}"


@pytest.mark.parametrize("doc", RULE_DOCS)
def test_references_is_nonempty_list(doc):
    refs = doc["references"]
    assert isinstance(refs, list) and len(refs) >= 1, "references must be a list with at least one URL"


@pytest.mark.parametrize("doc", RULE_DOCS)
def test_date_is_iso(doc):
    """Standard §2: date is ISO YYYY-MM-DD. PyYAML auto-parses unquoted ISO dates to date objects."""
    value = doc["date"]
    if isinstance(value, datetime.date):
        return  # already a valid date (datetime.datetime is a subclass, also fine)
    datetime.datetime.strptime(str(value), "%Y-%m-%d")  # raises ValueError on bad format


@pytest.mark.parametrize("doc", RULE_DOCS)
def test_tags_pair_technique_and_tactic(doc):
    """Standard §3: tags must include an ATT&CK technique AND a tactic tag."""
    tags = doc["tags"]
    assert isinstance(tags, list) and tags, "tags must be a non-empty list"
    techniques = [t for t in tags if TECHNIQUE_TAG.match(str(t))]
    tactics = [t for t in tags if ANY_ATTACK_TAG.match(str(t)) and not TECHNIQUE_TAG.match(str(t))]
    assert techniques, f"no ATT&CK technique tag (e.g. attack.t1003.001) in {tags}"
    assert tactics, f"no ATT&CK tactic tag (e.g. attack.credential_access) in {tags}"


@pytest.mark.parametrize("doc", RULE_DOCS)
def test_detection_logic_present(doc):
    """Standard §2: a rule needs real logic. Two valid shapes: detection or correlation."""
    if "correlation" in doc:
        corr = doc["correlation"]
        assert "type" in corr, "correlation block needs a `type`"
        assert "condition" in corr, "correlation block needs a `condition`"
    else:
        assert doc.get("logsource"), "missing `logsource`"
        assert doc.get("detection"), "missing `detection`"
        assert "condition" in doc["detection"], "`detection` must include a `condition`"


@pytest.mark.parametrize("doc", RULE_DOCS)
def test_falsepositives_are_concrete(doc):
    """Standard §3: falsepositives must be real, never 'None' — this is a graded part of every rule."""
    fps = doc["falsepositives"]
    if isinstance(fps, str):
        fps = [fps]
    assert fps, "falsepositives must not be empty"
    bad = [x for x in fps if str(x).strip().lower() in FP_PLACEHOLDERS]
    assert not bad, f"falsepositives must be concrete, not placeholder(s): {bad}"
