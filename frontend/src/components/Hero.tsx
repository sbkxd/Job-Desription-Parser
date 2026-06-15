'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { Brain, Star, ArrowDown } from 'lucide-react';

export default function Hero() {
  const containerVariants = {
    hidden: { opacity: 0, y: 30 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.8,
        staggerChildren: 0.2
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.6 } }
  };

  return (
    <div className="relative overflow-hidden py-20 lg:py-32 grid-bg">
      {/* Absolute glow balls */}
      <div className="absolute top-1/4 left-1/2 -z-10 h-72 w-72 -translate-x-1/2 -translate-y-1/2 rounded-full bg-accent-primary/10 blur-[120px] glow-primary" />
      <div className="absolute top-1/3 left-1/3 -z-10 h-96 w-96 -translate-x-1/2 -translate-y-1/2 rounded-full bg-accent-secondary/10 blur-[150px] glow-secondary" />

      <div className="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8 text-center">
        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate="visible"
          className="flex flex-col items-center space-y-6"
        >
          {/* Badge */}
          <motion.div
            variants={itemVariants}
            className="inline-flex items-center space-x-2 rounded-full border border-accent-primary/30 bg-accent-primary/5 px-4 py-1.5 text-xs font-mono font-medium tracking-wide text-accent-primary"
          >
            <Brain className="h-3.5 w-3.5" />
            <span>AI-POWERED ORCHESTRATION PIPELINE</span>
          </motion.div>

          {/* Heading */}
          <motion.h1
            variants={itemVariants}
            className="font-sans text-4xl font-extrabold tracking-tight text-white sm:text-6xl md:text-7xl leading-tight"
          >
            Transform Job Descriptions Into{' '}
            <span className="bg-gradient-to-r from-accent-primary via-[#4DEEEA] to-accent-secondary bg-clip-text text-transparent">
              Structured Skill Intelligence
            </span>
          </motion.h1>

          {/* Subheading */}
          <motion.p
            variants={itemVariants}
            className="mx-auto max-w-2xl text-base text-text-secondary sm:text-lg md:text-xl"
          >
            Extract skills, experience requirements, seniority, qualifications, and normalized ESCO taxonomy mappings using AI-powered analysis.
          </motion.p>

          {/* Call to Action scroll indicator */}
          <motion.div
            variants={itemVariants}
            className="pt-6"
          >
            <button
              onClick={() => {
                document.getElementById('analyze-section')?.scrollIntoView({ behavior: 'smooth' });
              }}
              className="group flex items-center space-x-2 rounded-full bg-zinc-900 border border-zinc-800 hover:border-accent-primary/50 text-white font-medium text-sm px-6 py-3 shadow-lg shadow-black/40 hover:shadow-accent-primary/10 transition-all duration-300 cursor-pointer"
            >
              <span>Get Started</span>
              <ArrowDown className="h-4 w-4 text-accent-primary group-hover:translate-y-1 transition-transform duration-300" />
            </button>
          </motion.div>
        </motion.div>
      </div>
    </div>
  );
}
