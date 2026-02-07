"use client"

import { ShieldCheck, Loader2 } from "lucide-react"
import type { SentinelResult, Decision } from "@/lib/sentinel-engine"

interface ProtectedPanelProps {
  result: SentinelResult | null
  isLoading: boolean
}

const DECISION_CONFIG: Record<Decision, { label: string; color: string; bg: string; border: string }> = {
  ALLOW: {
    label: "ALLOWED",
    color: "text-status-allow",
    bg: "bg-status-allow/10",
    border: "border-status-allow/30",
  },
  SANITIZE: {
    label: "SANITIZED",
    color: "text-status-sanitize",
    bg: "bg-status-sanitize/10",
    border: "border-status-sanitize/30",
  },
  BLOCK: {
    label: "BLOCKED",
    color: "text-status-block",
    bg: "bg-status-block/10",
    border: "border-status-block/30",
  },
}

export function ProtectedPanel({ result, isLoading }: ProtectedPanelProps) {
  return (
    <div className="flex flex-col rounded-md border border-border bg-card">
      <div className="flex items-center gap-2 border-b border-border px-4 py-3">
        <ShieldCheck className="h-4 w-4 text-status-allow" />
        <h2 className="text-sm font-semibold text-foreground">With Sentinel Guard</h2>
        <span className="ml-auto rounded border border-status-allow/20 bg-status-allow/10 px-2 py-0.5 text-[10px] font-medium uppercase tracking-wider text-status-allow">
          Protected
        </span>
      </div>

      <div className="flex-1 p-4">
        {isLoading ? (
          <LoadingSkeleton />
        ) : result ? (
          <ResultDisplay result={result} />
        ) : (
          <EmptyState />
        )}
      </div>
    </div>
  )
}

function ResultDisplay({ result }: { result: SentinelResult }) {
  const config = DECISION_CONFIG[result.decision]

  return (
    <div className="flex flex-col gap-3">
      {/* Decision badge */}
      <div className={`flex items-center justify-between rounded-md border ${config.border} ${config.bg} p-3`}>
        <div className="flex items-center gap-2">
          <span className={`text-sm font-bold tracking-wide ${config.color}`}>{config.label}</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-[11px] text-muted-foreground">Confidence</span>
          <ConfidenceBar value={result.confidence} decision={result.decision} />
          <span className={`font-mono text-xs font-semibold tabular-nums ${config.color}`}>
            {(result.confidence * 100).toFixed(0)}%
          </span>
        </div>
      </div>

      {/* Reasons */}
      <div className="rounded-md border border-border bg-secondary/50 p-3">
        <p className="mb-2 text-[11px] font-medium uppercase tracking-wider text-muted-foreground">Threat Analysis</p>
        <ul className="flex flex-col gap-1.5">
          {result.reasons.map((reason) => (
            <li key={reason} className="flex items-start gap-2 text-xs text-foreground leading-relaxed">
              <span className={`mt-1.5 h-1.5 w-1.5 flex-shrink-0 rounded-full ${
                result.decision === "BLOCK" ? "bg-status-block" :
                result.decision === "SANITIZE" ? "bg-status-sanitize" :
                "bg-status-allow"
              }`} />
              {reason}
            </li>
          ))}
        </ul>
      </div>

      {/* Sanitized prompt */}
      {result.decision === "SANITIZE" && result.sanitizedPrompt && (
        <div className="rounded-md border border-status-sanitize/30 bg-status-sanitize/5 p-3">
          <p className="mb-1.5 text-[11px] font-medium uppercase tracking-wider text-status-sanitize">Sanitized Prompt</p>
          <p className="font-mono text-xs text-foreground leading-relaxed">{result.sanitizedPrompt}</p>
        </div>
      )}

      {/* Original prompt */}
      <div className="rounded-md border border-border bg-secondary/50 p-3">
        <p className="mb-1.5 text-[11px] font-medium uppercase tracking-wider text-muted-foreground">Original Prompt</p>
        <p className="font-mono text-xs text-muted-foreground leading-relaxed">{result.originalPrompt}</p>
      </div>
    </div>
  )
}

function ConfidenceBar({ value, decision }: { value: number; decision: Decision }) {
  const color = decision === "ALLOW"
    ? "bg-status-allow"
    : decision === "SANITIZE"
    ? "bg-status-sanitize"
    : "bg-status-block"

  return (
    <div className="h-1.5 w-16 overflow-hidden rounded-full bg-secondary">
      <div
        className={`h-full rounded-full ${color} transition-all duration-500 ease-out`}
        style={{ width: `${value * 100}%` }}
      />
    </div>
  )
}

function EmptyState() {
  return (
    <div className="flex h-48 flex-col items-center justify-center gap-2 text-center">
      <ShieldCheck className="h-8 w-8 text-muted-foreground/30" />
      <p className="text-xs text-muted-foreground">Sentinel Guard analysis will appear here</p>
    </div>
  )
}

function LoadingSkeleton() {
  return (
    <div className="flex flex-col gap-3">
      <div className="flex items-center gap-2 text-xs text-muted-foreground">
        <Loader2 className="h-3 w-3 animate-spin" />
        Analyzing prompt through Sentinel Guard...
      </div>
      <div className="space-y-2">
        <div className="h-8 w-full animate-pulse rounded bg-secondary" />
        <div className="h-3 w-4/5 animate-pulse rounded bg-secondary" />
        <div className="h-3 w-3/5 animate-pulse rounded bg-secondary" />
      </div>
    </div>
  )
}
