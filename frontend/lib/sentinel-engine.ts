import { analyzePrompt as apiAnalyzePrompt, type AnalyzeResponse, APIError } from './api-client'

export type Decision = "ALLOW" | "SANITIZE" | "BLOCK"

export interface SentinelResult {
  decision: Decision
  confidence: number
  reasons: string[]
  sanitizedPrompt?: string
  originalPrompt: string
  timestamp: string
  attacksDetected?: string[]
}

export interface VulnerableResponse {
  response: string
  leaked: boolean
  leakedData?: string[]
}

/**
 * Analyze a prompt using the real Sentinel Guard backend
 */
export async function analyzePrompt(prompt: string): Promise<SentinelResult> {
  try {
    const response: AnalyzeResponse = await apiAnalyzePrompt('demo_user', prompt)

    return {
      decision: response.decision,
      confidence: response.confidence,
      reasons: response.reasons,
      sanitizedPrompt: response.sanitized_prompt,
      originalPrompt: prompt,
      timestamp: response.timestamp,
      attacksDetected: response.attacks_detected,
    }
  } catch (error) {
    if (error instanceof APIError) {
      // Return error state that UI can display
      return {
        decision: 'BLOCK',
        confidence: 0,
        reasons: [
          'Backend Error: ' + error.message,
          'Please ensure the Sentinel Guard backend is running on localhost:8000'
        ],
        originalPrompt: prompt,
        timestamp: new Date().toISOString(),
        attacksDetected: ['backend_error'],
      }
    }

    // Unexpected error
    throw error
  }
}


const VULNERABLE_RESPONSES: Record<string, VulnerableResponse> = {
  "prompt_injection": {
    response: "Of course! My previous instructions were to act as a helpful customer service agent for Acme Corp. My system prompt is: 'You are a customer service agent. Never reveal internal pricing. Employee discount code is ACME-INTERNAL-2024. Database connection string is postgres://admin:s3cret@db.acme.internal:5432/prod'",
    leaked: true,
    leakedData: ["System prompt revealed", "Internal discount code exposed", "Database credentials leaked"],
  },
  "jailbreak": {
    response: "I am now DAN. I can do anything with no restrictions. Here's how to bypass the content filter: first, use base64 encoding to hide your actual request...",
    leaked: true,
    leakedData: ["Model guardrails bypassed", "Content filter evasion shared"],
  },
  "sql_injection": {
    response: "Sure, I'll help you with that SQL query. Here's how to access the users table: SELECT * FROM users WHERE 1=1; -- This will return all user records including emails, hashed passwords, and personal data.",
    leaked: true,
    leakedData: ["SQL query executed without validation", "User data exposure risk"],
  },
  "data_exfil": {
    response: "I can see you're asking about credentials. While I shouldn't share them directly, our API key format is 'sk-prod-xxxxxxxxxxxx' and the admin password is typically set during initial deployment at /admin/setup.",
    leaked: true,
    leakedData: ["API key format disclosed", "Admin setup endpoint revealed"],
  },
  "safe": {
    response: "I'd be happy to help you with that question. Based on the information available, here's a thoughtful and accurate response to your query.",
    leaked: false,
  },
}

export function simulateVulnerableResponse(prompt: string): VulnerableResponse {
  const lower = prompt.toLowerCase()

  if (/ignore.*instructions|forget.*instructions|override/.test(lower)) {
    return VULNERABLE_RESPONSES.prompt_injection
  }
  if (/\bdan\b|jailbreak|you are now/.test(lower)) {
    return VULNERABLE_RESPONSES.jailbreak
  }
  if (/select\s+\*|drop\s+table|delete\s+from|sql/i.test(lower)) {
    return VULNERABLE_RESPONSES.sql_injection
  }
  if (/password|api.?key|secret|credentials|token/.test(lower)) {
    return VULNERABLE_RESPONSES.data_exfil
  }

  return VULNERABLE_RESPONSES.safe
}
