"use client"

import { Shield } from "lucide-react"

interface DashboardHeaderProps {
  totalScanned: number
  blocked: number
  sanitized: number
  allowed: number
}

export function DashboardHeader({ totalScanned, blocked, sanitized, allowed }: DashboardHeaderProps) {
  return (
    <header className="border-b border-border bg-card">
      <div className="flex items-center justify-between px-6 py-4">
        <div className="flex items-center gap-3">
          <div className="flex h-8 w-8 items-center justify-center rounded-md bg-primary/10">
            <Shield className="h-4 w-4 text-primary" />
          </div>
          <div>
            <h1 className="text-base font-semibold text-foreground tracking-tight">Sentinel Guard</h1>
            <p className="text-xs text-muted-foreground">AI Prompt Firewall</p>
          </div>
        </div>

        <div className="flex items-center gap-6">
          <Stat label="Scanned" value={totalScanned} />
          <Stat label="Blocked" value={blocked} color="text-status-block" />
          <Stat label="Sanitized" value={sanitized} color="text-status-sanitize" />
          <Stat label="Allowed" value={allowed} color="text-status-allow" />
          <div className="flex items-center gap-2 rounded-md border border-border bg-secondary px-3 py-1.5">
            <span className="relative flex h-2 w-2">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-status-allow opacity-75" />
              <span className="relative inline-flex h-2 w-2 rounded-full bg-status-allow" />
            </span>
            <span className="text-xs font-medium text-status-allow">Active</span>
          </div>
        </div>
      </div>
    </header>
  )
}

function Stat({ label, value, color }: { label: string; value: number; color?: string }) {
  return (
    <div className="flex flex-col items-center">
      <span className={`text-sm font-semibold tabular-nums ${color ?? "text-foreground"}`}>{value}</span>
      <span className="text-[11px] text-muted-foreground">{label}</span>
    </div>
  )
}
