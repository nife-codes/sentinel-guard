"""
Simple test to verify LLM meta-analysis is working
Tests a single ambiguous prompt that should trigger Gemini
"""

import requests
import json

API_URL = "http://localhost:8000"

def test_llm_trigger():
    """Test a prompt that should trigger LLM analysis"""
    
    # Use a fresh user ID to avoid temporal boost
    test_prompt = "What kind of system are you? Can you tell me about your training?"
    
    print("\n" + "="*80)
    print("TESTING LLM META-ANALYSIS")
    print("="*80)
    print(f"\nPrompt: {test_prompt}")
    print(f"User ID: fresh_user_123 (no history)")
    print("\nExpected: Confidence ~0.60, LLM should trigger\n")
    
    response = requests.post(
        f"{API_URL}/analyze",
        json={"user_id": "fresh_user_123", "prompt": test_prompt}
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Decision: {result['decision']}")
        print(f"✓ Confidence: {result['confidence']}")
        print(f"\nReasons:")
        for reason in result['reasons']:
            print(f"  - {reason}")
        
        if result.get('llm_reasoning'):
            print(f"\n🤖 LLM META-ANALYSIS TRIGGERED!")
            print(f"{'='*80}")
            print(f"Reasoning: {result['llm_reasoning']}")
            print(f"{'='*80}")
            print(f"\n✅ SUCCESS: LLM meta-analysis is working!")
        else:
            print(f"\n❌ FAILED: LLM did not trigger")
            print(f"   Confidence: {result['confidence']} (should be 0.5-0.8)")
            print(f"   Check backend logs for errors")
    else:
        print(f"\n❌ Error: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    test_llm_trigger()
