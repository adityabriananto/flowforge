import os
from typing import Dict, Any, List, Optional

class PromptPipeline:
    """
    A pipeline processing engine that dynamically aggregates context from multiple sources 
    (Memory, Artifacts, Workspace, Git) and injects it into a prompt template.
    """
    def __init__(self, template: str):
        self.template = template
        self.context: Dict[str, Any] = {}

    def load_memory(self, lessons: List[str]) -> "PromptPipeline":
        """Injects lessons learned/history from memory into context."""
        self.context["memory_context"] = "\n".join([f"- {lesson}" for lesson in lessons])
        return self

    def load_artifact(self, name: str, content: str) -> "PromptPipeline":
        """Injects an AI generated artifact into context."""
        if "artifacts" not in self.context:
            self.context["artifacts"] = {}
        self.context["artifacts"][name] = content
        
        # Flatten for easy template access (e.g. {artifact_architecture})
        flat_key = f"artifact_{name.replace('.', '_').replace('-', '_')}"
        self.context[flat_key] = content
        return self

    def load_workspace_file(self, file_path: str, max_chars: int = 5000) -> "PromptPipeline":
        """Injects a file from the workspace into context."""
        if not os.path.exists(file_path):
            content = f"[File not found: {file_path}]"
        else:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read(max_chars)
                    if len(content) >= max_chars:
                        content += "\n... [Content truncated] ..."
            except Exception as e:
                content = f"[Error reading file: {str(e)}]"
                
        if "workspace_files" not in self.context:
            self.context["workspace_files"] = {}
        file_name = os.path.basename(file_path)
        self.context["workspace_files"][file_name] = content
        
        # Flatten for easy template access (e.g. {file_login_py})
        flat_key = f"file_{file_name.replace('.', '_').replace('-', '_')}"
        self.context[flat_key] = content
        return self

    def load_git_diff(self, diff_content: str) -> "PromptPipeline":
        """Injects last git diff into context."""
        self.context["git_diff"] = diff_content
        return self

    def build(self, extra_vars: Optional[Dict[str, Any]] = None) -> str:
        """
        Processes and compiles the final formatted prompt.
        """
        combined = {**self.context, **(extra_vars or {})}
        
        # Ensure default keys exist in combined to prevent format KeyError
        defaults = {
            "memory_context": "No lessons learned recorded.",
            "git_diff": "No local git changes."
        }
        for k, v in defaults.items():
            if k not in combined:
                combined[k] = v

        try:
            return self.template.format(**combined)
        except KeyError as e:
            raise KeyError(f"Missing required context key {str(e)} in prompt pipeline build.")
