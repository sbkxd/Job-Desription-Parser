# Design System

This document outlines the visual tokens, custom Tailwind v4 configurations, typography, and premium styling parameters of the platform.

## Color Tokens

The UI uses a customized dark-first palette:

| Token | CSS Variable Value | HEX | Usage |
| :--- | :--- | :--- | :--- |
| **Background** | `--color-background` | `#09090B` | Core page backgrounds |
| **Cards** | `--color-card-bg` | `#111113` | Component cards, dashboard panel surfaces |
| **Accent Primary** | `--color-accent-primary` | `#00E5FF` | Glowing tabs, links, primary buttons, required tags |
| **Accent Secondary** | `--color-accent-secondary` | `#8B5CF6` | Subheadings, progress fills, preferred tags |
| **Success** | `--color-success-bg` | `#10B981` | Positive tags, checklist markers, passing audits |
| **Warning** | `--color-warning-bg` | `#F59E0B` | Attention items, pending states |
| **Error** | `--color-error-bg` | `#EF4444` | Out-of-taxonomy items, pipeline failure logs |

## CSS & Utility Classes

### 1. Glassmorphism Panel
```css
.glass-panel {
  background: rgba(17, 17, 19, 0.75);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.08);
}
```

### 2. Glowing Borders & Shadows
- **Accent Primary Glow**: `glow-primary` (`box-shadow: 0 0 25px rgba(0, 229, 255, 0.15)`)
- **Accent Secondary Glow**: `glow-secondary` (`box-shadow: 0 0 25px rgba(139, 92, 246, 0.15)`)

### 3. Mesh Grid Patterns
- **Grid Background Overlay**: `grid-bg` (`background-size: 40px 40px` with custom line gradients).
