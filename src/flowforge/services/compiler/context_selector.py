import os
from typing import Dict, Any, List

class ContextSelector:
    @staticmethod
    def select_relevant_context(
        keywords: List[str], 
        project_context: Dict[str, Any], 
        workspace_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Filters project files and git context to keep only items matching the keywords list.
        Minimizes context package size by discarding irrelevant details.
        """
        relevant_context = {}
        
        # 1. Filter inline dictionary project context keys
        for key, value in project_context.items():
            key_lower = key.lower()
            # If any keyword matches the key or if keywords list is empty (include all)
            if not keywords or any(kw.lower() in key_lower for kw in keywords):
                relevant_context[key] = value
                
        # 2. Optionally scan workspace directory files for match
        if workspace_path and os.path.exists(workspace_path):
            files_context = {}
            for root, _, files in os.walk(workspace_path):
                # Skip build/cache directories
                if any(ignored in root for ignored in [".git", ".venv", "__pycache__", "node_modules", "dist", "build"]):
                    continue
                for file_name in files:
                    # Only look for text source files
                    if file_name.endswith((".py", ".md", ".yaml", ".ff.yaml", ".json", ".txt")):
                        file_path = os.path.join(root, file_name)
                        try:
                            with open(file_path, "r", encoding="utf-8") as f:
                                content = f.read()
                            # If file content relates to mission keywords
                            if any(kw.lower() in content.lower() or kw.lower() in file_name.lower() for kw in keywords):
                                rel_path = os.path.relpath(file_path, workspace_path)
                                files_context[rel_path] = content[:2000] # Limit size per file
                        except Exception:
                            pass
            if files_context:
                relevant_context["workspace_files"] = files_context

        return relevant_context
