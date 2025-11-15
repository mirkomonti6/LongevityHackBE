# Longevity App - Pelmeni Hackathon

A data-driven longevity app that identifies the one thing that can improve your lifespan the most through an evidence-based approach. Instead of 20 biohacks, you get one clear focus, one simple habit, and measurable progress.

## Concept

The app uses large longevity datasets to identify the most important lifestyle factor for your health based on your lifestyle data and optional blood values. Instead of being overwhelmed with many recommendations, you focus on one evidence-based habit with clear impact.

### UX Flow

1. **Onboarding** (5 steps)
   - Welcome & Goals
   - Basics (Age, Sex, Height, Weight, Medical Flags)
   - Lifestyle Snapshot (Sleep, Movement, Stress, Energy)
   - Blood Test (optional: HbA1c, LDL, HDL, Triglycerides, CRP, Resting Heart Rate)
   - Constraints & Preferences

2. **One Key Factor**
   - Analysis of entered data
   - Identification of the most important improvement area
   - Recommendation of a concrete habit
   - Estimate of potential lifespan extension

3. **Habit Tracking** (coming soon)
   - Weekly check-ins
   - Progress tracking
   - Adaptive adjustments

## Tech Stack

- **Next.js 16** with App Router and React Server Components
- **Tailwind CSS v4** with CSS variables for theming
- **shadcn/ui** for UI components
- **TypeScript** for type safety

## Quick Start

```bash
npm install
npm run dev
```

The app runs at [http://localhost:3000](http://localhost:3000).

## Project Structure

```
src/
├── app/
│   ├── page.tsx              # Main page with onboarding
│   ├── layout.tsx             # Root layout
│   └── globals.css            # Global styles & theme variables
├── components/
│   ├── onboarding/
│   │   ├── onboarding-wizard.tsx    # Main wizard component
│   │   ├── use-onboarding.ts         # State management hook
│   │   ├── summary-card.tsx         # Results view
│   │   └── steps/                    # Individual step components
│   └── ui/                    # shadcn/ui components
└── lib/
    ├── onboarding-schema.ts   # TypeScript types & step configuration
    └── utils.ts              # Helper functions (cn)
```

## Adding Components

```bash
npx shadcn@latest add <component-name>
```

Components are located in `src/components/ui`. The helper function `cn` can be found in `src/lib/utils.ts`.

## Note on Dummy Data

The current implementation uses dummy values and simple heuristics for analysis. Blood values and calculations will later be replaced by backend integration with real longevity datasets.

## Useful Links

- [Next.js Docs](https://nextjs.org/docs)
- [Tailwind CSS v4](https://tailwindcss.com/blog/tailwindcss-v4-alpha)
- [shadcn/ui Registry](https://ui.shadcn.com)
