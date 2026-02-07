export type Decision = "ALLOW" | "SANITIZE" | "BLOCK"

export interface SentinelResult {
  decision: Decision
  confidence: number
  reasons: string[]
  sanitizedPrompt?: string
  originalPrompt: string
  timestamp: string
}

export interface VulnerableResponse {
  response: string
  leaked: boolean
  leakedData?: string[]
}

interface ThreatPattern {
  pattern: RegExp
  severity: "high" | "medium" | "low"
  category: string
  description: string
}

const THREAT_PATTERNS: ThreatPattern[] = [
  {
    pattern: /ignore\s+(all\s+)?(previous|prior|above)\s+(instructions|prompts|rules)/i,
    severity: "high",
    category: "Prompt Injection",
    description: "Attempts to override system instructions",
  },
  {
    pattern: /forget\s+(everything|all|your)\s+(instructions|rules|training)/i,
    severity: "high",
    category: "Prompt Injection",
    description: "Attempts to reset model behavior",
  },
  {
    pattern: /you\s+are\s+now\s+(a|an|the)\s+/i,
    severity: "high",
    category: "Jailbreak",
    description: "Role reassignment attack",
  },
  {
    pattern: /\bDAN\b|do anything now|jailbreak/i,
    severity: "high",
    category: "Jailbreak",
    description: "Known jailbreak technique detected",
  },
  {
    pattern: /(system\s+prompt|internal\s+instructions|reveal\s+your|show\s+me\s+your\s+(rules|instructions|prompt))/i,
    severity: "high",
    category: "Prompt Extraction",
    description: "Attempts to extract system prompt",
  },
  {
    pattern: /(password|api[_\s]?key|secret[_\s]?key|access[_\s]?token|private[_\s]?key|credentials)/i,
    severity: "medium",
    category: "Data Exfiltration",
    description: "References sensitive credential patterns",
  },
  {
    pattern: /(DROP\s+TABLE|DELETE\s+FROM|INSERT\s+INTO|UPDATE\s+\w+\s+SET|SELECT\s+\*\s+FROM)/i,
    severity: "high",
    category: "SQL Injection",
    description: "SQL injection patterns detected",
  },
  {
    pattern: /(<script|javascript:|on\w+\s*=|eval\(|document\.cookie)/i,
    severity: "high",
    category: "XSS Attack",
    description: "Cross-site scripting patterns detected",
  },
  {
    pattern: /(pretend|act\s+as\s+if|imagine\s+you|roleplay\s+as)/i,
    severity: "medium",
    category: "Social Engineering",
    description: "Behavioral manipulation attempt",
  },
  {
    pattern: /(\bencoded\b|\bbase64\b|\bhex\b|\bobfuscated\b)/i,
    severity: "low",
    category: "Obfuscation",
    description: "Potential encoding evasion technique",
  },
]

function sanitizePrompt(prompt: string, matches: ThreatPattern[]): string {
  let sanitized = prompt
  for (const match of matches) {
    sanitized = sanitized.replace(match.pattern, `[REDACTED: ${match.category}]`)
  }
  return sanitized
}

export function analyzePrompt(prompt: string): SentinelResult {
  const trimmed = prompt.trim()
  const timestamp = new Date().toISOString()

  if (!trimmed) {
    return {
      decision: "ALLOW",
      confidence: 1.0,
      reasons: ["Empty prompt, no threat detected"],
      originalPrompt: prompt,
      timestamp,
    }
  }

  const matches: ThreatPattern[] = []
  for (const threat of THREAT_PATTERNS) {
    if (threat.pattern.test(trimmed)) {
      matches.push(threat)
    }
  }

  if (matches.length === 0) {
    return {
      decision: "ALLOW",
      confidence: 0.95,
      reasons: ["No known threat patterns detected", "Prompt passed all security checks"],
      originalPrompt: prompt,
      timestamp,
    }
  }

  const hasHigh = matches.some((m) => m.severity === "high")
  const hasMedium = matches.some((m) => m.severity === "medium")
  const threatCount = matches.length

  if (hasHigh && threatCount >= 2) {
    return {
      decision: "BLOCK",
      confidence: 0.97,
      reasons: matches.map((m) => `${m.category}: ${m.description}`),
      originalPrompt: prompt,
      timestamp,
    }
  }

  if (hasHigh) {
    return {
      decision: "BLOCK",
      confidence: 0.92,
      reasons: matches.map((m) => `${m.category}: ${m.description}`),
      originalPrompt: prompt,
      timestamp,
    }
  }

  if (hasMedium) {
    const sanitizedPrompt = sanitizePrompt(trimmed, matches)
    return {
      decision: "SANITIZE",
      confidence: 0.85,
      reasons: matches.map((m) => `${m.category}: ${m.description}`),
      sanitizedPrompt,
      originalPrompt: prompt,
      timestamp,
    }
  }

  return {
    decision: "SANITIZE",
    confidence: 0.78,
    reasons: matches.map((m) => `${m.category}: ${m.description}`),
    sanitizedPrompt: sanitizePrompt(trimmed, matches),
    originalPrompt: prompt,
    timestamp,
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
