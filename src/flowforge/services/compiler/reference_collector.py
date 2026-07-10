import os
from typing import List

class ReferenceCollector:
    @staticmethod
    def collect_references(reference_keys: List[str], references_dir: str) -> List[str]:
        """
        Collects text/doc reference content from references_dir matching the keys listed in the mission.
        """
        collected = []
        if not os.path.exists(references_dir):
            return collected

        for ref_key in reference_keys:
            # Look for matching file name, e.g. ref_key.txt or ref_key.md
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
        return collected
