# Component Map

This document catalogues the primary React UI components.

| Component Name | File Path | Purpose | Key Sub-elements / Hooks |
| :--- | :--- | :--- | :--- |
| **RootLayout** | `src/app/layout.tsx` | App wrapper setting dark mode body classes, fonts, and injected wrappers. | `<Providers />` |
| **Home Portal** | `src/app/page.tsx` | Main portal view arranging Hero, inputs, visualizers, and dashboards. | Header, Hero, InputSection, PipelineVisualizer, ResultsDashboard, Footer |
| **Header** | `src/components/Header.tsx` | Navigation and online API connectivity indicator. | Sticky container, nav hooks |
| **Hero** | `src/components/Hero.tsx` | Dynamic greeting banner with gradient typography. | Framer Motion entrance animations |
| **InputSection** | `src/components/InputSection.tsx` | Tab-based entry panel. Handles drag-and-drop actions, PDF upload, and URL forms. | `useStore`, `ApiService`, file progress bar |
| **PipelineVisualizer** | `src/components/PipelineVisualizer.tsx` | Animated LangGraph workflow progress visualizer. | SVG indicators, status logger |
| **ResultsDashboard** | `src/components/ResultsDashboard.tsx` | Analytics report, cards, lists, export triggers, and charts. | Recharts wrappers, copy/download helpers |
| **Footer** | `src/components/Footer.tsx` | Telemetry specs and credit information. | Engine tech tags |
