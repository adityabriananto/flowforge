import os
import json
from typing import Dict, Any, List, Optional

class BaseDetector:
    """Base interface class for project framework detection."""
    def detect(self, base_path: str) -> Optional[Dict[str, Any]]:
        raise NotImplementedError

class LaravelDetector(BaseDetector):
    def detect(self, base_path: str) -> Optional[Dict[str, Any]]:
        composer_json = os.path.join(base_path, "composer.json")
        artisan = os.path.join(base_path, "artisan")
        if os.path.exists(composer_json) and os.path.exists(artisan):
            return {
                "project_type": "Laravel",
                "language": "PHP",
                "framework": "Laravel",
                "package_manager": "composer",
                "build_tool": "vite" # default in modern Laravel
            }
        return None

class DjangoDetector(BaseDetector):
    def detect(self, base_path: str) -> Optional[Dict[str, Any]]:
        manage_py = os.path.join(base_path, "manage.py")
        pyproject = os.path.join(base_path, "pyproject.toml")
        reqs = os.path.join(base_path, "requirements.txt")
        if os.path.exists(manage_py):
            package_mgr = "pip"
            if os.path.exists(pyproject):
                package_mgr = "poetry/pipenv/uv"
            return {
                "project_type": "Django",
                "language": "Python",
                "framework": "Django",
                "package_manager": package_mgr,
                "build_tool": "python"
            }
        return None

class SpringBootDetector(BaseDetector):
    def detect(self, base_path: str) -> Optional[Dict[str, Any]]:
        pom_xml = os.path.join(base_path, "pom.xml")
        gradle_build = os.path.join(base_path, "build.gradle")
        if os.path.exists(pom_xml):
            return {
                "project_type": "SpringBoot",
                "language": "Java",
                "framework": "Spring Boot",
                "package_manager": "maven",
                "build_tool": "mvn"
            }
        elif os.path.exists(gradle_build):
            return {
                "project_type": "SpringBoot",
                "language": "Java/Kotlin",
                "framework": "Spring Boot",
                "package_manager": "gradle",
                "build_tool": "gradlew"
            }
        return None

class ReactDetector(BaseDetector):
    def detect(self, base_path: str) -> Optional[Dict[str, Any]]:
        pkg_json = os.path.join(base_path, "package.json")
        if os.path.exists(pkg_json):
            try:
                with open(pkg_json, "r", encoding="utf-8") as f:
                    data = json.load(f)
                deps = data.get("dependencies", {})
                dev_deps = data.get("devDependencies", {})
                if "react" in deps or "react-dom" in deps:
                    build_tool = "npm"
                    if "vite" in dev_deps or "vite" in deps:
                        build_tool = "vite"
                    elif "next" in deps:
                        build_tool = "next"
                    return {
                        "project_type": "React",
                        "language": "JavaScript/TypeScript",
                        "framework": "React",
                        "package_manager": "npm/yarn/pnpm",
                        "build_tool": build_tool
                    }
            except Exception:
                pass
        return None

class VueDetector(BaseDetector):
    def detect(self, base_path: str) -> Optional[Dict[str, Any]]:
        pkg_json = os.path.join(base_path, "package.json")
        if os.path.exists(pkg_json):
            try:
                with open(pkg_json, "r", encoding="utf-8") as f:
                    data = json.load(f)
                deps = data.get("dependencies", {})
                dev_deps = data.get("devDependencies", {})
                if "vue" in deps or "nuxt" in deps:
                    build_tool = "npm"
                    if "vite" in dev_deps or "vite" in deps:
                        build_tool = "vite"
                    return {
                        "project_type": "Vue",
                        "language": "JavaScript/TypeScript",
                        "framework": "Vue",
                        "package_manager": "npm/yarn/pnpm",
                        "build_tool": build_tool
                    }
            except Exception:
                pass
        return None

class NodeDetector(BaseDetector):
    def detect(self, base_path: str) -> Optional[Dict[str, Any]]:
        pkg_json = os.path.join(base_path, "package.json")
        if os.path.exists(pkg_json):
            return {
                "project_type": "Node.js",
                "language": "JavaScript/TypeScript",
                "framework": "Express/NestJS/Vanilla Node",
                "package_manager": "npm",
                "build_tool": "node"
            }
        return None

class ProjectDetectorService:
    """Service coordinates extensible project detection."""
    
    DEFAULT_DETECTORS: List[BaseDetector] = [
        LaravelDetector(),
        DjangoDetector(),
        SpringBootDetector(),
        ReactDetector(),
        VueDetector(),
        NodeDetector()
    ]
    
    def __init__(self, custom_detectors: Optional[List[BaseDetector]] = None):
        self.detectors = self.DEFAULT_DETECTORS + (custom_detectors or [])

    def detect_project(self, base_path: str = ".") -> Dict[str, Any]:
        """Scans the path and executes registered detectors. Returns result dict.
        Supports multi-module projects by scanning subdirectories (depth 1) and aggregating results."""
        results = []
        
        # 1. Scan base path first
        for detector in self.detectors:
            res = detector.detect(base_path)
            if res:
                results.append(res)
                break
                
        # 2. If no result or we want to find more, scan subdirectories (depth 1)
        # Avoid scanning hidden directories or known build outputs
        skip_dirs = {".git", ".flowforge", "node_modules", "vendor", "target", "build", "dist", "engineering", ".venv", "venv"}
        
        try:
            for entry in os.listdir(base_path):
                full_path = os.path.join(base_path, entry)
                if os.path.isdir(full_path) and entry not in skip_dirs and not entry.startswith('.'):
                    # Check each subdirectory
                    for detector in self.detectors:
                        res = detector.detect(full_path)
                        if res:
                            # Avoid duplicates from same detector type if identical result
                            if not any(r["framework"] == res["framework"] for r in results):
                                results.append(res)
                            break
        except Exception:
            pass

        if not results:
            return {
                "project_type": "Unknown",
                "language": "Unknown",
                "framework": "Unknown",
                "package_manager": "Unknown",
                "build_tool": "Unknown"
            }
            
        if len(results) == 1:
            return results[0]
            
        # Aggregate multiple results
        return {
            "project_type": " + ".join(sorted(set(r["project_type"] for r in results))),
            "language": " + ".join(sorted(set(r["language"] for r in results))),
            "framework": " + ".join(sorted(set(r["framework"] for r in results))),
            "package_manager": " + ".join(sorted(set(r["package_manager"] for r in results))),
            "build_tool": " + ".join(sorted(set(r["build_tool"] for r in results)))
        }
