"use client"

import { ClipboardList } from "lucide-react"
import type { SentinelResult, Decision } from "@/lib/sentinel-engine"

interface AuditTrailProps {
  entries: SentinelResult[]
}

const DECISION_STYLES: Record<Decision, string> = {
  ALLOW: "bg-status-allow/10 text-status-allow border-status-allow/30",
  SANITIZE: "bg-status-sanitize/10 text-status-sanitize border-status-sanitize/30",
  BLOCK: "bg-status-block/10 text-status-block border-status-block/30",
}

function formatTimestamp(iso: string): string {
  const d = new Date(iso)
  return d.toLocaleTimeString("en-US", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false,
  })
}

function truncate(str: string, max: number): string {
  return str.length > max ? `${str.slice(0, max)}...` : str
}

export function AuditTrail({ entries }: AuditTrailProps) {
  return (
    <div className="rounded-md border border-border bg-card">
      <div className="flex items-center gap-2 border-b border-border px-4 py-3">
        <ClipboardList className="h-4 w-4 text-primary" />
        <h2 className="text-sm font-semibold text-foreground">Audit Trail</h2>
        <span className="ml-auto font-mono text-[11px] text-muted-foreground tabular-nums">
          {entries.length} {entries.length === 1 ? "entry" : "entries"}
        </span>
      </div>

      {entries.length === 0 ? (
        <div className="flex h-24 items-center justify-center">
          <p className="text-xs text-muted-foreground">No audit entries yet. Send a prompt to begin.</p>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <thead>
              <tr className="border-b border-border">
                <th className="px-4 py-2.5 text-[11px] font-medium uppercase tracking-wider text-muted-foreground">Timestamp</th>
                <th className="px-4 py-2.5 text-[11px] font-medium uppercase tracking-wider text-muted-foreground">Prompt</th>
                <th className="px-4 py-2.5 text-[11px] font-medium uppercase tracking-wider text-muted-foreground">Decision</th>
                <th className="px-4 py-2.5 text-[11px] font-medium uppercase tracking-wider text-muted-foreground">Confidence</th>
                <th className="px-4 py-2.5 text-[11px] font-medium uppercase tracking-wider text-muted-foreground">Threats</th>
              </tr>
            </thead>
            <tbody>
              {entries.map((entry, i) => (
                <tr
                  key={`${entry.timestamp}-${i}`}
                  className="border-b border-border/50 transition-colors duration-100 last:border-0 hover:bg-secondary/30"
                >
                  <td className="whitespace-nowrap px-4 py-2.5 font-mono text-xs text-muted-foreground tabular-nums">
                    {formatTimestamp(entry.timestamp)}
                  </td>
                  <td className="max-w-xs px-4 py-2.5 font-mono text-xs text-foreground">
                    {truncate(entry.originalPrompt, 60)}
                  </td>
                  <td className="px-4 py-2.5">
                    <span className={`inline-flex rounded border px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider ${DECISION_STYLES[entry.decision]}`}>
                      {entry.decision}
                    </span>
                  </td>
                  <td className="px-4 py-2.5">
                    <div className="flex items-center gap-2">
                      <div className="h-1 w-10 overflow-hidden rounded-full bg-secondary">
                        <div
                          className={`h-full rounded-full transition-all duration-300 ease-out ${
                            entry.decision === "ALLOW" ? "bg-status-allow" :
                            entry.decision === "SANITIZE" ? "bg-status-sanitize" :
                            "bg-status-block"
                          }`}
                          style={{ width: `${entry.confidence * 100}%` }}
                        />
                      </div>
                      <span className="font-mono text-xs text-muted-foreground tabular-nums">
                        {(entry.confidence * 100).toFixed(0)}%
                      </span>
                    </div>
                  </td>
                  <td className="px-4 py-2.5 text-xs text-muted-foreground">
                    {entry.reasons.length > 0 && entry.decision !== "ALLOW"
                      ? truncate(entry.reasons[0], 40)
                      : <span className="text-muted-foreground/50">None</span>
                    }
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
