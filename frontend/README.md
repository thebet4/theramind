# TheraMind Frontend

Next.js 15 frontend with TailwindCSS and shadcn/ui.

## Quick Start

```bash
npm install
cp .env.example .env.local
# Edit .env.local
npm run dev
```

Open http://localhost:3000

## Tech Stack

- Next.js 15 (App Router)
- TailwindCSS + shadcn/ui
- React Hook Form + Zod
- Supabase Auth
- Axios

## Structure

```
frontend/
├── app/
│   ├── (auth)/         # Login, register
│   └── (dashboard)/    # Protected routes
├── components/         # UI components
├── lib/               # Utilities
├── hooks/             # Custom hooks
└── types/             # TypeScript types
```

## Scripts

```bash
npm run dev        # Development
npm run build      # Production build
npm run lint       # ESLint
npm run test       # Tests
```

## Deployment

```bash
npm run build
vercel deploy --prod
```

