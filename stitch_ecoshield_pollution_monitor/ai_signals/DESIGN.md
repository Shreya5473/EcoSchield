---
name: EcoShield
colors:
  surface: '#0c1324'
  surface-dim: '#0c1324'
  surface-bright: '#33394c'
  surface-container-lowest: '#070d1f'
  surface-container-low: '#151b2d'
  surface-container: '#191f31'
  surface-container-high: '#23293c'
  surface-container-highest: '#2e3447'
  on-surface: '#dce1fb'
  on-surface-variant: '#bbcabf'
  inverse-surface: '#dce1fb'
  inverse-on-surface: '#2a3043'
  outline: '#86948a'
  outline-variant: '#3c4a42'
  surface-tint: '#4edea3'
  primary: '#4edea3'
  on-primary: '#003824'
  primary-container: '#10b981'
  on-primary-container: '#00422b'
  inverse-primary: '#006c49'
  secondary: '#95d3ba'
  on-secondary: '#003829'
  secondary-container: '#0b513d'
  on-secondary-container: '#83c2a9'
  tertiary: '#ffb3af'
  on-tertiary: '#650911'
  tertiary-container: '#fc7c78'
  on-tertiary-container: '#711419'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#6ffbbe'
  primary-fixed-dim: '#4edea3'
  on-primary-fixed: '#002113'
  on-primary-fixed-variant: '#005236'
  secondary-fixed: '#b0f0d6'
  secondary-fixed-dim: '#95d3ba'
  on-secondary-fixed: '#002117'
  on-secondary-fixed-variant: '#0b513d'
  tertiary-fixed: '#ffdad7'
  tertiary-fixed-dim: '#ffb3af'
  on-tertiary-fixed: '#410005'
  on-tertiary-fixed-variant: '#842225'
  background: '#0c1324'
  on-background: '#dce1fb'
  surface-variant: '#2e3447'
typography:
  display-lg:
    fontFamily: Geist
    fontSize: 48px
    fontWeight: '700'
    lineHeight: '1.1'
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Geist
    fontSize: 24px
    fontWeight: '600'
    lineHeight: '1.2'
    letterSpacing: -0.01em
  headline-sm:
    fontFamily: Geist
    fontSize: 18px
    fontWeight: '600'
    lineHeight: '1.4'
  body-lg:
    fontFamily: Geist
    fontSize: 16px
    fontWeight: '400'
    lineHeight: '1.5'
  body-sm:
    fontFamily: Geist
    fontSize: 14px
    fontWeight: '400'
    lineHeight: '1.5'
  label-caps:
    fontFamily: JetBrains Mono
    fontSize: 12px
    fontWeight: '500'
    lineHeight: '1'
    letterSpacing: 0.08em
  data-mono:
    fontFamily: JetBrains Mono
    fontSize: 14px
    fontWeight: '400'
    lineHeight: '1'
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  base: 4px
  container-padding: 24px
  gutter: 16px
  panel-gap: 12px
---

## Brand & Style
The design system establishes a high-performance HUD (Heads-Up Display) aesthetic tailored for environmental intelligence and risk monitoring. The brand personality is vigilant, technical, and authoritative, evoking the atmosphere of a mission control center.

The visual style is **Corporate Modern with HUD influences**, utilizing a sophisticated "Dark Mode" foundation. It prioritizes data density and situational awareness through a highly structured interface. Visual interest is generated through luminous emerald accents against a near-black void, creating a sense of depth and focus suitable for long-term monitoring.

## Colors
The palette is dominated by **Rich Black (#020617)** for the canvas to ensure maximum contrast for data visualization. 

**Emerald Green** serves as the primary "Chrome" color, used for all functional UI elements including borders, active states, and interactive pills. This distinguishes operational tools from the data itself.

**Semantic Risks:**
- **Critical:** Red is reserved exclusively for immediate environmental threats or high-risk zones.
- **Elevated:** Amber denotes areas requiring attention or caution.
- **Stable/Neutral:** Blue represents standard geopolitical or environmental baseline data.
- **Optimal:** Green (distinct from UI Emerald) represents healthy ecological metrics.

## Typography
The typography system uses **Geist** for primary interface elements to provide a clean, high-tech sans-serif feel that remains legible at high densities. **JetBrains Mono** is utilized for labels, data points, and coordinates to reinforce the "instrumentation" aesthetic.

Hierarchy is maintained through strict capitalization rules for labels and the use of monospace numerals for any fluctuating data values to prevent layout shift during updates.

## Layout & Spacing
The layout follows a **Fluid HUD Grid** model. Content is organized into modular panels that dock to the edges of the screen, preserving a central "Focus Area" for the primary visualization (The Globe).

The spacing rhythm is tight, using a 4px baseline to maximize information density. Panels should utilize 12px internal padding to keep content grouped without wasting screen real estate. On mobile, side panels collapse into a bottom-sheet tray or full-screen overlays to maintain the primary view's integrity.

## Elevation & Depth
Depth is achieved through **Tonal Layering and Glassmorphism**. 

- **Surface Level 0:** The near-black background canvas.
- **Surface Level 1 (Panels):** Semi-transparent black overlays (80% opacity) with a subtle backdrop blur (12px) and 1px Emerald Green borders.
- **Surface Level 2 (Popovers/Tooltips):** Solid dark fills with a subtle outer glow in Emerald Green to indicate focus.

Shadows are avoided in favor of light-based depth (borders and inner glows) to maintain the emissive "screen-within-a-screen" feel.

## Shapes
The shape language is precise and geometric. A **Soft (0.25rem)** corner radius is applied to panels and major containers to prevent the interface from feeling overly aggressive while maintaining a professional, engineered look. Interactive elements like buttons and status pills utilize more aggressive rounding (Pill-shaped) to clearly distinguish them from structural containers.

## Components

### Buttons & Pills
Interactive triggers are styled as "Active Chrome." Use a 1px Emerald Green border with a low-opacity Emerald fill (10-15%). Upon hover, the fill opacity increases, and the border gains a subtle neon glow effect.

### Panels
All dashboard panels must feature a header with a 1px Emerald bottom border and a JetBrains Mono title. Close/Expand icons are placed in the top right, styled in a muted grey that turns Emerald on hover.

### Data Inputs
Input fields are "Ghost" style: no background fill, only a 1px bottom border in a muted Emerald. Focus states should trigger a full border box and a subtle inner glow.

### Status Indicators
Small circular dots are used for "Live" status. For risk levels (Critical, Elevated, etc.), use high-contrast badges with white text on the semantic color background to ensure they "pop" against the UI chrome.

### Charts & Sparklines
Keep chart lines thin (1.5px) and use the Emerald green for standard metrics, switching to semantic colors only when thresholds are crossed.