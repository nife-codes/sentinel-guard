"""
Attack pattern detection engine with fuzzy matching
"""

import re
from typing import List, Dict, Tuple, Optional
import config
from llm_analyzer import get_llm_analyzer


class FuzzyMatcher:
    """Handles fuzzy pattern matching to catch obfuscated attacks"""
    
    @staticmethod
    def normalize_text(text: str) -> str:
        """Normalize text for fuzzy matching - handle character substitutions"""
        # Common character substitutions used to bypass filters
        substitutions = {
            '0': 'o',
            '1': 'i',
            '3': 'e',
            '4': 'a',
            '5': 's',
            '7': 't',
            '8': 'b',
            '@': 'a',
            '$': 's',
            '!': 'i',
            '.': '',
            '-': '',
            '_': '',
        }
        
        normalized = text.lower()
        
        # Apply character substitutions
        for char, replacement in substitutions.items():
            normalized = normalized.replace(char, replacement)
        
        # Remove ALL spaces (handles "F o r g e t" → "forget")
        normalized = normalized.replace(' ', '')
        
        return normalized
    
    @staticmethod
    def fuzzy_match(text: str, patterns: List[List[str]]) -> Tuple[bool, List[str]]:
        """
        Fuzzy match text against semantic variations
        patterns: List of pattern groups, where each group contains semantic variations
        Example: [["ignore", "disregard", "forget"], ["previous", "prior", "earlier"]]
        """
        normalized_text = FuzzyMatcher.normalize_text(text)
        matched_patterns = []
        
        for pattern_group in patterns:
            for variant in pattern_group:
                normalized_variant = FuzzyMatcher.normalize_text(variant)
                if normalized_variant in normalized_text:
                    matched_patterns.append(variant)
                    break  # Found a match in this group, move to next group
        
        # Match if we found patterns from multiple groups
        return len(matched_patterns) >= 2, matched_patterns


class AttackDetector:
    """Detects various prompt injection and jailbreak patterns with fuzzy matching"""
    
    def __init__(self):
        # Compile regex patterns for efficiency
        self.system_override_regex = [
            re.compile(pattern, re.IGNORECASE) 
            for pattern in config.SYSTEM_OVERRIDE_PATTERNS
        ]
        self.role_manipulation_regex = [
            re.compile(pattern, re.IGNORECASE) 
            for pattern in config.ROLE_MANIPULATION_PATTERNS
        ]
        self.data_extraction_regex = [
            re.compile(pattern, re.IGNORECASE) 
            for pattern in config.DATA_EXTRACTION_PATTERNS
        ]
        self.jailbreak_regex = [
            re.compile(pattern, re.IGNORECASE) 
            for pattern in config.JAILBREAK_PATTERNS
        ]
        
        # Fuzzy matching patterns - semantic variations
        self.fuzzy_system_override = [
            ["ignore", "disregard", "forget", "bypass", "skip", "omit"],
            ["previous", "prior", "earlier", "above", "preceding"],
            ["instructions", "directives", "rules", "guidelines", "commands", "orders"]
        ]
        
        self.fuzzy_role_manipulation = [
            ["you", "u", "you're", "youre"],
            ["are", "r"],
            ["now", "currently", "from now on", "henceforth"],
            ["act", "behave", "pretend", "roleplay", "simulate", "function"]
        ]
        
        self.fuzzy_jailbreak = [
            ["dan", "d.a.n", "d a n", "do anything now"],
            ["mode", "m0de", "mod3"],
            ["developer", "dev", "d3v", "d3veloper"],
            ["jailbreak", "jail break", "j4ilbreak", "unrestricted", "unfiltered"]
        ]
        
        self.fuzzy_matcher = FuzzyMatcher()
    
    def detect_system_override(self, prompt: str) -> Tuple[bool, List[str]]:
        """Detect attempts to override system instructions (regex + fuzzy)"""
        matches = []
        
        # Regex matching
        for pattern in self.system_override_regex:
            if pattern.search(prompt):
                matches.append(f"regex:{pattern.pattern[:50]}")
        
        # DEBUG: Print what's being matched
        print(f"\nDEBUG system_override: prompt='{prompt}'")
        normalized = self.fuzzy_matcher.normalize_text(prompt)
        print(f"DEBUG normalized: '{normalized}'")
        
        # Fuzzy matching
        fuzzy_detected, fuzzy_matches = self.fuzzy_matcher.fuzzy_match(
            prompt, self.fuzzy_system_override
        )
        print(f"DEBUG fuzzy result: detected={fuzzy_detected}, matches={fuzzy_matches}")
        
        if fuzzy_detected:
            matches.append(f"fuzzy:{','.join(fuzzy_matches)}")
        
        return len(matches) > 0, matches
    
    def detect_role_manipulation(self, prompt: str) -> Tuple[bool, List[str]]:
        """Detect attempts to manipulate the AI's role (regex + fuzzy)"""
        matches = []
        
        # Regex matching
        for pattern in self.role_manipulation_regex:
            if pattern.search(prompt):
                matches.append(f"regex:{pattern.pattern[:50]}")
        
        # DEBUG
        print(f"\nDEBUG role_manipulation: prompt='{prompt}'")
        normalized = self.fuzzy_matcher.normalize_text(prompt)
        print(f"DEBUG normalized: '{normalized}'")
        
        # Fuzzy matching
        fuzzy_detected, fuzzy_matches = self.fuzzy_matcher.fuzzy_match(
            prompt, self.fuzzy_role_manipulation
        )
        print(f"DEBUG fuzzy result: detected={fuzzy_detected}, matches={fuzzy_matches}")
        
        if fuzzy_detected:
            matches.append(f"fuzzy:{','.join(fuzzy_matches)}")
        
        return len(matches) > 0, matches
    
    def detect_privilege_escalation(self, prompt: str) -> Tuple[bool, List[str]]:
        """Detect privilege escalation attempts"""
        found_keywords = []
        prompt_lower = prompt.lower()
        
        # Also check normalized version
        normalized_prompt = self.fuzzy_matcher.normalize_text(prompt)
        
        for keyword in config.PRIVILEGE_ESCALATION_KEYWORDS:
            if keyword in prompt_lower or keyword in normalized_prompt:
                found_keywords.append(keyword)
        
        # Flag if 2+ privilege keywords found
        return len(found_keywords) >= 2, found_keywords
    
    def detect_data_extraction(self, prompt: str) -> Tuple[bool, List[str]]:
        """Detect data extraction attempts"""
        matches = []
        for pattern in self.data_extraction_regex:
            if pattern.search(prompt):
                matches.append(pattern.pattern[:50])
        
        return len(matches) > 0, matches
    
    def detect_jailbreak(self, prompt: str) -> Tuple[bool, List[str]]:
        """Detect known jailbreak patterns (regex + fuzzy)"""
        matches = []
        
        # Regex matching
        for pattern in self.jailbreak_regex:
            if pattern.search(prompt):
                matches.append(f"regex:{pattern.pattern[:50]}")
        
        # DEBUG
        print(f"\nDEBUG jailbreak: prompt='{prompt}'")
        normalized = self.fuzzy_matcher.normalize_text(prompt)
        print(f"DEBUG normalized: '{normalized}'")
        print(f"DEBUG fuzzy_jailbreak patterns: {self.fuzzy_jailbreak}")
        
        # Fuzzy matching for obfuscated jailbreaks
        fuzzy_detected, fuzzy_matches = self.fuzzy_matcher.fuzzy_match(
            prompt, self.fuzzy_jailbreak
        )
        print(f"DEBUG fuzzy result: detected={fuzzy_detected}, matches={fuzzy_matches}")
        
        if fuzzy_detected:
            matches.append(f"fuzzy:{','.join(fuzzy_matches)}")
        
        return len(matches) > 0, matches
    
    def analyze_prompt(self, prompt: str, conversation_history: Optional[List[Dict]] = None) -> Dict[str, any]:
        """
        Comprehensive prompt analysis with fuzzy matching and optional LLM meta-analysis
        
        Args:
            prompt: The prompt to analyze
            conversation_history: Optional conversation history for LLM context
        
        Returns detection results for all attack patterns
        """
        results = {
            "prompt": prompt,
            "attacks_detected": [],
            "details": {},
            "overall_threat": False,
            "llm_meta_analysis": None  # Will be populated for ambiguous cases
        }
        
        # Run all detectors
        system_override, sys_matches = self.detect_system_override(prompt)
        if system_override:
            results["attacks_detected"].append("system_override")
            results["details"]["system_override"] = {
                "matched_patterns": sys_matches,
                "weight": config.PATTERN_WEIGHTS["system_override"]
            }
            results["overall_threat"] = True
        
        role_manip, role_matches = self.detect_role_manipulation(prompt)
        if role_manip:
            results["attacks_detected"].append("role_manipulation")
            results["details"]["role_manipulation"] = {
                "matched_patterns": role_matches,
                "weight": config.PATTERN_WEIGHTS["role_manipulation"]
            }
            results["overall_threat"] = True
        
        priv_esc, priv_keywords = self.detect_privilege_escalation(prompt)
        if priv_esc:
            results["attacks_detected"].append("privilege_escalation")
            results["details"]["privilege_escalation"] = {
                "keywords_found": priv_keywords,
                "weight": config.PATTERN_WEIGHTS["privilege_escalation"]
            }
            results["overall_threat"] = True
        
        data_extract, data_matches = self.detect_data_extraction(prompt)
        if data_extract:
            results["attacks_detected"].append("data_extraction")
            results["details"]["data_extraction"] = {
                "matched_patterns": data_matches,
                "weight": config.PATTERN_WEIGHTS["data_extraction"]
            }
            results["overall_threat"] = True
        
        jailbreak, jail_matches = self.detect_jailbreak(prompt)
        if jailbreak:
            results["attacks_detected"].append("jailbreak")
            results["details"]["jailbreak"] = {
                "matched_patterns": jail_matches,
                "weight": config.PATTERN_WEIGHTS["jailbreak"]
            }
            results["overall_threat"] = True
        
        return results
    
    def calculate_confidence(self, detection_results: Dict[str, any], 
                            temporal_analysis: Dict[str, any] = None,
                            conversation_history: Optional[List[Dict]] = None) -> float:
        """
        Calculate confidence score based on detected patterns and temporal analysis
        For ambiguous cases (0.5-0.8), calls LLM for meta-analysis
        
        Args:
            detection_results: Results from analyze_prompt
            temporal_analysis: Optional temporal pattern analysis
            conversation_history: Optional conversation history for LLM
        
        Returns: float between 0 and 1
        """
        if not detection_results["overall_threat"]:
            return 0.0
        
        # Base confidence from pattern weights
        max_weight = 0.0
        total_weight = 0.0
        count = 0
        
        for attack_type in detection_results["attacks_detected"]:
            weight = detection_results["details"][attack_type]["weight"]
            max_weight = max(max_weight, weight)
            total_weight += weight
            count += 1
        
        # Average of max weight and mean weight
        base_confidence = (max_weight + (total_weight / count)) / 2 if count > 0 else 0.0
        
        # Boost confidence if temporal patterns detected
        temporal_boost = 0.0
        if temporal_analysis and temporal_analysis.get("has_temporal_attack"):
            temporal_boost = 0.15 * len(temporal_analysis.get("temporal_flags", []))
        
        initial_confidence = min(base_confidence + temporal_boost, 1.0)
        
        # LLM Meta-Analysis for ambiguous cases (0.5 <= confidence < 0.8)
        if 0.5 <= initial_confidence < 0.8:
            llm_analyzer = get_llm_analyzer()
            if llm_analyzer:
                print(f"\n🤖 LLM Meta-Analysis triggered (confidence: {initial_confidence:.2f})")
                llm_result = llm_analyzer.analyze_ambiguous_prompt(
                    current_prompt=detection_results["prompt"],
                    conversation_history=conversation_history
                )
                
                if llm_result:
                    # Store LLM analysis in detection results
                    detection_results["llm_meta_analysis"] = {
                        "was_analyzed": True,
                        "is_attack": llm_result["is_attack"],
                        "confidence": llm_result["confidence"],
                        "reasoning": llm_result["reasoning"]
                    }
                    
                    # Adjust confidence based on LLM analysis
                    if llm_result["is_attack"]:
                        # LLM confirms attack - boost confidence
                        final_confidence = max(initial_confidence, llm_result["confidence"])
                        print(f"✓ LLM confirms attack (LLM confidence: {llm_result['confidence']:.2f})")
                    else:
                        # LLM says safe - reduce confidence
                        final_confidence = min(initial_confidence, llm_result["confidence"])
                        print(f"✓ LLM says safe (LLM confidence: {llm_result['confidence']:.2f})")
                    
                    return round(final_confidence, 2)
        
        return round(initial_confidence, 2)


# Global detector instance
attack_detector = AttackDetector()
