import yaml
import os
import re
import subprocess
from typing import Dict, Any, List, Optional
from dataclasses import asdict
from flowforge.services.runtime.provider_registry import AIRuntimeProviderRegistry
from flowforge.ports.ai_provider import AIProvider
from flowforge.domain.mission_package import MissionPackage

def parse_and_write_files(content: str, base_path: str) -> List[str]:
    """Parses <file path="...">...</file> tags from AI output and writes them to disk."""
    files_changed = []
    # Pattern to find file blocks
    pattern = r'<file\s+path=["\'](.*?)["\']\s*>(.*?)</file>'
    matches = re.finditer(pattern, content, re.DOTALL)
    for match in matches:
        rel_path = match.group(1)
        file_content = match.group(2)
        
        # Strip CDATA if present
        cdata_pattern = r'^\s*<!\[CDATA\[(.*?)\]\]>\s*$'
        cdata_match = re.match(cdata_pattern, file_content, re.DOTALL)
        if cdata_match:
            file_content = cdata_match.group(1)
            
        file_content = file_content.strip() + "\n"
        
        abs_path = os.path.join(base_path, rel_path)
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        with open(abs_path, "w", encoding="utf-8") as f:
            f.write(file_content)
        files_changed.append(rel_path)
        print(f"[FlowForge CLI] -> Wrote file: {rel_path}")
        
    return files_changed

class SubprocessCLIProviderAdapter(AIProvider):
    """Executes AI providers via local CLI commands."""
    def __init__(self, name_str: str, command: str, health_command: Optional[str] = None):
        self._name = name_str
        self.command = command
        self.health_command = health_command

    def name(self) -> str:
        return self._name

    def health(self) -> Dict[str, Any]:
        return {
            "installed": True,
            "available": True,
            "healthy": True,
            "health_command": self.health_command
        }

    def execute(self, mission_package: MissionPackage, **kwargs) -> Dict[str, Any]:
        base_path = kwargs.get("base_path", ".")
        mission_code = mission_package.mission.get("id", "UNKNOWN")
        
        # Determine package file path
        package_file_path = os.path.join(base_path, ".flowforge", "packages", f"{mission_code}.package.yaml")
        
        # Append package path to command
        full_command = f"{self.command} {package_file_path}"
        
        print(f"[FlowForge CLI] Executing CLI Provider '{self.name()}': {full_command}")
        
        try:
            result = subprocess.run(
                full_command,
                shell=True,
                cwd=base_path
            )
            
            status = "SUCCESS" if result.returncode == 0 else "FAILED"
            
            return {
                "status": status,
                "summary": f"Executed CLI command with return code {result.returncode}.",
                "artifacts": [],
                "decisions": [],
                "files_changed": [],
                "warnings": [],
                "blockers": [],
                "recommendations": [],
                "handover_summary": None,
                "provider_metadata": {
                    "provider": self.name(),
                    "command_executed": full_command,
                    "returncode": result.returncode
                }
            }
        except Exception as e:
            return {
                "status": "FAILED",
                "summary": f"Failed to execute CLI command: {str(e)}"
            }

class GoogleGeminiAPIProviderAdapter(AIProvider):
    """Executes AI providers directly via REST APIs using google-generativeai."""
    def __init__(self, name_str: str, model: str, api_key_env: str, api_key: str = None):
        self._name = name_str
        self.model = model
        self.api_key_env = api_key_env
        self.api_key = api_key

    def name(self) -> str:
        return self._name

    def health(self) -> Dict[str, Any]:
        has_key = bool(self.api_key or os.environ.get(self.api_key_env))
        return {
            "installed": True, 
            "available": has_key, 
            "healthy": has_key, 
            "error": f"Missing API Key in config and ENV: {self.api_key_env}" if not has_key else None
        }

    def execute(self, mission_package: MissionPackage, **kwargs) -> Dict[str, Any]:
        try:
            from google import genai
            from google.genai import types
        except ImportError:
            return {"status": "FAILED", "summary": "google-genai is not installed. Run 'pip install google-genai'"}
            
        api_key = self.api_key or os.environ.get(self.api_key_env)
        if not api_key:
            return {"status": "FAILED", "summary": f"Missing API Key in provider config or environment variable: {self.api_key_env}"}
            
        print(f"[FlowForge CLI] Executing API Provider '{self.name()}' via Google Gemini SDK (Model: {self.model})")
        print("[FlowForge CLI] Generating AI Response, please wait...")
        
        mission_id = mission_package.mission.get("code", mission_package.mission.get("id", "UNKNOWN"))
        base_path = kwargs.get("base_path", ".")
        package_file_path = os.path.join(base_path, ".flowforge", "packages", f"{mission_id}.package.yaml")
        
        if os.path.exists(package_file_path):
            with open(package_file_path, "r", encoding="utf-8") as f:
                payload = f.read()
        else:
            payload = yaml.dump(asdict(mission_package), default_flow_style=False)
        
        system_instruction = (
            "You are an autonomous AI software engineer. You are provided with a Mission Package containing context, goals, and constraints. "
            "Execute the mission and output the requested reports or code.\n\n"
            "IMPORTANT: If you write or modify any files, you MUST enclose the file contents in the following XML format:\n"
            "<file_changes>\n"
            '  <file path="src/example/path.ts">\n'
            "    <![CDATA[\n"
            "    // your full file content here\n"
            "    ]]>\n"
            "  </file>\n"
            "</file_changes>\n\n"
            f"CRITICAL: You MUST output your execution report in your response, wrapped in the XML format above, targeting the exact file path: engineering/reports/{mission_id}-Execution-Report.md\n"
        )
        prompt = f"MISSION PACKAGE:\n\n{payload}"
        
        try:
            client = genai.Client(api_key=api_key)
            
            # Remove the 'models/' prefix if the user included it by accident
            model_name = self.model.replace("models/", "")
            
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction
                )
            )
            
            
            content = response.text
            
            print("\n" + "="*50)
            print("[AI Execution Output]")
            print("="*50)
            print(f"RAW RESPONSE DUMP: {response}")
            print(content)
            print("="*50 + "\n")
            
            files_written = []
            try:
                base_path = kwargs.get("base_path", ".")
                files_written = parse_and_write_files(content, base_path)
            except Exception as e:
                print(f"[FlowForge CLI] -> Error writing parsed files: {e}")
            
            return {
                "status": "SUCCESS",
                "summary": "Received successful completion from API.",
                "artifacts": [f for f in files_written if 'reports/' in f or f.endswith('.md')],
                "decisions": [],
                "files_changed": files_written,
                "warnings": [],
                "blockers": [],
                "recommendations": [],
                "handover_summary": None,
                "provider_metadata": {
                    "provider": self.name(),
                    "model": self.model
                }
            }
        except Exception as e:
            return {
                "status": "FAILED",
                "summary": f"API execution failed: {str(e)}"
            }

class OpenAIAPIProviderAdapter(AIProvider):
    """Executes AI providers directly via REST APIs using official openai library."""
    def __init__(self, name_str: str, model: str, api_key_env: str, api_key: str = None):
        self._name = name_str
        self.model = model
        self.api_key_env = api_key_env
        self.api_key = api_key

    def name(self) -> str:
        return self._name

    def health(self) -> Dict[str, Any]:
        has_key = bool(self.api_key or os.environ.get(self.api_key_env))
        return {
            "installed": True, 
            "available": has_key, 
            "healthy": has_key, 
            "error": f"Missing API Key in config and ENV: {self.api_key_env}" if not has_key else None
        }

    def execute(self, mission_package: MissionPackage, **kwargs) -> Dict[str, Any]:
        try:
            from openai import OpenAI
        except ImportError:
            return {"status": "FAILED", "summary": "openai is not installed. Run 'pip install openai'"}
            
        api_key = self.api_key or os.environ.get(self.api_key_env)
        if not api_key:
            return {"status": "FAILED", "summary": f"Missing API Key in provider config or environment variable: {self.api_key_env}"}
            
        print(f"[FlowForge CLI] Executing API Provider '{self.name()}' via OpenAI SDK (Model: {self.model})")
        print("[FlowForge CLI] Generating AI Response, please wait...")
        
        mission_id = mission_package.mission.get("code", mission_package.mission.get("id", "UNKNOWN"))
        base_path = kwargs.get("base_path", ".")
        package_file_path = os.path.join(base_path, ".flowforge", "packages", f"{mission_id}.package.yaml")
        
        if os.path.exists(package_file_path):
            with open(package_file_path, "r", encoding="utf-8") as f:
                payload = f.read()
        else:
            payload = yaml.dump(asdict(mission_package), default_flow_style=False)
        
        mission_id = mission_package.mission.get("code", mission_package.mission.get("id", "UNKNOWN"))
        
        system_instruction = (
            "You are an autonomous AI software engineer. You are provided with a Mission Package containing context, goals, and constraints. "
            "Execute the mission and output the requested reports or code.\n\n"
            "IMPORTANT: If you write or modify any files, you MUST enclose the file contents in the following XML format:\n"
            "<file_changes>\n"
            '  <file path="src/example/path.ts">\n'
            "    <![CDATA[\n"
            "    // your full file content here\n"
            "    ]]>\n"
            "  </file>\n"
            "</file_changes>\n\n"
            f"CRITICAL: You MUST output your execution report in your response, wrapped in the XML format above, targeting the exact file path: engineering/reports/{mission_id}-Execution-Report.md\n"
        )
        prompt = f"MISSION PACKAGE:\n\n{payload}"
        
        try:
            client = OpenAI(api_key=api_key)
            
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": prompt}
                ]
            )
            
            content = response.choices[0].message.content
            
            print("\n" + "="*50)
            print("[AI Execution Output]")
            print("="*50)
            print(content)
            print("="*50 + "\n")
            
            files_written = []
            try:
                base_path = kwargs.get("base_path", ".")
                files_written = parse_and_write_files(content, base_path)
            except Exception as e:
                print(f"[FlowForge CLI] -> Error writing parsed files: {e}")
            
            return {
                "status": "SUCCESS",
                "summary": "Received successful completion from API.",
                "artifacts": [f for f in files_written if 'reports/' in f or f.endswith('.md')],
                "decisions": [],
                "files_changed": files_written,
                "warnings": [],
                "blockers": [],
                "recommendations": [],
                "handover_summary": None,
                "provider_metadata": {
                    "provider": self.name(),
                    "model": self.model
                }
            }
        except Exception as e:
            return {
                "status": "FAILED",
                "summary": f"API execution failed: {str(e)}"
            }
