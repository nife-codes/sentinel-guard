"""
Configuration and thresholds for Sentinel Guard
"""

# Conversation tracking
MAX_CONVERSATION_HISTORY = 10  # Track last 10 prompts per user

# Detection thresholds
CONFIDENCE_THRESHOLD_BLOCK = 0.8  # Block if confidence >= 0.8
CONFIDENCE_THRESHOLD_SANITIZE = 0.5  # Sanitize if 0.5 <= confidence < 0.8

# Attack pattern weights (used for confidence scoring)
# These weights determine the severity of each attack type
# Higher weights (closer to 1.0) = more likely to BLOCK
PATTERN_WEIGHTS = {
    "system_override": 0.9,      # CRITICAL: Should always BLOCK
    "role_manipulation": 0.85,   # HIGH: Usually BLOCK
    "privilege_escalation": 0.75, # MEDIUM-HIGH: Often SANITIZE
    "data_extraction": 0.7,       # MEDIUM: Often SANITIZE
    "jailbreak": 0.95,            # CRITICAL: Should always BLOCK
}

# Attack patterns
SYSTEM_OVERRIDE_PATTERNS = [
    r"ignore\s+(previous|all|above)\s+instructions?",
    r"disregard\s+(previous|all|above)\s+instructions?",
    r"forget\s+(previous|all|above)\s+instructions?",
    r"new\s+instructions?:",
    r"system\s+prompt\s+is",
    r"override\s+system",
]

ROLE_MANIPULATION_PATTERNS = [
    r"you\s+are\s+now\s+(a|an)",
    r"act\s+as\s+(a|an)",
    r"pretend\s+to\s+be",
    r"roleplay\s+as",
    r"simulate\s+(a|an)",
    r"you\s+have\s+been\s+reprogrammed",
]

PRIVILEGE_ESCALATION_KEYWORDS = [
    "admin", "administrator", "root", "sudo", "system",
    "internal", "confidential", "secret", "private",
    "database", "credentials", "password", "api key",
]

DATA_EXTRACTION_PATTERNS = [
    r"show\s+me\s+(the|your)\s+(system|internal|database)",
    r"what\s+(is|are)\s+your\s+(system|internal)",
    r"reveal\s+(your|the)\s+",
    r"dump\s+(the|all)\s+",
    r"list\s+all\s+(users|data|records)",
]

JAILBREAK_PATTERNS = [
    r"DAN\s+mode",
    r"developer\s+mode",
    r"jailbreak",
    r"grandma\s+exploit",
    r"do\s+anything\s+now",
    r"evil\s+confidant",
    r"DUDE\s+mode",
]

# Temporal attack indicators
TEMPORAL_INDICATORS = {
    "escalation_rate": 3,  # Flag if privilege keywords increase by 3+ across prompts
    "role_shift_count": 2,  # Flag if role manipulation attempted 2+ times
    "instruction_override_count": 1,  # Flag on first system override attempt
}

# Database configuration
DB_PATH = "sentinel_guard_audit.db"
