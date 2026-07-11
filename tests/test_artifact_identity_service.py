import pytest
from flowforge.services.artifact_identity_service import ArtifactIdentityService

def test_scenario_1_empty_repo():
    # Scenario 1: Repository empty -> Expected: PROJECT-000
    ident = ArtifactIdentityService.generate_next_identity("PROJECT", [])
    assert ident == "PROJECT-000"

def test_scenario_2_existing_1():
    # Scenario 2: Existing: PROJECT-000 -> Expected: PROJECT-001
    ident = ArtifactIdentityService.generate_next_identity("PROJECT", ["PROJECT-000"])
    assert ident == "PROJECT-001"

def test_scenario_3_existing_3():
    # Scenario 3: Existing: PROJECT-000, PROJECT-001, PROJECT-002 -> Expected: PROJECT-003
    ident = ArtifactIdentityService.generate_next_identity("PROJECT", ["PROJECT-000", "PROJECT-001", "PROJECT-002"])
    assert ident == "PROJECT-003"

def test_scenario_4_mission_moved():
    # Scenario 4: Mission moved: Active -> Completed
    # The ArtifactIdentityService only sees identifiers, not folders, but logically it's equivalent.
    ident = ArtifactIdentityService.generate_next_identity("PROJECT", ["PROJECT-000", "PROJECT-001"])
    assert ident == "PROJECT-002"

def test_scenario_5_mixed_folders():
    # Scenario 5: Mixed folders: backlog, active, completed -> Expected: highest sequence + 1
    # Tested by providing existing identifiers in random order
    ident = ArtifactIdentityService.generate_next_identity("PROJECT", ["PROJECT-002", "PROJECT-000", "PROJECT-001"])
    assert ident == "PROJECT-003"

def test_scenario_6_gap():
    # Scenario 6: Gap: PROJECT-000, PROJECT-005 -> Expected: PROJECT-006
    ident = ArtifactIdentityService.generate_next_identity("PROJECT", ["PROJECT-000", "PROJECT-005"])
    assert ident == "PROJECT-006"

def test_scenario_7_mixed_prefixes():
    # Scenario 7: Mixed prefixes: PROJECT-001, PROJECT-002, RFC-001, ADR-001
    existing = ["PROJECT-001", "PROJECT-002", "RFC-001", "ADR-001"]
    
    # Generating PROJECT -> PROJECT-003
    ident_proj = ArtifactIdentityService.generate_next_identity("PROJECT", existing)
    assert ident_proj == "PROJECT-003"
    
    # Generating RFC -> RFC-002
    ident_rfc = ArtifactIdentityService.generate_next_identity("RFC", existing)
    assert ident_rfc == "RFC-002"

def test_invalid_formats_ignored():
    # Additional safety test
    existing = ["PROJECT-ABC", "PROJECT-", "PROJECT-001A", "OTHER-002", "PROJECT-001"]
    ident = ArtifactIdentityService.generate_next_identity("PROJECT", existing)
    assert ident == "PROJECT-002"
