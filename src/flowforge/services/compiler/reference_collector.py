import os
from typing import List

class ReferenceCollector:
    @staticmethod
    def collect_references(reference_keys: List[str], references_dir: str, base_path: str = ".") -> List[str]:
        """
        Collects text/doc reference content from references_dir matching the keys listed in the mission,
        and automatically appends important project structure configurations deterministically.
        """
        collected = []
        
        # 1. Collect from references_dir
        if os.path.exists(references_dir):
            for ref_key in reference_keys:
                for file_name in os.listdir(references_dir):
                    name_without_ext = os.path.splitext(file_name)[0]
                    if name_without_ext.lower() == ref_key.lower():
                        file_path = os.path.join(references_dir, file_name)
                        try:
                            with open(file_path, "r", encoding="utf-8") as f:
                                content = f.read()
                            collected.append(f"[{file_name}]: {content[:2000]}")
                        except Exception:
                            pass

        # 2. Add standard repository references if they exist
        common_files = ["README.md", "package.json", "composer.json", "requirements.txt", "pyproject.toml"]
        for cf in common_files:
            cf_path = os.path.join(base_path, cf)
            if os.path.exists(cf_path):
                collected.append(f"[{cf}]: Found at repository root")

        return collected
