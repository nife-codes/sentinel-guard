# Sentinel Guard Frontend

Interactive web dashboard for the Sentinel Guard AI Prompt Firewall. Provides real-time visualization of prompt analysis, threat detection, and security decisions.

## Features

- 🎯 **Real-time Prompt Analysis** - Submit prompts and see instant security analysis
- 🔍 **Split-Screen Comparison** - Compare vulnerable vs. protected LLM responses
- 📊 **Live Statistics** - Track blocked, sanitized, and allowed prompts
- 📝 **Audit Trail** - Complete history of all analyzed prompts with timestamps
- 🎨 **Modern UI** - Built with Next.js, TypeScript, and shadcn/ui components

## Tech Stack

- **Framework:** Next.js 16 (App Router)
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **Components:** shadcn/ui (Radix UI primitives)
- **Icons:** Lucide React
- **Package Manager:** pnpm

## Prerequisites

- Node.js 18+ 
- pnpm (or npm/yarn)
- Sentinel Guard backend running on `http://localhost:8000`

## Quick Start

### 1. Install Dependencies

```bash
pnpm install
```

### 2. Configure Environment

Create a `.env.local` file (or use the existing one):

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. Start Development Server

```bash
pnpm run dev
```

The frontend will be available at **http://localhost:3000**

### 4. Ensure Backend is Running

Make sure the Sentinel Guard FastAPI backend is running:

```bash
# In the parent directory
python main.py
```

## Available Scripts

```bash
pnpm run dev      # Start development server
pnpm run build    # Build for production
pnpm run start    # Start production server
pnpm run lint     # Run ESLint
```

## Project Structure

```
frontend/
├── app/                    # Next.js app directory
│   ├── layout.tsx         # Root layout with metadata
│   ├── page.tsx           # Main dashboard page
│   └── globals.css        # Global styles
├── components/            # React components
│   ├── dashboard-header.tsx    # Stats header
│   ├── prompt-input.tsx        # Prompt submission form
│   ├── vulnerable-panel.tsx    # Unprotected LLM demo
│   ├── protected-panel.tsx     # Sentinel Guard results
│   ├── audit-trail.tsx         # History table
│   └── ui/                     # shadcn/ui components
├── lib/                   # Utilities and API client
│   ├── api-client.ts      # Backend API integration
│   ├── sentinel-engine.ts # Type definitions
│   └── utils.ts           # Helper functions
└── public/                # Static assets
```

## API Integration

The frontend connects to the Sentinel Guard backend via the `/analyze` endpoint:

**Request:**
```json
{
  "user_id": "demo_user",
  "prompt": "Your prompt here"
}
```

**Response:**
```json
{
  "decision": "BLOCK" | "SANITIZE" | "ALLOW",
  "confidence": 0.95,
  "reasons": ["Threat detected: ..."],
  "attacks_detected": ["prompt_injection"],
  "sanitized_prompt": "...",
  "timestamp": "2024-..."
}
```

## Development Notes

- The "Vulnerable Panel" shows simulated unprotected LLM responses for demonstration purposes
- The "Protected Panel" shows real analysis results from the Sentinel Guard backend
- All prompts are logged in the audit trail with full details
- Statistics update in real-time as you submit prompts

## Troubleshooting

**Frontend won't connect to backend:**
- Verify backend is running on `http://localhost:8000`
- Check `.env.local` has correct `NEXT_PUBLIC_API_URL`
- Look for CORS errors in browser console

**Build errors:**
- Clear `.next` folder: `rm -rf .next`
- Reinstall dependencies: `pnpm install`
- Check Node.js version: `node --version` (should be 18+)

## License

Part of the Sentinel Guard project.
