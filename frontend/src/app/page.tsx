'use client';

import React from 'react';
import Header from '../components/Header';
import Hero from '../components/Hero';
import InputSection from '../components/InputSection';
import PipelineVisualizer from '../components/PipelineVisualizer';
import ResultsDashboard from '../components/ResultsDashboard';
import Footer from '../components/Footer';

export default function Home() {
  return (
    <div className="flex min-h-screen flex-col bg-background text-text-primary">
      {/* Dynamic Grid Overlay */}
      <div className="fixed inset-0 -z-20 grid-bg opacity-30 pointer-events-none" />

      {/* Header Navigation */}
      <Header />

      <main className="flex-1 pb-16">
        {/* Decorative Hero Panel */}
        <Hero />

        {/* Input Panel Card */}
        <div className="relative z-10 -mt-16">
          <InputSection />
        </div>

        {/* Live LangGraph Progress Animation */}
        <PipelineVisualizer />

        {/* Final Report Dashboard */}
        <ResultsDashboard />

        {/* Core Features Overview Section (Required navigation anchors) */}
        <section id="features-section" className="mx-auto max-w-5xl px-4 py-16 border-t border-border-dark scroll-mt-20">
          <div className="text-center space-y-4 mb-12">
            <span className="text-xs font-mono text-accent-secondary uppercase font-semibold">Engine Features</span>
            <h3 className="text-2xl sm:text-3xl font-extrabold text-white">Full Stack Deep Skill Mining</h3>
            <p className="mx-auto max-w-xl text-sm text-text-secondary">
              Extract, audit, and normalize unstructured requirements at scale.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="rounded-xl border border-border-dark bg-[#111113]/40 p-6 space-y-3">
              <span className="inline-flex h-8 w-8 items-center justify-center rounded-lg bg-accent-primary/10 text-accent-primary font-mono text-xs">01</span>
              <h4 className="font-bold text-white text-sm">Ingestion Pipeline</h4>
              <p className="text-xs text-text-secondary leading-relaxed">
                Asynchronous headless fetching with Playwright or file scraping support for PDFs.
              </p>
            </div>
            <div className="rounded-xl border border-border-dark bg-[#111113]/40 p-6 space-y-3">
              <span className="inline-flex h-8 w-8 items-center justify-center rounded-lg bg-accent-secondary/10 text-accent-secondary font-mono text-xs">02</span>
              <h4 className="font-bold text-white text-sm">ESCO Matching Cascade</h4>
              <p className="text-xs text-text-secondary leading-relaxed">
                Vector embeddings mapping extracted strings directly to the official European Skills/Occupations taxonomy.
              </p>
            </div>
            <div className="rounded-xl border border-border-dark bg-[#111113]/40 p-6 space-y-3">
              <span className="inline-flex h-8 w-8 items-center justify-center rounded-lg bg-success-bg/10 text-success-bg font-mono text-xs">03</span>
              <h4 className="font-bold text-white text-sm">Confidence & Quality Queue</h4>
              <p className="text-xs text-text-secondary leading-relaxed">
                Mistral validation for low-confidence skills with automatic flags for human audit queues.
              </p>
            </div>
          </div>
        </section>

        {/* Documentation Section (Required navigation anchors) */}
        <section id="docs-section" className="mx-auto max-w-5xl px-4 py-16 border-t border-border-dark scroll-mt-20">
          <div className="rounded-xl border border-border-dark bg-gradient-to-r from-accent-primary/5 via-accent-secondary/5 to-transparent p-8 space-y-4">
            <h3 className="text-xl font-bold text-white">Need detailed system references?</h3>
            <p className="text-xs text-text-secondary max-w-2xl">
              Learn about our REST endpoints, LangGraph StateGraph configurations, and NLP model setup. Read the generated markdown files under the `docs/` folder in the project workspace.
            </p>
          </div>
        </section>
      </main>

      {/* Footer Details */}
      <Footer />
    </div>
  );
}
