import os
import pytest
from flowforge.services.workspace.mission_lifecycle_manager import MissionLifecycleManager
from flowforge.services.workspace.engineering_workspace import EngineeringWorkspace

def test_mission_identity_generation(tmp_path):
    import shutil
    import os
    base = str(tmp_path)
    
    # Init workspace
    EngineeringWorkspace.initialize_workspace(base)
    
    # Copy template manually
    src_template = os.path.join(os.getcwd(), "engineering", "missions", "templates", "mission.yaml")
    dest_template_dir = os.path.join(base, "engineering", "missions", "templates")
    os.makedirs(dest_template_dir, exist_ok=True)
    shutil.copy(src_template, dest_template_dir)
    
    # 1. Create first mission -> should be PROJECT-001 or PROJECT-000?
    # Because ArtifactIdentityService gives max + 1. Empty is PROJECT-000.
    path1 = MissionLifecycleManager.create_mission(
        title="First",
        description="Desc",
        base_path=base
    )
    
    # 2. Complete the mission (move it)
    MissionLifecycleManager.start_mission("PROJECT-000", base_path=base)
    MissionLifecycleManager.complete_mission("PROJECT-000", base_path=base)
    
    # 3. Create second mission -> should be PROJECT-001
    path2 = MissionLifecycleManager.create_mission(
        title="Second",
        description="Desc",
        base_path=base
    )
    
    assert "PROJECT-000" in path1
    assert "PROJECT-001" in path2
