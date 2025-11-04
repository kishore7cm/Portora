# Portora Design System

## Color Palette Rules

This document defines the **official color palette and design tokens** that must be used consistently across all pages and components in the Portora application.

---

## 🎨 Primary Color Palette

### Brand Colors (Sky Blue)
**Purpose:** Primary brand identity, CTAs, interactive elements

- `brand-50` → `#f0f9ff` - Lightest backgrounds
- `brand-100` → `#e0f2fe` - Very light backgrounds  
- `brand-200` → `#bae6fd` - Light borders/dividers
- `brand-500` → `#0ea5e9` - Base brand color
- `brand-600` → `#0284c7` - **PRIMARY CTA buttons** ⭐
- `brand-700` → `#0369a1` - Hover states

**Usage:**
- Primary buttons: `bg-brand-600` or `bg-gradient-brand`
- Hover states: `hover:bg-brand-700`
- Text links: `text-brand-600` with `hover:text-brand-700`
- Badges/Highlights: `bg-brand-100 text-brand-700`

### Neutral Colors (Grays)
**Purpose:** Text, borders, backgrounds, cards

- `neutral-50` → `#fafafa` - White alternative
- `neutral-100` → `#f5f5f5` - Very light backgrounds
- `neutral-200` → `#e5e5e5` - **Standard borders** ⭐
- `neutral-600` → `#525252` - **Secondary text** ⭐
- `neutral-900` → `#171717` - **Primary text/headings** ⭐

**Usage:**
- Primary text: `text-neutral-900`
- Secondary text: `text-neutral-600`
- Borders: `border-neutral-200`
- Card backgrounds: `bg-white` with `border-neutral-200`

---

## 🎯 Design Tokens

### Gradients
- `bg-gradient-brand` - Primary button gradient
- `bg-gradient-soft` - Subtle background gradients
- `bg-gradient-hero` - Hero section background
- Text gradients: `bg-gradient-to-r from-brand-600 via-brand-500 to-brand-400 bg-clip-text text-transparent`

### Shadows
- `shadow-soft` - Cards, subtle elevation (0 2px 8px)
- `shadow-medium` - Medium elevation (0 4px 16px)
- `shadow-strong` - Strong elevation (0 8px 32px)
- `shadow-brand` - Brand-colored shadow for CTAs

### Transitions
- Default: `transition-all duration-200`
- Smooth: `transition-all duration-300`
- Fast: `transition-all duration-150`

---

## 📋 Component Rules

### Buttons

**Primary Button (CTA):**
```tsx
className="rounded-xl bg-gradient-brand px-6 py-3 font-semibold text-white hover:shadow-brand shadow-medium hover:scale-105 transition-all duration-300"
```

**Secondary Button:**
```tsx
className="rounded-xl border-2 border-neutral-300 px-6 py-3 font-semibold text-neutral-800 hover:bg-neutral-50 hover:border-brand-400 hover:text-brand-600 transition-all duration-300 shadow-soft"
```

### Cards
```tsx
className="rounded-2xl border border-neutral-200 bg-white p-6 shadow-soft hover:shadow-medium transition-all duration-300"
```

### Navigation Links
```tsx
className="text-sm font-medium text-neutral-600 hover:text-brand-600 transition-colors duration-200"
```

---

## 🚫 What NOT to Use

**DO NOT use:**
- `slate-*` colors (use `neutral-*` instead)
- `sky-*` colors (use `brand-*` instead)
- Hard-coded hex colors
- Inconsistent shadow values
- Missing transitions on interactive elements

**Migration Pattern:**
- `slate-200` → `neutral-200`
- `slate-600` → `neutral-600`
- `slate-900` → `neutral-900`
- `sky-600` → `brand-600`
- `bg-sky-600` → `bg-gradient-brand` or `bg-brand-600`

---

## ✅ Quick Reference

| Element | Class |
|---------|-------|
| Primary Text | `text-neutral-900` |
| Secondary Text | `text-neutral-600` |
| Primary Button | `bg-gradient-brand text-white` |
| Secondary Button | `border-neutral-300 text-neutral-800` |
| Card Border | `border-neutral-200` |
| Card Shadow | `shadow-soft` |
| Hover Link | `hover:text-brand-600` |

---

## 📖 Usage Example

```tsx
// ✅ CORRECT
<button className="rounded-xl bg-gradient-brand px-6 py-3 font-semibold text-white hover:shadow-brand shadow-medium transition-all duration-300">
  Get started
</button>

// ❌ WRONG
<button className="bg-sky-600 text-white">
  Get started
</button>
```

---

**Last Updated:** 2025-01-26  
**Maintained by:** Design Team  
**See:** `/src/lib/design-system.ts` for TypeScript definitions
