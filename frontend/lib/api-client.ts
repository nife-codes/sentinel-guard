/**
 * API Client for Sentinel Guard Backend
 * Handles all communication with the FastAPI backend
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export interface AnalyzeRequest {
  user_id: string
  prompt: string
}

export interface AnalyzeResponse {
  decision: 'ALLOW' | 'SANITIZE' | 'BLOCK'
  confidence: number
  reasons: string[]
  attacks_detected: string[]
  sanitized_prompt?: string
  timestamp: string
}

export class APIError extends Error {
  constructor(
    message: string,
    public status?: number,
    public details?: unknown
  ) {
    super(message)
    this.name = 'APIError'
  }
}

/**
 * Analyze a prompt using the Sentinel Guard backend
 */
export async function analyzePrompt(
  userId: string,
  prompt: string
): Promise<AnalyzeResponse> {
  try {
    const response = await fetch(`${API_URL}/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_id: userId,
        prompt: prompt,
      } as AnalyzeRequest),
    })

    if (!response.ok) {
      const errorText = await response.text()
      throw new APIError(
        `Backend returned ${response.status}: ${errorText}`,
        response.status,
        errorText
      )
    }

    const data = await response.json()
    return data as AnalyzeResponse
  } catch (error) {
    if (error instanceof APIError) {
      throw error
    }

    // Network or other errors
    if (error instanceof TypeError && error.message.includes('fetch')) {
      throw new APIError(
        'Cannot connect to Sentinel Guard backend. Is it running on ' + API_URL + '?',
        undefined,
        error
      )
    }

    throw new APIError(
      'Unexpected error communicating with backend',
      undefined,
      error
    )
  }
}

/**
 * Health check for the backend
 */
export async function checkBackendHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${API_URL}/`, {
      method: 'GET',
    })
    return response.ok
  } catch {
    return false
  }
}
