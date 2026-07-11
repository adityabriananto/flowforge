import os
from typing import Dict, Any, List, Optional

class ContextSelector:
    @staticmethod
    def select_relevant_context(
        keywords: List[str], 
        project_context: Dict[str, Any], 
        workspace_path: Optional[str] = None,
        base_path: str = "."
    ) -> Dict[str, Any]:
        """
        Filters project files and git context to keep only items matching the keywords list.
        Minimizes context package size by discarding irrelevant details.
        """
        import yaml
        relevant_context = {}
        
        # Load local engineering state and workspace info if available
        engineering_dir = os.path.join(base_path, "engineering")
        if os.path.exists(engineering_dir):
            workspace_yaml = os.path.join(engineering_dir, "WORKSPACE.yaml")
            if os.path.exists(workspace_yaml):
                try:
                    with open(workspace_yaml, "r", encoding="utf-8") as f:
                        ws_data = yaml.safe_load(f)
                    if isinstance(ws_data, dict):
                        relevant_context["framework"] = ws_data.get("framework")
                        relevant_context["language"] = ws_data.get("language")
                        relevant_context["project_type"] = ws_data.get("workspace_type")
                except Exception:
                    pass
            
            state_yaml = os.path.join(engineering_dir, "PROJECT_STATE.yaml")
            if os.path.exists(state_yaml):
                try:
                    with open(state_yaml, "r", encoding="utf-8") as f:
                        state_data = yaml.safe_load(f)
                    if isinstance(state_data, dict):
                        proj_meta = state_data.get("project")
                        if isinstance(proj_meta, dict):
                            relevant_context["current_phase"] = proj_meta.get("current_phase")
                            relevant_context["repository_name"] = proj_meta.get("name")
                except Exception:
                    pass
        
        # Filter inline dictionary project context keys
        for key, value in project_context.items():
            key_lower = key.lower()
            if not keywords or any(kw.lower() in key_lower for kw in keywords):
                relevant_context[key] = value
                
        # Optionally scan workspace directory files for match
        if workspace_path and os.path.exists(workspace_path):
            files_context = {}
            for root, _, files in os.walk(workspace_path):
                if any(ignored in root for ignored in [".git", ".venv", "__pycache__", "node_modules", "dist", "build"]):
                    continue
                for file_name in files:
                    if file_name.endswith((".py", ".md", ".yaml", ".ff.yaml", ".json", ".txt")):
                        file_path = os.path.join(root, file_name)
                        try:
                            with open(file_path, "r", encoding="utf-8") as f:
                                content = f.read()
                            if any(kw.lower() in content.lower() or kw.lower() in file_name.lower() for kw in keywords):
                                rel_path = os.path.relpath(file_path, workspace_path)
                                files_context[rel_path] = content[:2000] # Limit size per file
                        except Exception:
                            pass
            if files_context:
                relevant_context["workspace_files"] = files_context

        return relevant_context
