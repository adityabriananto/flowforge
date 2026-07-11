import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from flowforge.services.compiler.compiler import MissionPackageCompiler
from flowforge.services.workspace.state_service import EngineeringStateService
from flowforge.services.workspace.session_service import EngineeringSessionService
from flowforge.services.runtime.provider_registry import AIRuntimeProviderRegistry
from flowforge.domain.mission_package import MissionPackage
from flowforge.domain.engineering_state import EngineeringState
from flowforge.domain.engineering_session import EngineeringSession, SessionStatus

class AIRuntimeEngine:
    def __init__(
        self,
        compiler: MissionPackageCompiler,
        state_service: EngineeringStateService,
        session_service: EngineeringSessionService,
        provider_registry: AIRuntimeProviderRegistry
    ):
        self.compiler = compiler
        self.state_service = state_service
        self.session_service = session_service
        self.provider_registry = provider_registry

    def execute_mission(self, mission_code: str, base_path: str = ".", provider_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Coordinates the complete end-to-end engineering execution workflow.
        Compiles the mission, initializes a session, selects the AI provider,
        executes tasks, updates project state, and saves outcomes.
        """
        import os
        from flowforge.services.workspace.mission_lifecycle_manager import MissionLifecycleManager
        from flowforge.services.mission_loader import MissionLoader

        # 1. Resolve mission file path
        _, resolved_path = MissionLifecycleManager._find_mission_file(mission_code, base_path=base_path)
        if not resolved_path:
            raise RuntimeError(f"Mission '{mission_code}' not found in backlog, active, or completed directories.")

        try:
            mission = MissionLoader.load_from_file(resolved_path)
        except Exception as e:
            raise RuntimeError(f"Runtime failed to load mission file '{resolved_path}': {str(e)}")

        # Configure compiler paths relative to base_path
        self.compiler.rules_file_path = os.path.join(base_path, "engineering/decisions/AGENTS.md")
        self.compiler.references_dir = os.path.join(base_path, "engineering/architecture")

        # Compile the mission package
        try:
            mission_package = self.compiler.compile(mission=mission)
        except Exception as e:
            raise RuntimeError(f"Runtime failed to compile mission package for '{mission_code}': {str(e)}")

        # 2. Select active provider
        if provider_name:
            provider = self.provider_registry.get(provider_name)
        else:
            provider = self.provider_registry.default()

        # 3. Load active engineering state
        try:
            state = self.state_service.load_state(base_path)
        except Exception:
            # Fallback if state doesn't exist yet (Zero-config init fallback)
            from flowforge.domain.engineering_state import EngineeringState, ProjectState
            state = EngineeringState(project=ProjectState(id=str(uuid.uuid4()), name=mission_package.mission.title))
            self.state_service.save_state(state, base_path)

        # 4. Create and start engineering session
        session_id = str(uuid.uuid4())
        session = self.session_service.create_session(
            provider=provider.name(),
            mission=mission_code,
            session_id=session_id,
            base_path=base_path
        )
        self.session_service.start_session(session_id, base_path=base_path)

        # Update current mission in engineering state
        self.state_service.update_current_mission(mission_code, base_path=base_path)

        # 5. Execute AI provider
        start_time = datetime.utcnow()
        try:
            # Delegate raw execution to provider
            exec_res = provider.execute(mission_package, state)
            status = exec_res.get("status", "SUCCESS")
        except Exception as e:
            # Handle failure transitions
            self.session_service.fail_session(session_id, base_path=base_path)
            raise RuntimeError(f"AI Provider execution failed for '{provider.name()}': {str(e)}")

        finish_time = datetime.utcnow()
        duration = (finish_time - start_time).total_seconds()

        # 6. Add results to session
        if status == "SUCCESS":
            # Add artifacts
            for art in exec_res.get("artifacts", []):
                self.session_service.add_artifact(session_id, art, base_path=base_path)
            # Add decisions
            for dec in exec_res.get("decisions", []):
                self.session_service.add_decision(
                    session_id=session_id,
                    title=dec.get("title", "Untitled Decision"),
                    rationale=dec.get("rationale", ""),
                    artifact_reference=dec.get("artifact_reference"),
                    base_path=base_path
                )
            # Add blockers
            for blk in exec_res.get("blockers", []):
                self.session_service.add_blocker(session_id, blk, base_path=base_path)
            # Add recommendations
            for rec in exec_res.get("recommendations", []):
                self.session_service.add_recommendation(session_id, rec, base_path=base_path)
            # Add files changed
            session_loaded = self.session_service.load_session(session_id, base_path=base_path)
            session_loaded.files_changed = list(exec_res.get("files_changed", []))
            self.session_service.save_session(session_loaded, base_path=base_path)

            # 7. Complete Session & update state references (blockers, completed status, etc.)
            self.session_service.complete_session(
                session_id=session_id,
                summary=exec_res.get("summary", "Mission successfully completed."),
                handover_summary=exec_res.get("handover_summary", "Handover to next mission."),
                base_path=base_path,
                state_service=self.state_service
            )
        else:
            self.session_service.fail_session(session_id, base_path=base_path)

        # 8. Return formatted execution outcome
        summary_str = self.session_service.export_session_summary(session_id, base_path=base_path)
        return {
            "session_id": session_id,
            "status": status,
            "duration_seconds": duration,
            "summary_report": summary_str
        }
