# WealthWise AI - Design System
> **Theme**: Fiscal Clarity & Professional Trust  
> **Stack**: Next.js + Tailwind CSS + Shadcn/UI + Lucide Icons

---

## 1. Brand Identity & Voice

### Core Philosophy
WealthWise AI is an **Active Auditor**, not a passive calculator. The interface functions as a "Financial Cockpit"—precise, dark-mode native, and engineered for trust.

### Tone of Voice

| Style | ❌ Bad | ✅ Good |
|-------|--------|---------|
| Competent, Not Corporate | "Please wait while we check." | "Scanning Form 16... Verifying 80CCD(2) Compliance." |
| Urgent, Not Panic-Inducing | "YOU ARE LOSING MONEY!" | "Efficiency Gap: ₹45,000 potential savings detected." |

### "No-Jargon" Translation

| Tax Term | User-Friendly Name |
|----------|-------------------|
| Sec 44ADA | "Presumptive Shield" |
| Sec 112A | "Harvesting Limit" |
| Sec 43B(h) | "MSME Guard" |
| Sec 115BBH | "Crypto Trap" |

---

## 2. Color Palette

### Primary Colors (Tailwind Config)

| Role | Name | Hex | Tailwind | Usage |
|------|------|-----|----------|-------|
| Background | Vault Navy | `#0F172A` | `bg-slate-950` | Main app background |
| Surface | Slate Glass | `#1E293B` | `bg-slate-900` | Cards, Sidebar, Modals |
| Primary | Net-Gain Green | `#10B981` | `text-emerald-500` | "Fix It" buttons, Positive |
| Danger | Leakage Red | `#EF4444` | `text-red-500` | Risk Meters, Tax Liability |
| Accent | Electric Blue | `#3B82F6` | `text-blue-500` | Links, Info tooltips |
| Text Primary | Ledger White | `#F8FAFC` | `text-slate-50` | Headings, Primary Data |
| Text Secondary | Audit Grey | `#94A3B8` | `text-slate-400` | Subtitles, Metadata |

### CSS Variables

```css
@layer base {
  :root {
    --background: 222.2 84% 4.9%;  /* Slate 950 */
    --foreground: 210 40% 98%;     /* Slate 50 */
    --card: 217.2 32.6% 17.5%;     /* Slate 900 */
    --primary: 142.1 76.2% 36.3%;  /* Emerald 600 */
    --destructive: 0 62.8% 30.6%;  /* Red 600 */
  }
 
  body {
    @apply bg-background text-foreground antialiased font-sans;
  }

  /* Force Mono for all Numbers */
  .fiscal-num {
    @apply font-mono tracking-tight;
  }
}
```

---

## 3. Typography

### Font Stack

| Type | Font | Usage |
|------|------|-------|
| Headings | Inter (Variable) | Page Titles, CTAs |
| Body | Roboto (Regular) | Explanations, disclaimers |
| Data/Code | JetBrains Mono | **ALL Numbers** (₹1,50,000), Tax Sections, Audit Logs |

---

## 4. Component Library

### Cards (Guardian Containers)

**Base Style**: `bg-slate-900 border border-slate-800 rounded-xl shadow-sm`

| State | Style |
|-------|-------|
| Idle | White Border (`border-slate-800`) |
| Active/Scanning | Pulsing Blue (`animate-pulse border-blue-500/50`) |
| Issue Found | Red Left Border (`border-l-4 border-l-red-500`) |

### Buttons

| Variant | Style |
|---------|-------|
| Primary (Fix) | `bg-emerald-600 hover:bg-emerald-700 text-white font-semibold rounded-lg shadow-md` |
| Secondary | `bg-transparent border border-slate-700 text-slate-300 hover:bg-slate-800` |
| Ghost | `text-slate-500 hover:text-slate-400 hover:bg-transparent` |

### The "Transparent Brain" Loader

Instead of a spinner, use a **Terminal Log** component:
- Font: JetBrains Mono, `text-xs`, `text-emerald-400`
- Animation: Typewriter effect

```
> Parsing Form 16... Done.
> Identifying Income Heads... Salary (Found), Crypto (Found).
> Running Sec 115BBH Check...
```

---

## 5. UX Patterns

### The "Twin-Engine" Dashboard

| Panel | Background | Content |
|-------|------------|---------|
| Left (The Past) | `bg-slate-950` | Uploaded docs, raw data |
| Right (The Future) | `bg-slate-900` | Simulator, Savings |

### The "Tunnel" Navigation

**Rule**: Once a Guardian flow starts (e.g., "Upload Bank Statement"), remove the sidebar.  
**Focus**: User must finish upload or click "Cancel". No wandering.

### "Human-in-the-Loop" Modal

**Trigger**: Ambiguous Bank Credit detected (>₹20k)

```
┌─────────────────────────────────────────────┐
│ Unidentified Credit: ₹50,000               │
├─────────────────────────────────────────────┤
│ Received from 'UPI-RAZORPAY'.               │
│ Is this Business Income?                    │
│                                             │
│ [Yes, Business (44ADA)]  [No, Personal]     │
└─────────────────────────────────────────────┘
```

---

## 6. Guardian Visual Identity

| Guardian | Color | Icon | Badge |
|----------|-------|------|-------|
| Salary Sentinel | Blue `#3B82F6` | 💼 Briefcase | Shield |
| Portfolio Architect | Purple `#8B5CF6` | 📊 Chart | Graph |
| Hustle Shield | Orange `#F97316` | 🔧 Wrench | Bolt |
| Windfall Warden | Teal `#14B8A6` | 🎁 Gift | Star |

---

## 7. Micro-Copy Library

| State | Copy |
|-------|------|
| Loading | "Auditing your financial DNA..." |
| Success | "Optimization Complete. Refund Unlocked." |
| File Error | "unreadable_pdf: Please upload a clearer version." |
| Crypto Alert | "Sec 115BBH Trap: Crypto losses cannot offset Salary." |
| Privacy | "🔒 Ephemeral Session: Data wiped in 29m 59s." |

---

## 8. Responsive Breakpoints

| Name | Width | Target |
|------|-------|--------|
| Mobile | < 640px | Not primary (fallback) |
| Tablet | 640px - 1024px | Secondary |
| Desktop | 1024px - 1440px | **Primary** |
| Wide | > 1440px | Enhanced |

---

## 9. Accessibility

| Requirement | Standard |
|-------------|----------|
| Color Contrast | WCAG AA (4.5:1 for text) |
| Focus States | Visible outline on all interactive elements |
| Font Size | Minimum 14px for body text |
| Touch Targets | Minimum 44x44px on mobile |