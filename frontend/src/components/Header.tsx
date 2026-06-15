'use client';

import React from 'react';
import { Cpu, Terminal, Shield } from 'lucide-react';

export default function Header() {
  const scrollTo = (id: string) => {
    const el = document.getElementById(id);
    if (el) {
      el.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <header className="sticky top-0 z-50 w-full border-b border-border-dark glass-panel transition-all duration-300">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between">
          {/* Logo & Title */}
          <div className="flex items-center space-x-3 cursor-pointer" onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}>
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-accent-primary to-accent-secondary p-0.5 shadow-lg shadow-accent-primary/20">
              <div className="flex h-full w-full items-center justify-center rounded-[6px] bg-background">
                <Cpu className="h-5 w-5 text-accent-primary animate-pulse" />
              </div>
            </div>
            <span className="font-sans text-lg font-bold tracking-tight bg-gradient-to-r from-white via-zinc-200 to-zinc-400 bg-clip-text text-transparent">
              JD Skill Intelligence
            </span>
            <span className="rounded bg-accent-primary/10 px-2 py-0.5 text-2xs font-mono font-semibold tracking-wider text-accent-primary border border-accent-primary/25 uppercase">
              v1.0
            </span>
          </div>

          {/* Navigation */}
          <nav className="hidden md:flex items-center space-x-8 text-sm font-medium">
            <button
              onClick={() => scrollTo('analyze-section')}
              className="text-text-secondary hover:text-accent-primary transition-colors duration-200 cursor-pointer"
            >
              Analyze
            </button>
            <button
              onClick={() => scrollTo('features-section')}
              className="text-text-secondary hover:text-accent-primary transition-colors duration-200 cursor-pointer"
            >
              Features
            </button>
            <button
              onClick={() => scrollTo('docs-section')}
              className="text-text-secondary hover:text-accent-primary transition-colors duration-200 cursor-pointer"
            >
              Documentation
            </button>
          </nav>

          {/* Status Badge */}
          <div className="flex items-center space-x-2 rounded-full border border-success-bg/25 bg-success-bg/5 px-3.5 py-1.5 text-xs font-medium text-success-bg">
            <span className="h-2 w-2 rounded-full bg-success-bg animate-ping" />
            <span>Pipeline Active</span>
          </div>
        </div>
      </div>
    </header>
  );
}
