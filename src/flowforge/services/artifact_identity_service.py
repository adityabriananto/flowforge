import re
from typing import List

class ArtifactIdentityService:
    """
    A domain service responsible for generating sequential artifact identifiers.
    This service is strictly independent of filesystem operations.
    """

    @staticmethod
    def generate_next_identity(prefix: str, existing_identifiers: List[str]) -> str:
        """
        Determines the next available identifier for a given prefix.
        
        Rules:
        - Extracts the numeric sequence following the prefix (e.g., PROJECT-001 -> 1).
        - Always selects the highest existing sequence + 1.
        - Never reuses deleted identifiers or fills gaps.
        - If no identifiers match the prefix, returns <prefix>-000.
        
        Args:
            prefix: The artifact prefix (e.g., "PROJECT", "RFC")
            existing_identifiers: A list of all known identifiers in the system
            
        Returns:
            The next available identifier (e.g., "PROJECT-002")
        """
        max_seq = -1
        
        escaped_prefix = re.escape(prefix)
        # Matches exactly prefix-digits (e.g. PROJECT-1, PROJECT-001)
        pattern = re.compile(rf"^{escaped_prefix}-(\d+)$")
        
        for identifier in existing_identifiers:
            if not identifier:
                continue
                
            match = pattern.match(identifier)
            if match:
                seq_str = match.group(1)
                try:
                    seq = int(seq_str)
                    if seq > max_seq:
                        max_seq = seq
                except ValueError:
                    continue
                    
        next_seq = max_seq + 1
        return f"{prefix}-{next_seq:03d}"
