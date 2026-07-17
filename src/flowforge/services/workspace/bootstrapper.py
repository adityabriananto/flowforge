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
        # 1. Validation: Check Git repository status
        if not cls.is_git_repository(base_path):
            print("[INFO] Git repository not found.\n       Continuing without Git integration.")


        # 2. Detect Project Properties
        detector = ProjectDetectorService()
        project_details = detector.detect_project(base_path)

        # 3. Create Engineering Workspace Folders
        EngineeringWorkspace.initialize_workspace(base_path)

        # 4. Generate/Install Templates (only if missing)
        cls._install_default_templates(base_path)

        # 5. Generate engineering/WORKSPACE.yaml
        workspace_yaml = os.path.join(base_path, "engineering", "WORKSPACE.yaml")
        if force or not os.path.exists(workspace_yaml):
            workspace_data = {
                "workspace_type": project_details["project_type"],
                "language": project_details["language"],
                "framework": project_details["framework"],
                "package_manager": project_details["package_manager"],
                "build_tool": project_details["build_tool"]
            }
            with open(workspace_yaml, "w", encoding="utf-8") as f:
                yaml.dump(workspace_data, f, sort_keys=False, default_flow_style=False)

        # 6. Generate engineering/PROJECT_STATE.yaml
        import uuid
        from datetime import datetime
        project_state_yaml = os.path.join(base_path, "engineering", "PROJECT_STATE.yaml")
        if force or not os.path.exists(project_state_yaml):
            repo_name = os.path.basename(os.path.abspath(base_path)) or "unknown-project"
            project_state_data = {
                "version": "1",
                "project": {
                    "id": str(uuid.uuid4()),
                    "name": repo_name,
                    "framework": project_details.get("framework") or "Unknown",
                    "language": project_details.get("language") or "Unknown",
                    "project_type": project_details.get("project_type") or "Generic",
                    "workspace_version": "1.0.0",
                    "current_phase": "discovery",
                    "created_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
                },
                "active_missions": [],
                "completed_missions": []
            }
            with open(project_state_yaml, "w", encoding="utf-8") as f:
                yaml.dump(project_state_data, f, sort_keys=False, default_flow_style=False)

        # 7. Generate Initial Mission: PROJECT-000 Repository Discovery (idempotent)
        from flowforge.services.workspace.templates import render_mission_data
        mission_id = f"{prefix}-000"
        m_state, _ = MissionLifecycleManager._find_mission_file(mission_id, base_path)
        if not m_state:
            m_data = render_mission_data(
                mission_type="Repository Discovery",
                project_details=project_details,
                custom_desc=f"Scan the {project_details.get('framework', 'project')} directory structure, dependencies, and requirements to index base knowledge."
            )
            MissionLifecycleManager.create_mission(
                title=m_data["title"],
                description=m_data["description"],
                mission_id=mission_id,
                base_path=base_path,
                goal=m_data["goal"],
                deliverables=m_data["deliverables"],
                definition_of_done=m_data["definition_of_done"],
                constraints=m_data["constraints"]
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

        # 3. implementation_report.md
        report = os.path.join(templates_dir, "implementation_report.md")
        if not os.path.exists(report):
            content = """# Engineering Implementation Report

## Executive Summary
[Provide a summary of the implementation.]

## Scope
[Describe the approved scope.]

## Files Created
[List new files.]

## Files Modified
[List modified files.]

## Technical Changes
[Explain the technical modifications made.]

## Validation Performed
[Describe how the implementation was tested.]

## Backward Compatibility
[Note any impacts to backward compatibility.]

## Known Limitations
[List any known limitations.]

## Completion Status
[State whether the mission is completed.]
"""
            with open(report, "w", encoding="utf-8") as f:
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
