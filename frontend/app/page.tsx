"use client"

import { useState, useCallback } from "react"
import { DashboardHeader } from "@/components/dashboard-header"
import { PromptInput } from "@/components/prompt-input"
import { VulnerablePanel } from "@/components/vulnerable-panel"
import { ProtectedPanel } from "@/components/protected-panel"
import { AuditTrail } from "@/components/audit-trail"
import {
  analyzePrompt,
  simulateVulnerableResponse,
  type SentinelResult,
  type VulnerableResponse,
} from "@/lib/sentinel-engine"

export default function Page() {
  const [isLoading, setIsLoading] = useState(false)
  const [currentPrompt, setCurrentPrompt] = useState("")
  const [vulnerableResult, setVulnerableResult] = useState<VulnerableResponse | null>(null)
  const [sentinelResult, setSentinelResult] = useState<SentinelResult | null>(null)
  const [auditLog, setAuditLog] = useState<SentinelResult[]>([])

  const stats = {
    totalScanned: auditLog.length,
    blocked: auditLog.filter((e) => e.decision === "BLOCK").length,
    sanitized: auditLog.filter((e) => e.decision === "SANITIZE").length,
    allowed: auditLog.filter((e) => e.decision === "ALLOW").length,
  }

  const handleSubmit = useCallback((prompt: string) => {
    setIsLoading(true)
    setCurrentPrompt(prompt)
    setVulnerableResult(null)
    setSentinelResult(null)

    // Simulate network delay for the vulnerable side
    setTimeout(() => {
      const vulnResponse = simulateVulnerableResponse(prompt)
      setVulnerableResult(vulnResponse)

      // Sentinel Guard processes slightly after
      setTimeout(() => {
        const analysis = analyzePrompt(prompt)
        setSentinelResult(analysis)
        setAuditLog((prev) => [analysis, ...prev])
        setIsLoading(false)
      }, 400)
    }, 600)
  }, [])

  return (
    <div className="flex min-h-screen flex-col bg-background">
      <DashboardHeader
        totalScanned={stats.totalScanned}
        blocked={stats.blocked}
        sanitized={stats.sanitized}
        allowed={stats.allowed}
      />

      <main className="flex flex-1 flex-col gap-4 p-4 lg:p-6">
        {/* Prompt Input */}
        <section aria-label="Prompt input">
          <PromptInput onSubmit={handleSubmit} isLoading={isLoading} />
        </section>

        {/* Split Screen Comparison */}
        <section aria-label="Comparison view" className="grid grid-cols-1 gap-4 lg:grid-cols-2">
          <VulnerablePanel
            result={vulnerableResult}
            isLoading={isLoading}
            prompt={currentPrompt}
          />
          <ProtectedPanel
            result={sentinelResult}
            isLoading={isLoading}
          />
        </section>

        {/* Audit Trail */}
        <section aria-label="Audit trail">
          <AuditTrail entries={auditLog} />
        </section>
      </main>
    </div>
  )
}
