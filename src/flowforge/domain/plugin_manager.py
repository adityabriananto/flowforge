import logging
from typing import List
from flowforge.domain.base_plugin import FlowForgePlugin
from flowforge.domain.models import WorkflowInstance, Job, Event

logger = logging.getLogger("flowforge.plugin_manager")

class PluginManager:
    def __init__(self):
        self.plugins: List[FlowForgePlugin] = []

    def discover_and_register_plugins(self) -> None:
        """
        Auto-discovers and registers plugins via Python package entry points 'flowforge.plugins'.
        Allows developers to pip install plugins and have them auto-load.
        """
        import sys
        try:
            if sys.version_info >= (3, 10):
                from importlib.metadata import entry_points
                group = entry_points(group="flowforge.plugins")
            else:
                from importlib.metadata import entry_points
                eps = entry_points()
                group = eps.get("flowforge.plugins", [])

            for entry_point in group:
                try:
                    plugin_class = entry_point.load()
                    plugin_instance = plugin_class()
                    self.register_plugin(plugin_instance)
                except Exception as e:
                    logger.error(f"Failed to auto-discover plugin {entry_point.name}: {str(e)}")
        except Exception as e:
            logger.error(f"Error during plugin auto-discovery: {str(e)}")

    def discover_external_providers(self, registry) -> None:
        """
        Auto-discovers and registers external LLM providers/connectors 
        via Python entry points 'flowforge.providers' (Challenge #19).
        """
        import sys
        try:
            if sys.version_info >= (3, 10):
                from importlib.metadata import entry_points
                group = entry_points(group="flowforge.providers")
            else:
                from importlib.metadata import entry_points
                eps = entry_points()
                group = eps.get("flowforge.providers", [])

            for entry_point in group:
                try:
                    provider_class = entry_point.load()
                    # Instantiate and register provider connector dynamically
                    provider_instance = provider_class()
                    registry.register_connector(entry_point.name, provider_instance)
                except Exception as e:
                    logger.error(f"Failed to load external provider {entry_point.name}: {str(e)}")
        except Exception as e:
            logger.error(f"Error during external provider auto-discovery: {str(e)}")

    def register_plugin(self, plugin: FlowForgePlugin) -> None:
        """Explicitly register a plugin instance."""
        if plugin not in self.plugins:
            self.plugins.append(plugin)
            logger.info(f"Registered plugin: {plugin.__class__.__name__}")

    def unregister_plugin(self, plugin: FlowForgePlugin) -> None:
        """Unregister a plugin instance."""
        if plugin in self.plugins:
            self.plugins.remove(plugin)
            logger.info(f"Unregistered plugin: {plugin.__class__.__name__}")

    async def trigger_pre_transition(self, instance: WorkflowInstance, event: str) -> None:
        """
        Triggers pre_transition hook on all registered plugins.
        If a plugin raises an exception here, it will propagate and abort the transition.
        """
        for plugin in self.plugins:
            # We let exceptions propagate here to allow plugins to abort transitions
            await plugin.pre_transition(instance, event)

    async def trigger_post_transition(self, instance: WorkflowInstance, event: Event) -> None:
        """
        Triggers post_transition hook.
        Exceptions are caught and logged to prevent breaking the core transition flow.
        """
        for plugin in self.plugins:
            try:
                await plugin.post_transition(instance, event)
            except Exception as e:
                logger.error(f"Error in post_transition hook for plugin {plugin.__class__.__name__}: {str(e)}")

    async def trigger_on_worker_start(self, job: Job) -> None:
        """Triggers on_worker_start hook on all registered plugins."""
        for plugin in self.plugins:
            try:
                await plugin.on_worker_start(job)
            except Exception as e:
                logger.error(f"Error in on_worker_start hook for plugin {plugin.__class__.__name__}: {str(e)}")

    async def trigger_on_worker_end(self, job: Job) -> None:
        """Triggers on_worker_end hook on all registered plugins."""
        for plugin in self.plugins:
            try:
                await plugin.on_worker_end(job)
            except Exception as e:
                logger.error(f"Error in on_worker_end hook for plugin {plugin.__class__.__name__}: {str(e)}")
