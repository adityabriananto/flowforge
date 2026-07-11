from typing import Dict, Any, List

MISSION_TEMPLATES = {
    "Repository Discovery": {
        "title": "Repository Discovery",
        "description": "Scan project directory structure, dependencies, and requirements to index base knowledge.",
        "goal": "Establish the engineering baseline by scanning and indexing the repository.",
        "deliverables": [
            "Repository Structure Report",
            "Technology Stack Report ({framework} on {language})",
            "Backend Architecture Overview",
            "Frontend Architecture Overview",
            "Dependency Analysis",
            "Database Overview",
            "Queue & Scheduler Analysis",
            "External Integrations Summary",
            "Initial Technical Debt Report"
        ],
        "definition_of_done": [
            "Repository analyzed",
            "Architecture documented",
            "Technology stack identified",
            "PROJECT_STATE updated",
            "Engineering baseline established"
        ],
        "constraints": [
            "Do not modify source code files",
            "Only parse metadata, configurations, and directory layout"
        ]
    },
    "Feature Development": {
        "title": "Feature Development",
        "description": "Implement a new feature or capability according to specifications.",
        "goal": "Build, test, and integrate the proposed feature successfully.",
        "deliverables": [
            "Source Code Implementation",
            "Unit Tests Suite",
            "API Documentation Update"
        ],
        "definition_of_done": [
            "Feature implemented according to specifications",
            "Unit tests pass with >80% coverage",
            "Linter and formatter checks passed",
            "Code compiles without warnings"
        ],
        "constraints": [
            "Must follow clean coding guidelines",
            "No breaking changes to existing APIs"
        ]
    },
    "Bug Fix": {
        "title": "Bug Fix",
        "description": "Resolve a reported bug or unexpected execution failure.",
        "goal": "Identify root cause and correct the erroneous code flow.",
        "deliverables": [
            "Regression Test Case",
            "Bug Fix Patch",
            "Post-Mortem Brief"
        ],
        "definition_of_done": [
            "Reported bug is no longer reproducible",
            "Regression tests verify the fix",
            "No regressions introduced in secondary flows"
        ],
        "constraints": [
            "Do not alter unrelated logic"
        ]
    },
    "Refactoring": {
        "title": "Refactoring",
        "description": "Improve internal code structure without changing its external behavior.",
        "goal": "Reduce technical debt, optimize execution speed, or enhance readability.",
        "deliverables": [
            "Refactored Code Modules",
            "Performance Benchmark Comparison",
            "Impact Assessment Report"
        ],
        "definition_of_done": [
            "Code modularity increased",
            "Unit tests verify zero functional regression",
            "Complexity metrics reduced"
        ],
        "constraints": [
            "Zero changes to public API signatures"
        ]
    },
    "Architecture Review": {
        "title": "Architecture Review",
        "description": "Evaluate system design, components modularity, and database patterns.",
        "goal": "Document current architecture limits and draft optimization RFCs.",
        "deliverables": [
            "ADR (Architecture Decision Record) Draft",
            "System Topology Diagram",
            "Scalability Bottlenecks Brief"
        ],
        "definition_of_done": [
            "System architecture thoroughly analyzed",
            "Bottlenecks documented",
            "Proposed design changes recorded in ADR/RFC format"
        ],
        "constraints": [
            "Analytical only, no code modifications allowed"
        ]
    }
}

def render_mission_data(
    mission_type: str, 
    project_details: Dict[str, Any], 
    custom_title: str = "",
    custom_desc: str = ""
) -> Dict[str, Any]:
    """
    Renders mission template based on type and project details, replacing
    placeholders with detected frameworks, languages, etc.
    """
    tpl = MISSION_TEMPLATES.get(mission_type, MISSION_TEMPLATES["Repository Discovery"])
    
    # Extract framework, language, and project_type safely
    fw = project_details.get("framework") or "Unknown Framework"
    lang = project_details.get("language") or "Unknown Language"
    pt = project_details.get("project_type") or "Generic Project"
    
    # Format templates
    title = custom_title or tpl["title"]
    description = custom_desc or tpl["description"]
    goal = tpl["goal"].format(framework=fw, language=lang, project_type=pt)
    
    deliverables = []
    for d in tpl["deliverables"]:
        deliverables.append(d.format(framework=fw, language=lang, project_type=pt))
        
    definition_of_done = list(tpl["definition_of_done"])
    constraints = list(tpl["constraints"])
    
    return {
        "title": title,
        "description": description,
        "goal": goal,
        "deliverables": deliverables,
        "definition_of_done": definition_of_done,
        "constraints": constraints,
        "references": []
    }
