import re

class MisinformationDetector:
    def __init__(self):
        self.categories = {
            "miracle_cures": [
                r"\b100% cure\b", r"\bmagic pill\b", r"\bcure overnight\b", 
                r"\bmiracle\b", r"\binstant cure\b", r"\bsecret cure\b",
                r"\bcure all\b", r"\bguaranteed cure\b"
            ],
            "conspiracy_authority": [
                r"doctors won'?t tell you", r"hidden truth", r"they don'?t want you to know",
                r"medical system is lying", r"big pharma wants you sick",
                r"government is hiding", r"mainstream medicine is fake"
            ],
            "absolutist_language": [
                r"\balways\b", r"\bnever\b", r"\beveryone\b", r"\bperfectly\b"
            ],
            "fear_triggers": [
                r"\bdeadly\b", r"\btoxin\b", r"\bpoison\b", r"will kill you",
                r"\bfatal\b", r"destroy your body", r"\bcancer-causing\b"
            ]
        }
        
    def detect_manipulation(self, text):
        """
        Scan text for phrases that match viral misinformation patterns.
        Returns a dictionary with flags and categories.
        """
        detected_flags = []
        text_lower = text.lower()
        
        for category, patterns in self.categories.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    if category not in detected_flags:
                        detected_flags.append(category)
                        
        is_flagged = len(detected_flags) > 0
        return {
            "is_flagged": is_flagged,
            "manipulation_categories": detected_flags
        }
