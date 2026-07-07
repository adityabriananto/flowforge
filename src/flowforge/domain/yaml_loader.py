import uuid
import re
import os
from typing import Dict, Any
from flowforge.domain.models import Workflow, StateConfig

def parse_yaml_fallback(content: str) -> Dict[str, Any]:
    """
    A robust space-indentation aware fallback YAML parser using regex.
    """
    data = {}
    current_section = None
    current_state = None
    current_role = None
    
    lines = content.splitlines()
    for line in lines:
        # Strip trailing comments but keep leading indent spaces
        line_clean = re.sub(r'#.*$', '', line).rstrip()
        if not line_clean.strip():
            continue
            
        indent = len(line_clean) - len(line_clean.lstrip())
        line_stripped = line_clean.strip()
        
        # Root level properties (no indentation)
        if indent == 0:
            root_match = re.match(r'^(name|version|initial_state):\s*["\']?(.*?)["\']?$', line_stripped)
            if root_match:
                data[root_match.group(1)] = root_match.group(2)
                continue
                
            section_match = re.match(r'^(states|transitions|roles):$', line_stripped)
            if section_match:
                current_section = section_match.group(1)
                if current_section == "states":
                    data["states"] = {}
                elif current_section == "roles":
                    data["roles"] = {}
                else:
                    data["transitions"] = []
                current_state = None
                continue
                
        # State definition level (2-space indent)
        elif current_section == "states" and indent == 2:
            state_header = re.match(r'^(\w+):$', line_stripped)
            if state_header:
                current_state = state_header.group(1)
                data["states"][current_state] = {}
                continue
                
        # State properties level (4-space indent)
        elif current_section == "states" and indent == 4 and current_state:
            prop_match = re.match(r'^(\w+):\s*["\']?(.*?)["\']?$', line_stripped)
            if prop_match:
                key = prop_match.group(1)
                val = prop_match.group(2)
                if val.lower() == "true":
                    val = True
                elif val.lower() == "false":
                    val = False
                elif val.isdigit():
                    val = int(val)
                data["states"][current_state][key] = val
                continue
                
        # Roles definition level (2-space indent)
        elif current_section == "roles" and indent == 2:
            role_header = re.match(r'^(\w+):$', line_stripped)
            if role_header:
                current_role = role_header.group(1)
                data["roles"][current_role] = {}
                continue
                
        # Roles properties level (4-space indent)
        elif current_section == "roles" and indent == 4:
            prop_match = re.match(r'^(\w+):\s*["\']?(.*?)["\']?$', line_stripped)
            if prop_match:
                key = prop_match.group(1)
                val = prop_match.group(2)
                data["roles"][current_role][key] = val
                continue
                
        # Transitions level (2-space indent starting with list item dash)
        elif current_section == "transitions" and indent == 2:
            trans_match = re.search(r'from:\s*["\']?(\w+)["\']?,\s*event:\s*["\']?(\w+)["\']?,\s*to:\s*["\']?(\w+)["\']?', line_stripped)
            if trans_match:
                data["transitions"].append({
                    "from": trans_match.group(1),
                    "event": trans_match.group(2),
                    "to": trans_match.group(3)
                })
                
    return data

def load_workflow_from_yaml(yaml_content: str) -> Workflow:
    """
    Loads and parses a Workflow definition from YAML string content.
    Fills transitions table (from_state, event) -> to_state mapping.
    """
    try:
        import yaml
        parsed = yaml.safe_load(yaml_content)
    except ImportError:
        # Use our robust zero-dependency regex fallback YAML parser
        parsed = parse_yaml_fallback(yaml_content)
        
    name = parsed.get("name", "Unnamed Workflow")
    version = parsed.get("version", "1.0.0")
    initial_state = parsed.get("initial_state", "IDLE")
    
    # Reconstruct states configs
    states = {}
    for state_name, config_dict in parsed.get("states", {}).items():
        states[state_name] = StateConfig(
            name=config_dict.get("name", state_name),
            worker_type=config_dict.get("worker_type"),
            script=config_dict.get("script"),
            timeout_seconds=config_dict.get("timeout_seconds", 300),
            next_state=config_dict.get("next_state"),
            on_failure=config_dict.get("on_failure"),
            require_human=config_dict.get("require_human", False),
            on_approve=config_dict.get("on_approve"),
            on_reject=config_dict.get("on_reject"),
            is_final=config_dict.get("is_final", False)
        )
        
    # Reconstruct transitions table
    transitions = {}
    for trans in parsed.get("transitions", []):
        from_s = trans.get("from")
        event = trans.get("event")
        to_s = trans.get("to")
        if from_s and event and to_s:
            transitions[(from_s, event)] = to_s
            
    return Workflow(
        id=uuid.uuid4(),
        name=name,
        version=version,
        initial_state=initial_state,
        states=states,
        transitions=transitions
    )

def load_workflow_from_file(file_path: str) -> Workflow:
    """
    Loads a Workflow from a file on disk. 
    Strictly verifies the file identity using the standard extension '.ff.yaml'.
    """
    if not file_path.endswith(".ff.yaml"):
        raise ValueError(
            f"Invalid FlowForge workflow file extension: '{file_path}'. "
            f"Workflow definition files must strictly end with '.ff.yaml' as the system standard."
        )
        
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Workflow file not found: {file_path}")
        
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    return load_workflow_from_yaml(content)
