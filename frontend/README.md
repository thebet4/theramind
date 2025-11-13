# TheraMind - Frontend

Next.js 15 frontend for TheraMind platform.

## 🚀 Quick Start

```bash
# Install dependencies
npm install

# Setup environment variables
cp ../.env.example .env.local
# Edit .env.local with your API URLs

# Start development server
npm run dev

# Open browser
open http://localhost:3000
```

## 📁 Project Structure

```
frontend/
├── app/                     # Next.js 15 App Router
│   ├── (auth)/              # Auth routes
│   │   ├── login/
│   │   └── register/
│   │
│   ├── (dashboard)/         # Protected routes
│   │   ├── layout.tsx       # Dashboard layout
│   │   ├── page.tsx         # Dashboard home
│   │   ├── patients/        # Patient management
│   │   ├── sessions/        # Session history
│   │   └── settings/        # User settings
│   │
│   ├── api/                 # API routes (if needed)
│   ├── layout.tsx           # Root layout
│   └── page.tsx             # Landing page
│
├── components/              # React components
│   ├── ui/                  # shadcn/ui components
│   ├── auth/
│   │   ├── LoginForm.tsx
│   │   └── RegisterForm.tsx
│   ├── dashboard/
│   │   ├── Sidebar.tsx
│   │   └── Header.tsx
│   ├── sessions/
│   │   ├── SessionCard.tsx
│   │   ├── SessionUpload.tsx
│   │   └── SummaryView.tsx
│   └── patients/
│       ├── PatientList.tsx
│       └── PatientForm.tsx
│
├── lib/                     # Utilities
│   ├── supabase.ts          # Supabase client
│   ├── api.ts               # API client
│   ├── utils.ts             # Helpers
│   └── validations.ts       # Form validations
│
├── hooks/                   # Custom hooks
│   ├── useAuth.ts
│   ├── useSession.ts
│   └── usePatients.ts
│
├── types/                   # TypeScript types
│   ├── session.ts
│   ├── patient.ts
│   └── user.ts
│
├── styles/                  # Global styles
│   └── globals.css
│
├── public/                  # Static assets
│   ├── images/
│   └── icons/
│
├── package.json
├── tsconfig.json
├── tailwind.config.ts
├── next.config.js
└── .env.example
```

## 🎨 Tech Stack

- **Framework:** Next.js 15 (App Router)
- **Styling:** TailwindCSS
- **Components:** shadcn/ui
- **State:** React hooks + Context
- **Forms:** React Hook Form + Zod
- **Auth:** Supabase Auth
- **HTTP:** Axios
- **Real-time:** Supabase Realtime

## 🧪 Running Tests

```bash
# Unit tests
npm run test

# E2E tests with Playwright
npm run test:e2e

# Component tests
npm run test:components
```

## 📦 Building for Production

```bash
# Build
npm run build

# Start production server
npm start

# Deploy to Vercel
vercel deploy --prod
```

## 🎯 Key Features

- ✅ Server-side rendering (SSR)
- ✅ Static generation where possible
- ✅ Optimistic UI updates
- ✅ Real-time notifications
- ✅ File upload with progress
- ✅ Responsive design (mobile-first)
- ✅ Dark mode support
- ✅ Accessibility (WCAG 2.1)

## 🔧 Scripts

```bash
npm run dev          # Start dev server
npm run build        # Build for production
npm run start        # Start prod server
npm run lint         # Run ESLint
npm run format       # Format with Prettier
npm run type-check   # TypeScript check
```

