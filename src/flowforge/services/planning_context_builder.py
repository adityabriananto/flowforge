import os
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from flowforge.services.workspace.mission_lifecycle_manager import MissionLifecycleManager

@dataclass
class PlanningContext:
    project_name: str = "Unknown"
    framework: str = "Unknown"
    language: str = "Unknown"
    project_type: str = "Unknown"
    current_phase: str = "Unknown"
    existing_missions: int = 0
    recent_adrs: List[str] = field(default_factory=list)
    recent_rfcs: List[str] = field(default_factory=list)
    completed_missions: List[str] = field(default_factory=list)

class PlanningContextBuilder:
    """
    Collects Engineering Workspace knowledge to normalize engineering metadata.
    Does not scan repository source code, relies entirely on structured workspace data.
    """
    
    def __init__(self, base_path: str = "."):
        self.base_path = base_path

    def build_context(self) -> PlanningContext:
        import json
        try:
            import tomllib as toml
        except ImportError:
            try:
                import tomli as toml
            except ImportError:
                toml = None
        import yaml
        
        context = PlanningContext()
        state_data = {}
        ws_data = {}
        
        workspace_path = os.path.join(self.base_path, "engineering", "WORKSPACE.yaml")
        try:
            if os.path.exists(workspace_path):
                with open(workspace_path, "r", encoding="utf-8") as f:
                    ws_data = yaml.safe_load(f) or {}
                
                context.project_name = ws_data.get("project_name") or "Unknown"
                context.framework = ws_data.get("framework") or "Unknown"
                context.language = ws_data.get("language") or "Unknown"
                context.project_type = ws_data.get("project_type") or "Unknown"
        except Exception:
            pass

        project_state_path = os.path.join(self.base_path, "engineering", "PROJECT_STATE.yaml")
        try:
            if os.path.exists(project_state_path):
                with open(project_state_path, "r", encoding="utf-8") as f:
                    state_data = yaml.safe_load(f) or {}
                    
                if state_data.get("project_name"):
                    context.project_name = state_data["project_name"]
                    
                context.current_phase = state_data.get("current_phase") or "Unknown"
                
                completed = state_data.get("completed_missions", [])
                context.completed_missions = [m for m in completed if isinstance(m, str)]
                context.existing_missions = len(context.completed_missions) + len(state_data.get("active_missions", []))
        except Exception:
            pass

        # 1. Resolve Project Name
        if context.project_name == "Unknown":
            # Try git remote
            import subprocess
            try:
                out = subprocess.check_output(["git", "config", "--get", "remote.origin.url"], cwd=self.base_path, stderr=subprocess.DEVNULL)
                url = out.decode("utf-8").strip()
                if url:
                    basename = url.split("/")[-1]
                    if basename.endswith(".git"):
                        basename = basename[:-4]
                    if basename:
                        context.project_name = basename
            except Exception:
                pass
                
        if context.project_name == "Unknown":
            # Project directory name
            dirname = os.path.basename(os.path.abspath(self.base_path))
            if dirname:
                context.project_name = dirname
                
        if context.project_name == "Unknown":
            # Fallback to repo metadata
            try:
                pkg_json_path = os.path.join(self.base_path, "package.json")
                if os.path.exists(pkg_json_path):
                    with open(pkg_json_path, "r", encoding="utf-8") as f:
                        pkg = json.load(f)
                        if pkg.get("name"): context.project_name = pkg["name"]
            except Exception: pass
            
            if context.project_name == "Unknown":
                try:
                    composer_path = os.path.join(self.base_path, "composer.json")
                    if os.path.exists(composer_path):
                        with open(composer_path, "r", encoding="utf-8") as f:
                            comp = json.load(f)
                            if comp.get("name"): context.project_name = comp["name"]
                except Exception: pass
                
            if context.project_name == "Unknown":
                try:
                    pyproj_path = os.path.join(self.base_path, "pyproject.toml")
                    if os.path.exists(pyproj_path) and toml is not None:
                        with open(pyproj_path, "rb") as f:
                            pyproj = toml.load(f)
                            if pyproj.get("project", {}).get("name"): 
                                context.project_name = pyproj["project"]["name"]
                            elif pyproj.get("tool", {}).get("poetry", {}).get("name"):
                                context.project_name = pyproj["tool"]["poetry"]["name"]
                except Exception: pass

        # 2. Resolve Project Type
        fw_map = {
            "laravel": "Web Application",
            "django": "Web Application",
            "spring boot": "Backend Service",
            "fastapi": "Backend Service",
            "react": "Frontend Application",
            "vue": "Frontend Application",
            "console": "CLI Application"
        }
        if context.framework != "Unknown":
            fw_lower = context.framework.lower()
            for key, val in fw_map.items():
                if key in fw_lower:
                    context.project_type = val
                    break

        # 3. Resolve Current Phase
        if context.current_phase == "Unknown":
            if not context.completed_missions:
                context.current_phase = "Project Initialization"
            else:
                latest_mission_id = context.completed_missions[-1]
                latest_mission_path = os.path.join(self.base_path, "engineering", "missions", "completed", f"{latest_mission_id}.yaml")
                latest_title = ""
                try:
                    if os.path.exists(latest_mission_path):
                        with open(latest_mission_path, "r", encoding="utf-8") as f:
                            m_data = yaml.safe_load(f)
                            if m_data and "title" in m_data:
                                latest_title = m_data["title"].lower()
                except Exception:
                    pass
                    
                if "discovery" in latest_title:
                    context.current_phase = "Project Definition"
                elif "definition" in latest_title:
                    context.current_phase = "Domain Modeling"
                elif "domain" in latest_title:
                    context.current_phase = "Business Workflow"
                elif "workflow" in latest_title:
                    context.current_phase = "Architecture Design"
                elif "architecture" in latest_title:
                    context.current_phase = "Implementation"
                else:
                    context.current_phase = "Implementation"

        # Find ADRs/RFCs (just the filenames as a hint)
        context.recent_adrs = self._list_templates("adr")
        context.recent_rfcs = self._list_templates("rfc")
        
        return context
        
    def _list_templates(self, doc_type: str) -> List[str]:
        # For simplicity, we just look at the templates folder or docs folder.
        # FlowForge keeps ADRs/RFCs typically inside docs/ or engineering/docs/
        # Currently, they might just be listed in templates or we can scan engineering/docs
        docs_path = os.path.join(self.base_path, "engineering", "docs", doc_type)
        if not os.path.exists(docs_path):
            return []
            
        docs = []
        try:
            for file_name in os.listdir(docs_path):
                if file_name.endswith(".md"):
                    docs.append(file_name.replace(".md", ""))
        except Exception:
            pass
        return docs
