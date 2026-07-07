from typing import Dict, Any, List, Optional
import asyncio
from flowforge.services.prompt.prompt_pipeline import (
    PromptPipeline as ServicePromptPipeline,
    MemoryLoaderStage,
    ArtifactLoaderStage,
    WorkspaceLoaderStage,
    GitLoaderStage
)

class PromptPipeline:
    """Backward compatible wrapper that translates old builder calls into the new middleware pipeline (Challenge #17)."""
    def __init__(self, template: str):
        self.template = template
        self.service_pipeline = ServicePromptPipeline(template)
        self.initial_vars: Dict[str, Any] = {}

    def load_memory(self, lessons: List[str]) -> "PromptPipeline":
        self.service_pipeline.add_stage(MemoryLoaderStage(lessons))
        return self

    def load_artifact(self, name: str, content: str) -> "PromptPipeline":
        self.service_pipeline.add_stage(ArtifactLoaderStage(name, content))
        return self

    def load_workspace_file(self, file_path: str, max_chars: int = 5000) -> "PromptPipeline":
        self.service_pipeline.add_stage(WorkspaceLoaderStage(file_path, max_chars))
        return self

    def load_git_diff(self, diff_content: str) -> "PromptPipeline":
        self.service_pipeline.add_stage(GitLoaderStage(diff_content))
        return self

    def build(self, extra_vars: Optional[Dict[str, Any]] = None) -> str:
        """Synchronously executes the async middleware chain for compatibility with old test cases."""
        combined_vars = {**self.initial_vars, **(extra_vars or {})}
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
        try:
            import nest_asyncio
            nest_asyncio.apply()
        except ImportError:
            pass
            
        return loop.run_until_complete(self.service_pipeline.execute_pipeline(combined_vars))
