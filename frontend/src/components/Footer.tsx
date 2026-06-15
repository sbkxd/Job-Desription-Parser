'use client';

import React from 'react';
import { Globe, Database, Zap, Cpu } from 'lucide-react';

export default function Footer() {
  return (
    <footer className="mt-auto border-t border-border-dark bg-[#0a0a0c] py-8 text-xs text-text-secondary">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col space-y-6 md:flex-row md:items-center md:justify-between md:space-y-0">
          {/* Logo & Credits */}
          <div className="flex flex-col space-y-2">
            <div className="flex items-center space-x-2">
              <Cpu className="h-4 w-4 text-accent-primary" />
              <span className="font-semibold text-white">JD Skill Intelligence Platform</span>
            </div>
            <p className="text-zinc-500">
              © {new Date().getFullYear()} Altrosyn. Powered by Mistral AI, LangGraph, and ESCO Taxonomy.
            </p>
          </div>

          {/* Engine Specs */}
          <div className="flex flex-wrap gap-4 text-2xs font-mono text-zinc-500">
            <div className="flex items-center space-x-1 border border-border-dark bg-[#111113] px-2 py-1 rounded">
              <Database className="h-3 w-3 text-accent-secondary" />
              <span>PostgreSQL + Alembic</span>
            </div>
            <div className="flex items-center space-x-1 border border-border-dark bg-[#111113] px-2 py-1 rounded">
              <Zap className="h-3 w-3 text-accent-primary" />
              <span>LangGraph Orchestrator</span>
            </div>
            <div className="flex items-center space-x-1 border border-border-dark bg-[#111113] px-2 py-1 rounded">
              <span>Mistral-Small-Latest</span>
            </div>
          </div>

          {/* Links */}
          <div className="flex space-x-6">
            <a
              href="https://github.com"
              target="_blank"
              rel="noopener noreferrer"
              className="hover:text-white transition-colors duration-200"
            >
              <Globe className="h-4 w-4" />
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
}
