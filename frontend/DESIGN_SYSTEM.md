# Clinical Frost Design System

> **Source of truth**: `design-tokens.json` and `design.md` at the project root.  
> All Tailwind utilities and CSS custom properties in this project derive from those files.

---

## Overview

The **Clinical Frost** design system produces a bright, sterile, and trustworthy interface for an AI differential-diagnosis workstation. The visual language prioritises precision, calm, and modernity — crisp borders, layered surfaces, and cinematic motion — without ever resorting to generic dashboard aesthetics.

---

## 1. Design Tokens → Tailwind Utilities

### Colors

Every color used in the application must come from this table. No Tailwind built-in colors (e.g. `gray-500`, `blue-600`) are permitted after the revamp.

| Token Key (JSON) | CSS Custom Property | Tailwind Utility Prefix | Hex |
|---|---|---|---|
| `colors.surface` | `--cf-surface` | `clinical-surface` | `#f8fbff` |
| `colors.surface-dim` | `--cf-surface-dim` | `clinical-surface-dim` | `#eef4fb` |
| `colors.surface-bright` | `--cf-surface-bright` | `clinical-surface-bright` | `#ffffff` |
| `colors.surface-container-lowest` | `--cf-surface-container-lowest` | `clinical-surface-container-lowest` | `#ffffff` |
| `colors.surface-container-low` | `--cf-surface-container-low` | `clinical-surface-container-low` | `#f4f8fd` |
| `colors.surface-container` | `--cf-surface-container` | `clinical-surface-container` | `#edf4fc` |
| `colors.surface-container-high` | `--cf-surface-container-high` | `clinical-surface-container-high` | `#e4eef9` |
| `colors.surface-container-highest` | `--cf-surface-container-highest` | `clinical-surface-container-highest` | `#d8e7f5` |
| `colors.surface-variant` | `--cf-surface-variant` | `clinical-surface-variant` | `#dfeaf4` |
| `colors.surface-tint` | `--cf-surface-tint` | `clinical-surface-tint` | `#a9c8e6` |
| `colors.on-surface` | `--cf-on-surface` | `clinical-on-surface` | `#16324b` |
| `colors.on-surface-variant` | `--cf-on-surface-variant` | `clinical-on-surface-variant` | `#5e768e` |
| `colors.inverse-surface` | `--cf-inverse-surface` | `clinical-inverse-surface` | `#16324b` |
| `colors.inverse-on-surface` | `--cf-inverse-on-surface` | `clinical-inverse-on-surface` | `#f4f8fd` |
| `colors.background` | `--cf-background` | `clinical-background` | `#f8fbff` |
| `colors.on-background` | `--cf-on-background` | `clinical-on-background` | `#16324b` |
| `colors.primary` | `--cf-primary` | `clinical-primary` | `#bcdcf4` |
| `colors.on-primary` | `--cf-on-primary` | `clinical-on-primary` | `#13314a` |
| `colors.primary-container` | `--cf-primary-container` | `clinical-primary-container` | `#dff1fd` |
| `colors.on-primary-container` | `--cf-on-primary-container` | `clinical-on-primary-container` | `#254b6b` |
| `colors.inverse-primary` | `--cf-inverse-primary` | `clinical-inverse-primary` | `#4d87b7` |
| `colors.primary-fixed` | `--cf-primary-fixed` | `clinical-primary-fixed` | `#dff1fd` |
| `colors.primary-fixed-dim` | `--cf-primary-fixed-dim` | `clinical-primary-fixed-dim` | `#bcdcf4` |
| `colors.secondary` | `--cf-secondary` | `clinical-secondary` | `#d7e8f7` |
| `colors.on-secondary` | `--cf-on-secondary` | `clinical-on-secondary` | `#24415b` |
| `colors.secondary-container` | `--cf-secondary-container` | `clinical-secondary-container` | `#eaf4fc` |
| `colors.on-secondary-container` | `--cf-on-secondary-container` | `clinical-on-secondary-container` | `#4a6b88` |
| `colors.tertiary` | `--cf-tertiary` | `clinical-tertiary` | `#e3eef8` |
| `colors.on-tertiary` | `--cf-on-tertiary` | `clinical-on-tertiary` | `#21415a` |
| `colors.tertiary-container` | `--cf-tertiary-container` | `clinical-tertiary-container` | `#f1f8fd` |
| `colors.on-tertiary-container` | `--cf-on-tertiary-container` | `clinical-on-tertiary-container` | `#4f708c` |
| `colors.outline` | `--cf-outline` | `clinical-outline` | `#b7c8d8` |
| `colors.outline-variant` | `--cf-outline-variant` | `clinical-outline-variant` | `#d0dee9` |
| `colors.error` | `--cf-error` | `clinical-error` | `#c45463` |
| `colors.on-error` | `--cf-on-error` | `clinical-on-error` | `#ffffff` |
| `colors.error-container` | `--cf-error-container` | `clinical-error-container` | `#fde6ea` |
| `colors.on-error-container` | `--cf-on-error-container` | `clinical-on-error-container` | `#7f1f31` |

#### Usage Examples

```tsx
// Background
<div className="bg-clinical-surface-bright" />

// Text
<p className="text-clinical-on-surface" />
<p className="text-clinical-on-surface-variant" />  // secondary text

// Borders
<div className="border border-clinical-outline-variant" />
<div className="border border-clinical-outline" />   // stronger border

// Primary accent
<button className="bg-clinical-primary text-clinical-on-primary" />

// Semantic error state
<div className="bg-clinical-error-container text-clinical-on-error-container border-clinical-error" />
```

---

### Typography

| Token | `fontSize` Utility | Size | Weight | Line Height |
|---|---|---|---|---|
| `typography.display-lg` | `text-display-lg` | 84px | 700 | 90px |
| `typography.headline-lg` | `text-headline-lg` | 32px | 600 | 40px |
| `typography.headline-md` | `text-headline-md` | 24px | 500 | 32px |
| `typography.body-lg` | `text-body-lg` | 18px | 400 | 28px |
| `typography.body-md` | `text-body-md` | 16px | 400 | 24px |
| `typography.label-sm` | `text-label-sm` | 12px | 600 | 16px |

Font family: `Inter` — applied globally via `font-sans` / `font-inter`.

#### Usage Pattern

```tsx
// Page title
<h1 className="text-headline-lg font-semibold text-clinical-on-surface tracking-tight" />

// Section header
<h3 className="text-headline-md font-semibold text-clinical-on-surface" />

// Form label (use the .form-label component class instead)
<label className="text-label-sm font-semibold text-clinical-on-surface-variant tracking-widest uppercase" />

// Body copy
<p className="text-body-md text-clinical-on-surface-variant" />
```

---

### Border Radius

| Token | CSS Var | Tailwind Utility | Value |
|---|---|---|---|
| `rounded.sm` | `--cf-radius-sm` | `rounded-sm` | 0.25rem |
| `rounded.DEFAULT` | `--cf-radius-md` | `rounded` / `rounded-md` | 0.5rem |
| `rounded.lg` | `--cf-radius-lg` | `rounded-lg` | 0.75rem |
| `rounded.xl` | `--cf-radius-xl` | `rounded-xl` | 1rem |
| `rounded.full` | `--cf-radius-full` | `rounded-full` | 9999px |

> **Rule**: Cards use `rounded-xl`. Buttons and inputs use `rounded-lg`. Chips and badges use `rounded-full`.

---

### Box Shadows

| Name | CSS Var | Tailwind Utility | Use |
|---|---|---|---|
| `card-standard` | `--cf-shadow-card` | `shadow-card` | Standard panels, cards |
| `card-elevated` | `--cf-shadow-elevated` | `shadow-card-elevated` | Report viewer, modals |
| `panel` | `--cf-shadow-panel` | `shadow-panel` | Result summary panels |
| `accent` | `--cf-shadow-accent` | `shadow-accent` | Cinematic accent bands |
| `focus` | `--cf-focus-ring` | `shadow-focus` | Focus ring on all interactive elements |

> Apply focus rings via `focus-visible:shadow-focus` and `outline-none`.

---

### Spacing

| Token | CSS Var | Value |
|---|---|---|
| `spacing.unit` | `--cf-spacing-unit` | 8px |
| `spacing.container-padding` | `--cf-container-padding` | 24px |
| `spacing.card-gap` | `--cf-card-gap` | 16px |
| `spacing.section-margin` | `--cf-section-margin` | 40px |
| `spacing.glass-padding` | `--cf-glass-padding` | 20px |

These map to Tailwind arbitrary-value utilities: `p-container-padding`, `gap-card-gap`, etc.

---

### Motion

| Token | CSS Var | Value |
|---|---|---|
| `motion.fast` | `--cf-motion-fast` | 140ms |
| `motion.standard` | `--cf-motion-standard` | 220ms |
| `motion.cinematic` | `--cf-motion-cinematic` | 420ms |
| `motion.drift` | `--cf-motion-drift` | 1200ms |

Custom Tailwind `duration-*` utilities map to these: `duration-fast`, `duration-standard`, `duration-cinematic`, `duration-drift`.

Easing functions:
- `ease-clinical` → `cubic-bezier(0.2, 0, 0, 1)` — standard interaction
- `ease-spring` → `cubic-bezier(0.16, 1, 0.3, 1)` — entrance animations

---

## 2. Component Class Reference

The following reusable component classes are defined in `src/index.css`:

### Buttons

| Class | Spec | When to use |
|---|---|---|
| `.btn-primary` | `bg-clinical-primary` · `text-clinical-on-primary` · `rounded-lg` · `h-12` | Primary action (Generate Report, Save Case) |
| `.btn-ghost` | `bg-clinical-surface-bright` · border · `rounded-lg` · `h-10` | Secondary action (Export PDF, Toggle) |
| `.btn-danger` | `bg-clinical-error-container` · `text-clinical-on-error-container` | Destructive action |

All buttons gain `translateY(-1px)` + `shadow-card` on hover, `translateY(0)` on active.

### Cards

| Class | Background | Border | Shadow | Radius |
|---|---|---|---|---|
| `.card-standard` | `surface-container-low` | `outline-variant` | `shadow-card` | `rounded-md` |
| `.card-elevated` | `surface-bright` | `outline` | `shadow-card-elevated` | `rounded-lg` |

### Inputs

| Class | Description |
|---|---|
| `.input-field` | Standard single-line input — `surface-bright`, `border-outline`, `rounded-lg`, focus glow |
| `.textarea-field` | Auto-resizing textarea — extends `.input-field`, adds `resize-none overflow-hidden` |
| `.form-label` | `text-label-sm font-semibold text-clinical-on-surface-variant tracking-widest uppercase` |

### Badges

| Class | Semantic meaning |
|---|---|
| `.badge-primary` | Primary / neutral indicator |
| `.badge-secondary` | Positive / success state |
| `.badge-tertiary` | Warning / advisory state |
| `.badge-error` | Error / danger state |
| `.badge-high` | Diagnosis high likelihood |
| `.badge-medium` | Diagnosis medium likelihood |
| `.badge-low` | Diagnosis low likelihood |

### Interactive List Items

`.list-item` — transparent background, `border-outline-variant`, `rounded-md`, `transition-colors`. Hover applies `surface-container-low`.

### Accent Band

`.accent-band` — `bg-clinical-primary-container`, `border-outline-variant`, `rounded-lg`, `shadow-accent`. Used for the cinematic top highlight in elevated diagnostic panels.

---

## 3. Diagnosis Confidence Color Mapping

| Likelihood | Bar Fill Color | Badge Class | Token |
|---|---|---|---|
| High | `#4d87b7` (`inverse-primary`) | `.badge-high` | `--cf-inverse-primary` |
| Medium | `#4f708c` (`on-tertiary-container`) | `.badge-medium` | `--cf-on-tertiary-container` |
| Low | `#b7c8d8` (`outline`) | `.badge-low` | `--cf-outline` |

---

## 4. Animations

| Utility | Definition | Use case |
|---|---|---|
| `animate-fade-up` | `fade-up` keyframe — opacity 0→1 + translateY(8px→0), 420ms spring | Page / panel entrance |
| `animate-shimmer` | `shimmer` keyframe — background-position sweep, 1.8s | Loading skeleton |

---

## 5. Modified Files

| File | Change |
|---|---|
| `frontend/tailwind.config.ts` | Extended with all Clinical Frost color, typography, radius, shadow, spacing, and motion tokens |
| `frontend/src/index.css` | Full CSS custom property declaration at `:root`, Google Fonts import, component classes |
| `frontend/src/components/layout/AppShell.tsx` | Surface-bright sidebar, primary active nav, label-sm typography |
| `frontend/src/components/layout/WorkspaceSplitPane.tsx` | Token-based surface and border divisions |
| `frontend/src/components/layout/TabNav.tsx` | Pastel-blue active tab, label-sm uppercase style |
| `frontend/src/components/layout/ClinicalInputPanel.tsx` | btn-primary, input-field, form-label, error-container |
| `frontend/src/components/layout/ReasoningOutputPanel.tsx` | Surface-bright overlay, badge-primary/secondary, tertiary warning banner |
| `frontend/src/components/forms/FormField.tsx` | `.form-label` + `.textarea-field` classes |
| `frontend/src/components/forms/CollapsibleSection.tsx` | Token surfaces, label-sm uppercase header, fade-up animation |
| `frontend/src/components/report/DiagnosisBar.tsx` | Token-mapped bar colors per likelihood level |
| `frontend/src/components/report/SectionBlock.tsx` | headline-md typography, outline-variant border |
| `frontend/src/components/report/ReportRenderer.tsx` | card-elevated, badge-primary/secondary, token-based collapsible findings |
| `frontend/src/components/report/ReportVersionList.tsx` | list-item class, primary-container active state |
| `frontend/src/components/report/DifferentialEvolution.tsx` | Primary-container rank badge, label-sm uppercase header |
| `frontend/src/components/report/EvolutionIndicator.tsx` | Token colors for up/down/new/same directions |
| `frontend/src/components/report/VersionBadge.tsx` | surface-container background, label-sm typography |
| `frontend/src/components/ui/Toast.tsx` | Semantic container tokens per toast type |
| `frontend/src/components/ui/ErrorBanner.tsx` | error-container + error border + rounded-lg |
| `frontend/src/components/ui/LoadingSkeleton.tsx` | Token-based shimmer gradient |
| `frontend/src/components/ui/Spinner.tsx` | inverse-primary default color |
| `frontend/src/components/settings/SettingRow.tsx` | body-md / label-sm typography, outline-variant border |
| `frontend/src/components/settings/ToggleSwitch.tsx` | inverse-primary active, surface-container-highest inactive |
| `frontend/src/components/casebook/CaseCard.tsx` | Lift-on-hover, cinematic accent line, badge-secondary tags |
| `frontend/src/components/casebook/EmptyState.tsx` | Token dashed border, outline-variant icon container, btn-primary |
| `frontend/src/pages/CasebookPage.tsx` | headline-lg title, token search input, token toggle, skeleton |
| `frontend/src/pages/NewCasePage.tsx` | Token header, card form, input-field, btn-primary |
| `frontend/src/pages/CaseWorkspacePage.tsx` | Token workspace header, btn-primary generate, btn-ghost secondary |
| `frontend/src/pages/SettingsPage.tsx` | Sectioned layout, card panels, badge stats, btn actions |
| `frontend/src/components/timeline/TimelinePanel.tsx` | Token-based panel, btn-primary action, error-container error state |
| `frontend/src/components/timeline/TimelineEntry.tsx` | Token badge classes per type, inverse-primary node, surface-bright card |
| `frontend/src/components/timeline/AddFollowUpModal.tsx` | Surface-bright modal, primary-container report toggle, input-field class |
| `frontend/src/components/ui/ErrorBoundary.tsx` | Error-container icon, surface-bright card, btn-primary reload |
| `frontend/DESIGN_SYSTEM.md` | ✨ This documentation file (new) |
