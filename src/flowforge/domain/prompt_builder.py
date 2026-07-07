import os
from typing import Dict, Any, List

class ContextLoader:
    """Helper class to load external workspace files or database context for prompts."""
    
    @staticmethod
    def load_file_content(file_path: str, max_chars: int = 10000) -> str:
        """Reads file contents from disk to inject into prompt context."""
        if not os.path.exists(file_path):
            return f"[File not found: {file_path}]"
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read(max_chars)
                if len(content) >= max_chars:
                    content += "\n... [Content truncated] ..."
                return content
        except Exception as e:
            return f"[Error loading file {file_path}: {str(e)}]"


class PromptBuilder:
    def __init__(self):
        self.templates: Dict[str, str] = {}
        # Pre-populate default prompts to avoid scattering
        self.templates["coding"] = (
            "Refactor the following Python code to fix: {bug_description}.\n"
            "Return ONLY the refined code. Do not include markdown wraps.\n\n"
            "Current Code:\n{current_code}"
        )
        self.templates["architecture"] = (
            "Design the system architecture based on requirements:\n{requirements}.\n"
            "Format the output as clean Markdown."
        )

    def add_template(self, name: str, template_string: str) -> None:
        """Adds a custom prompt template."""
        self.templates[name] = template_string

    def build_prompt(self, template_name: str, context: Dict[str, Any]) -> str:
        """
        Formats prompt template by replacing placeholding keys with context variables.
        """
        template = self.templates.get(template_name)
        if not template:
            raise ValueError(f"Prompt template '{template_name}' not registered in PromptBuilder.")
        
        # Safely format variables
        try:
            return template.format(**context)
        except KeyError as e:
            raise KeyError(f"Missing required context key {str(e)} for template '{template_name}'.")
