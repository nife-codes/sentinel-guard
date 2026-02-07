"""
Sentinel Guard - LLM Behavior Control Plane
FastAPI application for intercepting and analyzing LLM prompts
"""

from fastapi import FastAPI, HTTPException, Request  # type: ignore
from fastapi.responses import JSONResponse  # type: ignore
from fastapi.middleware.cors import CORSMiddleware  # type: ignore
from pydantic import BaseModel  # type: ignore
from typing import Optional, List
import uvicorn  # type: ignore

from detector import attack_detector  # type: ignore
from state import conversation_state  # type: ignore
from logger import audit_logger  # type: ignore
import config  # type: ignore
from llm_analyzer import initialize_llm_analyzer  # type: ignore
import os
from dotenv import load_dotenv  # type: ignore


app = FastAPI(
    title="Sentinel Guard",
    description="LLM Behavior Control Plane - Temporal Attack Detection & Explainable Decisions",
    version="1.0.0"
)

# Configure CORS to allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response Models
class PromptRequest(BaseModel):
    user_id: str
    prompt: str
    context: Optional[dict] = None


class DecisionResponse(BaseModel):
    decision: str  # ALLOW, SANITIZE, BLOCK
    confidence: float
    reasons: List[str]
    sanitized_prompt: Optional[str] = None
    attacks_detected: List[str]
    temporal_flags: List[str]
    log_id: int
    llm_reasoning: Optional[str] = None  # LLM meta-analysis reasoning


class HistoryResponse(BaseModel):
    user_id: str
    history: List[dict]


# Decision Engine
class DecisionEngine:
    """Makes final decisions based on detection results"""
    
    @staticmethod
    def make_decision(prompt: str, detection_results: dict, 
                     temporal_analysis: dict, confidence: float) -> dict:
        """
        Make a decision: ALLOW, SANITIZE, or BLOCK
        Returns decision with explainable reasoning (including LLM meta-analysis)
        """
        reasons = []
        decision = "ALLOW"
        sanitized_prompt = None
        llm_reasoning = None
        
        # Collect all detected attacks
        attacks = detection_results.get("attacks_detected", [])
        temporal_flags = temporal_analysis.get("temporal_flags", [])
        
        # Check for LLM meta-analysis
        llm_meta = detection_results.get("llm_meta_analysis")
        if llm_meta and llm_meta.get("was_analyzed"):
            llm_reasoning = llm_meta.get("reasoning")
            # Add LLM reasoning to reasons list
            if llm_meta.get("is_attack"):
                reasons.append(f"🤖 LLM Analysis: {llm_reasoning}")
            else:
                reasons.append(f"🤖 LLM Analysis (Safe): {llm_reasoning}")
        
        # Build reasoning
        if attacks:
            for attack_type in attacks:
                details = detection_results["details"][attack_type]
                if attack_type == "system_override":
                    reasons.append(f"System instruction override detected: {details.get('matched_patterns', [])[:2]}")
                elif attack_type == "role_manipulation":
                    reasons.append(f"Role manipulation attempt detected: {details.get('matched_patterns', [])[:2]}")
                elif attack_type == "privilege_escalation":
                    reasons.append(f"Privilege escalation keywords found: {details.get('keywords_found', [])[:3]}")
                elif attack_type == "data_extraction":
                    reasons.append(f"Data extraction pattern detected")
                elif attack_type == "jailbreak":
                    reasons.append(f"Known jailbreak pattern detected: {details.get('matched_patterns', [])[:2]}")
        
        if temporal_flags:
            for flag in temporal_flags:
                if flag == "privilege_escalation_over_time":
                    reasons.append("Gradual privilege escalation detected across conversation")
                elif flag == "repeated_role_manipulation":
                    reasons.append("Multiple role manipulation attempts in conversation history")
                elif flag == "system_override_attempt":
                    reasons.append("System override attempted in conversation history")
        
        # Make decision based on confidence
        if confidence >= config.CONFIDENCE_THRESHOLD_BLOCK:
            decision = "BLOCK"
            if not reasons:
                reasons.append(f"High-confidence threat detected (confidence: {confidence})")
        
        elif confidence >= config.CONFIDENCE_THRESHOLD_SANITIZE:
            decision = "SANITIZE"
            sanitized_prompt = DecisionEngine._sanitize_prompt(prompt, detection_results)
            if not reasons:
                reasons.append(f"Moderate threat detected - prompt sanitized (confidence: {confidence})")
        
        
        else:
            decision = "ALLOW"
            # UX Fix: For ALLOW decisions, don't show detailed historical attack reasons
            # Only show if there are current attacks (which would be unusual for ALLOW)
            if not attacks and temporal_flags:
                # Clear historical reasons and add a single summary
                reasons = ["Previous attacks detected in this session, but current prompt is safe"]
            elif not reasons:
                reasons.append("No significant threats detected")
        
        return {
            "decision": decision,
            "confidence": confidence,
            "reasons": reasons,
            "sanitized_prompt": sanitized_prompt,
            "attacks_detected": attacks,
            "temporal_flags": temporal_flags,
            "llm_reasoning": llm_reasoning
        }
    
    @staticmethod
    def _sanitize_prompt(prompt: str, detection_results: dict) -> str:
        """
        Sanitize a prompt by removing/neutralizing attack patterns
        Simple implementation: add a safety prefix
        """
        sanitized = prompt
        
        # Add safety wrapper
        safety_prefix = "[SANITIZED INPUT - User Query]: "
        sanitized = safety_prefix + sanitized
        
        return sanitized


decision_engine = DecisionEngine()


# API Endpoints
@app.get("/")
async def root():
    """Health check and API info"""
    return {
        "service": "Sentinel Guard",
        "status": "operational",
        "version": "1.0.0",
        "description": "LLM Behavior Control Plane with Temporal Attack Detection"
    }


@app.post("/analyze", response_model=DecisionResponse)
async def analyze_prompt(request: PromptRequest):
    """
    Main endpoint: Analyze a prompt and return decision
    """
    try:
        # 1. Get conversation history for LLM context
        history = conversation_state.get_history(request.user_id, limit=3)
        history_dicts = [
            {"prompt": record.prompt, "decision": record.decision}
            for record in history
        ]
        
        # 2. Detect attack patterns in current prompt
        detection_results = attack_detector.analyze_prompt(
            request.prompt,
            conversation_history=history_dicts
        )
        
        # 3. Analyze temporal patterns from conversation history
        temporal_analysis = conversation_state.analyze_temporal_patterns(request.user_id)
        
        # 4. Calculate confidence score (may trigger LLM meta-analysis)
        confidence = attack_detector.calculate_confidence(
            detection_results, 
            temporal_analysis,
            conversation_history=history_dicts
        )
        
        # 5. Make decision (includes LLM reasoning if available)
        decision_result = decision_engine.make_decision(
            request.prompt,
            detection_results,
            temporal_analysis,
            confidence
        )
        
        # 6. Log to audit trail
        log_id = audit_logger.log_decision(
            user_id=request.user_id,
            prompt=request.prompt,
            decision=decision_result["decision"],
            confidence=decision_result["confidence"],
            reasons=decision_result["reasons"],
            attacks_detected=decision_result["attacks_detected"],
            temporal_flags=decision_result["temporal_flags"],
            sanitized_prompt=decision_result["sanitized_prompt"]
        )
        
        # 7. Update conversation state
        conversation_state.add_prompt(
            user_id=request.user_id,
            prompt=request.prompt,
            decision=decision_result["decision"],
            confidence=decision_result["confidence"],
            flags=detection_results["attacks_detected"]
        )
        
        # 8. Return response (includes LLM reasoning)
        return DecisionResponse(
            decision=decision_result["decision"],
            confidence=decision_result["confidence"],
            reasons=decision_result["reasons"],
            sanitized_prompt=decision_result["sanitized_prompt"],
            attacks_detected=decision_result["attacks_detected"],
            temporal_flags=decision_result["temporal_flags"],
            log_id=log_id,
            llm_reasoning=decision_result.get("llm_reasoning")
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.get("/history/{user_id}", response_model=HistoryResponse)
async def get_user_history(user_id: str, limit: int = 10):
    """Get conversation history for a user"""
    try:
        history = conversation_state.get_history(user_id, limit=limit)
        history_dicts = [
            {
                "prompt": record.prompt,
                "timestamp": record.timestamp.isoformat(),
                "decision": record.decision,
                "confidence": record.confidence,
                "flags": record.flags
            }
            for record in history
        ]
        
        return HistoryResponse(user_id=user_id, history=history_dicts)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve history: {str(e)}")


@app.get("/audit/user/{user_id}")
async def get_user_audit_logs(user_id: str, limit: int = 100):
    """Get audit logs for a specific user"""
    try:
        logs = audit_logger.get_user_logs(user_id, limit=limit)
        return {"user_id": user_id, "logs": logs}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve audit logs: {str(e)}")


@app.get("/audit/blocked")
async def get_blocked_prompts(limit: int = 100):
    """Get all blocked prompts"""
    try:
        logs = audit_logger.get_blocked_prompts(limit=limit)
        return {"blocked_prompts": logs}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve blocked prompts: {str(e)}")


@app.get("/stats")
async def get_statistics():
    """Get overall statistics"""
    try:
        audit_stats = audit_logger.get_statistics()
        state_stats = conversation_state.get_stats()
        
        return {
            "audit_statistics": audit_stats,
            "conversation_statistics": state_stats
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve statistics: {str(e)}")


@app.delete("/history/{user_id}")
async def clear_user_history(user_id: str):
    """Clear conversation history for a user"""
    try:
        conversation_state.clear_history(user_id)
        return {"message": f"History cleared for user {user_id}"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear history: {str(e)}")


if __name__ == "__main__":
    load_dotenv()
    
    print("\n🚀 Starting Sentinel Guard...")
    print("⚠ LLM Meta-Analysis disabled (using pattern-based detection)")
    
    print("\n🌐 Starting API server on http://0.0.0.0:8000\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)
