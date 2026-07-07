import os
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

class PromptMiddleware(ABC):
    @abstractmethod
    async def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Processes the context pipeline (adding loader data, transforming variables, validating content)."""
        pass


class WorkspaceLoaderStage(PromptMiddleware):
    def __init__(self, file_path: str, max_chars: int = 5000):
        self.file_path = file_path
        self.max_chars = max_chars

    async def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        if not os.path.exists(self.file_path):
            content = f"[File not found: {self.file_path}]"
        else:
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    content = f.read(self.max_chars)
                    if len(content) >= self.max_chars:
                        content += "\n... [Content truncated] ..."
            except Exception as e:
                content = f"[Error reading file: {str(e)}]"
        
        if "workspace_files" not in context:
            context["workspace_files"] = {}
        file_name = os.path.basename(self.file_path)
        context["workspace_files"][file_name] = content
        
        flat_key = f"file_{file_name.replace('.', '_').replace('-', '_')}"
        context[flat_key] = content
        return context


class MemoryLoaderStage(PromptMiddleware):
    def __init__(self, lessons: List[str]):
        self.lessons = lessons

    async def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        context["memory_context"] = "\n".join([f"- {lesson}" for lesson in self.lessons])
        return context


class ArtifactLoaderStage(PromptMiddleware):
    def __init__(self, name: str, content: str):
        self.name = name
        self.content = content

    async def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        if "artifacts" not in context:
            context["artifacts"] = {}
        context["artifacts"][self.name] = self.content
        
        flat_key = f"artifact_{self.name.replace('.', '_').replace('-', '_')}"
        context[flat_key] = self.content
        return context


class GitLoaderStage(PromptMiddleware):
    def __init__(self, diff_content: str):
        self.diff_content = diff_content

    async def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        context["git_diff"] = self.diff_content
        return context


class PromptPipeline:
    """
    A Middleware-based Prompt Pipeline that sequentially runs loader, transformer, 
    validator, and renderer stages (Challenge #17 & Priority 2).
    """
    def __init__(self, template: str):
        self.template = template
        self.stages: List[PromptMiddleware] = []

    def add_stage(self, stage: PromptMiddleware) -> "PromptPipeline":
        """Injects a middleware stage into the pipeline."""
        self.stages.append(stage)
        return self

    async def execute_pipeline(self, initial_vars: Optional[Dict[str, Any]] = None) -> str:
        """
        Executes all registered middleware stages in order, then compiles the final prompt.
        """
        context = dict(initial_vars or {})
        
        # Run stages chain (Loader -> Transformer -> Validator -> Renderer)
        for stage in self.stages:
            context = await stage.process(context)
            
        defaults = {
            "memory_context": "No lessons learned recorded.",
            "git_diff": "No local git changes."
        }
        for k, v in defaults.items():
            if k not in context:
                context[k] = v

        try:
            return self.template.format(**context)
        except KeyError as e:
            raise KeyError(f"Missing required context key {str(e)} in prompt pipeline execution.")
