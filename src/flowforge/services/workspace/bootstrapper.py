import os
import yaml
from typing import Dict, Any, Optional
from flowforge.services.workspace.detector import ProjectDetectorService
from flowforge.services.workspace.engineering_workspace import EngineeringWorkspace
from flowforge.services.workspace.mission_lifecycle_manager import MissionLifecycleManager

class SmartBootstrapper:
    """
    Orchestrates the onboarding experience by automatically detecting project configuration,
    initializing folders, setting up metadata files, and creating the first backlog mission.
    """

    @staticmethod
    def is_git_repository(base_path: str) -> bool:
        return os.path.exists(os.path.join(base_path, ".git"))

    @classmethod
    def bootstrap(
        cls, 
        base_path: str = ".", 
        force: bool = False, 
        prefix: str = "PROJECT"
    ) -> Dict[str, Any]:
        """
        Initializes an engineering project environment dynamically.
        Idempotent: will not overwrite existing assets.
        """
        # 1. Validation: Prevent outside Git repositories unless force is True
        if not cls.is_git_repository(base_path) and not force:
            raise RuntimeError(
                "Error: Not running inside a Git repository. "
                "Use --force flag if you wish to bypass this safety check."
            )

        # 2. Detect Project Properties
        detector = ProjectDetectorService()
        project_details = detector.detect_project(base_path)

        # 3. Create Engineering Workspace Folders
        EngineeringWorkspace.initialize_workspace(base_path)

        # 4. Generate/Install Templates (only if missing)
        cls._install_default_templates(base_path)

        # 5. Generate engineering/WORKSPACE.yaml (idempotent)
        workspace_yaml = os.path.join(base_path, "engineering", "WORKSPACE.yaml")
        if not os.path.exists(workspace_yaml):
            workspace_data = {
                "workspace_type": project_details["project_type"],
                "language": project_details["language"],
                "framework": project_details["framework"],
                "package_manager": project_details["package_manager"],
                "build_tool": project_details["build_tool"]
            }
            with open(workspace_yaml, "w", encoding="utf-8") as f:
                yaml.dump(workspace_data, f, sort_keys=False, default_flow_style=False)

        # 6. Generate engineering/PROJECT_STATE.yaml (idempotent)
        project_state_yaml = os.path.join(base_path, "engineering", "PROJECT_STATE.yaml")
        if not os.path.exists(project_state_yaml):
            project_state_data = {
                "active_missions": [],
                "completed_missions": []
            }
            with open(project_state_yaml, "w", encoding="utf-8") as f:
                yaml.dump(project_state_data, f, sort_keys=False, default_flow_style=False)

        # 7. Generate Initial Mission: PROJECT-000 Repository Discovery (idempotent)
        mission_id = f"{prefix}-000"
        m_state, _ = MissionLifecycleManager._find_mission_file(mission_id, base_path)
        if not m_state:
            MissionLifecycleManager.create_mission(
                title="Repository Discovery",
                description="Scan project directory structure, dependencies, and requirements to index base knowledge.",
                mission_id=mission_id,
                base_path=base_path
            )

        return project_details

    @classmethod
    def _install_default_templates(cls, base_path: str) -> None:
        """Installs fallback template strings if they do not exist."""
        templates_dir = os.path.join(base_path, "engineering", "missions", "templates")
        os.makedirs(templates_dir, exist_ok=True)
        
        # We can dynamically fallback write templates if they are missing
        # 1. mission.yaml
        m_yaml = os.path.join(templates_dir, "mission.yaml")
        if not os.path.exists(m_yaml):
            content = """# FlowForge Mission Template (v1.0.0)
version: "1"
id: "FF-000"
title: "Mission Title"
description: "High-level goal description of what needs to be solved."
status: "BACKLOG"
priority: "medium"
owner: "owner-role"
reviewer: "reviewer-role"
phase: "development"
goal: "Define the specific technical objective"
deliverables:
  - "Deliverable item 1"
constraints:
  - "Constraint item 1"
definition_of_done:
  - "Unit tests pass with > 80% coverage"
references:
  - "rfc-000"
"""
            with open(m_yaml, "w", encoding="utf-8") as f:
                f.write(content)

        # 2. rfc.md
        rfc = os.path.join(templates_dir, "rfc.md")
        if not os.path.exists(rfc):
            content = """# RFC-000: Title of the Proposal (v1.0.0)

## 1. Abstract
A short abstract.

## 2. Specification
Details of the specification.
"""
            with open(rfc, "w", encoding="utf-8") as f:
                f.write(content)

        # 3. adr.md
        adr = os.path.join(templates_dir, "adr.md")
        if not os.path.exists(adr):
            content = """# ADR-000: Title (v1.0.0)

## Status
Proposed

## Context
Engineering challenge description.

## Decision
Actionable choice.
"""
            with open(adr, "w", encoding="utf-8") as f:
                f.write(content)

        # 4. sprint.md
        sprint = os.path.join(templates_dir, "sprint.md")
        if not os.path.exists(sprint):
            content = """# Sprint Plan & Roadmap (v1.0.0)
## Objective
Sprint objective.
"""
            with open(sprint, "w", encoding="utf-8") as f:
                f.write(content)

        # 5. review.md
        review = os.path.join(templates_dir, "review.md")
        if not os.path.exists(review):
            content = """# Sprint Review & Audit (v1.0.0)
## Retrospective
Summary of results.
"""
            with open(review, "w", encoding="utf-8") as f:
                f.write(content)
