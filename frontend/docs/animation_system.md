# Animation System

This document outlines the animation standards, transition definitions, and Framer Motion orchestrations.

## Animation Philosophies

1. **Fluid Micro-interactions**: Hover actions, transitions, and indicators must be smooth, short, and use responsive physics-based springs instead of linear tweens.
2. **Contextual Entrances**: Cards fade and rise slightly when rendered to establish reading focus.
3. **Progress Flows**: Telemetry items pulse with glow shadows while active.

## Motion Configurations

### Hero Entrance Orchestration
- **Container Stagger**:
  - `staggerChildren`: `0.2`
  - `duration`: `0.8`
- **Item Entrance**:
  - `y` shift: `20px` to `0px`
  - `opacity`: `0` to `1`

### Tab Switching Transitions
- Uses `<AnimatePresence mode="wait">`
- Form sliding transition:
  - `y` shift: `10px` to `0px` (entrance) or `-10px` (exit)
  - `opacity`: fade transition `duration: 0.2`

### Results Dashboard Reveal
- Smooth scrolling and fade-in container transition:
  - `y` shift: `30px` to `0px`
  - `duration`: `0.8`
  - `ease`: `easeInOut`
