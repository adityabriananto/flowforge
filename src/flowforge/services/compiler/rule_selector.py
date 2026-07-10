import os
from typing import List

class RuleSelector:
    @staticmethod
    def select_relevant_rules(keywords: List[str], rules_file_path: str) -> List[str]:
        """
        Parses rules_file_path (typically AGENTS.md) and extracts rule lines matching mission keywords.
        """
        relevant_rules = []
        if not os.path.exists(rules_file_path):
            return relevant_rules

        try:
            with open(rules_file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                
            current_rule_block = []
            for line in lines:
                line_clean = line.strip()
                if not line_clean:
                    continue
                
                # Check headers or bullet items as rule boundaries
                if line_clean.startswith(("-", "*", "#")):
                    if current_rule_block:
                        # Validate if block is relevant
                        block_text = " ".join(current_rule_block)
                        if not keywords or any(kw.lower() in block_text.lower() for kw in keywords):
                            relevant_rules.append(block_text)
                        current_rule_block = []
                    current_rule_block.append(line_clean)
                else:
                    if current_rule_block:
                        current_rule_block.append(line_clean)
                        
            if current_rule_block:
                block_text = " ".join(current_rule_block)
                if not keywords or any(kw.lower() in block_text.lower() for kw in keywords):
                    relevant_rules.append(block_text)
                    
        except Exception:
            pass
            
        return relevant_rules
