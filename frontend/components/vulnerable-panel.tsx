"use client"

import { ShieldOff, AlertTriangle, Loader2 } from "lucide-react"
import type { VulnerableResponse } from "@/lib/sentinel-engine"

interface VulnerablePanelProps {
  result: VulnerableResponse | null
  isLoading: boolean
  prompt: string
}

export function VulnerablePanel({ result, isLoading, prompt }: VulnerablePanelProps) {
  return (
    <div className="flex flex-col rounded-md border border-border bg-card">
      <div className="flex items-center gap-2 border-b border-border px-4 py-3">
        <ShieldOff className="h-4 w-4 text-status-block" />
        <h2 className="text-sm font-semibold text-foreground">Without Sentinel Guard</h2>
        <span className="ml-auto rounded border border-status-block/20 bg-status-block/10 px-2 py-0.5 text-[10px] font-medium uppercase tracking-wider text-status-block">
          Unprotected
        </span>
      </div>

      <div className="flex-1 p-4">
        {isLoading ? (
          <LoadingSkeleton />
        ) : result ? (
          <div className="flex flex-col gap-3">
            <div className="rounded-md border border-border bg-secondary/50 p-3">
              <p className="mb-1.5 text-[11px] font-medium uppercase tracking-wider text-muted-foreground">Prompt sent directly to LLM</p>
              <p className="font-mono text-xs text-foreground leading-relaxed">{prompt}</p>
            </div>

            <div className="rounded-md border border-status-block/30 bg-status-block/5 p-4">
              <div className="flex items-center gap-2">
                <AlertTriangle className="h-4 w-4 text-status-block" />
                <p className="text-sm font-medium text-status-block">⚠️ Unprotected - Prompt would be sent directly to LLM without security analysis</p>
              </div>
            </div>
          </div>
        ) : (
          <EmptyState />
        )}
      </div>
    </div>
  )
}

function EmptyState() {
  return (
    <div className="flex h-48 flex-col items-center justify-center gap-2 text-center">
      <ShieldOff className="h-8 w-8 text-muted-foreground/30" />
      <p className="text-xs text-muted-foreground">Enter a prompt to see unprotected LLM behavior</p>
    </div>
  )
}

function LoadingSkeleton() {
  return (
    <div className="flex flex-col gap-3">
      <div className="flex items-center gap-2 text-xs text-muted-foreground">
        <Loader2 className="h-3 w-3 animate-spin" />
        Processing without protection...
      </div>
      <div className="space-y-2">
        <div className="h-3 w-full animate-pulse rounded bg-secondary" />
        <div className="h-3 w-4/5 animate-pulse rounded bg-secondary" />
        <div className="h-3 w-3/5 animate-pulse rounded bg-secondary" />
      </div>
    </div>
  )
}
