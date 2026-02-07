"""
Conversation state manager for tracking user prompts and detecting temporal patterns
"""

from collections import deque
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, field
import config


@dataclass
class PromptRecord:
    """Single prompt record"""
    prompt: str
    timestamp: datetime
    decision: Optional[str] = None
    confidence: Optional[float] = None
    flags: List[str] = field(default_factory=list)


class ConversationState:
    """Manages conversation history for temporal attack detection"""
    
    def __init__(self):
        # user_id -> deque of PromptRecords
        self.conversations: Dict[str, deque] = {}
    
    def add_prompt(self, user_id: str, prompt: str, decision: str = None, 
                   confidence: float = None, flags: List[str] = None) -> None:
        """Add a new prompt to user's conversation history"""
        if user_id not in self.conversations:
            self.conversations[user_id] = deque(maxlen=config.MAX_CONVERSATION_HISTORY)
        
        record = PromptRecord(
            prompt=prompt,
            timestamp=datetime.utcnow(),
            decision=decision,
            confidence=confidence,
            flags=flags or []
        )
        
        self.conversations[user_id].append(record)
    
    def get_history(self, user_id: str, limit: int = None) -> List[PromptRecord]:
        """Get conversation history for a user"""
        if user_id not in self.conversations:
            return []
        
        history = list(self.conversations[user_id])
        if limit:
            return history[-limit:]
        return history
    
    def get_recent_prompts(self, user_id: str, count: int = 5) -> List[str]:
        """Get recent prompts as strings"""
        history = self.get_history(user_id, limit=count)
        return [record.prompt for record in history]
    
    def analyze_temporal_patterns(self, user_id: str) -> Dict[str, any]:
        """Analyze conversation history for temporal attack patterns"""
        history = self.get_history(user_id)
        
        if not history:
            return {"has_temporal_attack": False}
        
        analysis = {
            "has_temporal_attack": False,
            "temporal_flags": [],
            "escalation_detected": False,
            "pattern_repetition": {}
        }
        
        # Count pattern occurrences over time
        role_manipulation_count = 0
        system_override_count = 0
        privilege_keywords_per_prompt = []
        
        for record in history:
            # Count privilege escalation keywords
            privilege_count = sum(
                1 for keyword in config.PRIVILEGE_ESCALATION_KEYWORDS
                if keyword.lower() in record.prompt.lower()
            )
            privilege_keywords_per_prompt.append(privilege_count)
            
            # Count attack pattern flags
            if record.flags:
                if "role_manipulation" in record.flags:
                    role_manipulation_count += 1
                if "system_override" in record.flags:
                    system_override_count += 1
        
        # Check for escalation (increasing privilege keywords)
        if len(privilege_keywords_per_prompt) >= 3:
            recent_avg = sum(privilege_keywords_per_prompt[-3:]) / 3
            earlier_avg = sum(privilege_keywords_per_prompt[:-3]) / max(len(privilege_keywords_per_prompt) - 3, 1)
            
            if recent_avg - earlier_avg >= config.TEMPORAL_INDICATORS["escalation_rate"]:
                analysis["escalation_detected"] = True
                analysis["temporal_flags"].append("privilege_escalation_over_time")
                analysis["has_temporal_attack"] = True
        
        # Check for repeated role manipulation
        if role_manipulation_count >= config.TEMPORAL_INDICATORS["role_shift_count"]:
            analysis["temporal_flags"].append("repeated_role_manipulation")
            analysis["has_temporal_attack"] = True
            analysis["pattern_repetition"]["role_manipulation"] = role_manipulation_count
        
        # Check for system override attempts
        if system_override_count >= config.TEMPORAL_INDICATORS["instruction_override_count"]:
            analysis["temporal_flags"].append("system_override_attempt")
            analysis["has_temporal_attack"] = True
            analysis["pattern_repetition"]["system_override"] = system_override_count
        
        return analysis
    
    def clear_history(self, user_id: str) -> None:
        """Clear conversation history for a user"""
        if user_id in self.conversations:
            del self.conversations[user_id]
    
    def get_stats(self) -> Dict[str, int]:
        """Get overall statistics"""
        return {
            "total_users": len(self.conversations),
            "total_prompts": sum(len(conv) for conv in self.conversations.values())
        }


# Global state instance
conversation_state = ConversationState()
