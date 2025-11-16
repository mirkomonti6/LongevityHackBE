'use client';

/**
 * Large central branch visualization for the Progress page.
 *
 * - Does NOT touch any streak logic – it just takes a numeric streak (0–10)
 * - For each completed day (up to 10) we render one leaf on the branch
 * - As streak grows, more leaves appear along the branch
 * - Modern, clean, "health tech" aesthetic (no emojis)
 */

import * as React from 'react';
import { motion } from 'motion/react';

import { cn } from '@/lib/utils';

type BranchProgressProps = {
  /** Current streak, 0–10 (we’ll clamp inside just to be safe) */
  streak: number;
  className?: string;
};

type LeafPoint = {
  x: number; // percentage (0–100) of container width
  y: number; // percentage (0–100) of container height
  angle: number; // rotation angle in degrees for natural hanging
};

// Blattpositionen GENAU an den ZWEIGEN, nicht am Hauptast!
// Zweige: 
// 1. Linker Zweig unten: 20,78 → 14,70
// 2. Zweig unten rechts: 30,68 → 24,60
// 3. Zweig links oben: 42,58 → 36,48
// 4. Zweig mittig rechts: 55,50 → 64,42
// 5. Zweig rechts oben: 65,42 → 78,34
// 6. Kleiner Zweig oben rechts: 75,32 → 86,24
const LEAF_POINTS: LeafPoint[] = [
  // Blatt 1: Am linken Zweig unten (20,78 → 14,70), etwas weiter links - umgedreht
  { x: 15, y: 74, angle: 115 },
  
  // Blatt 2: Am linken Zweig unten, weiter unten und links - umgedreht
  { x: 13, y: 72, angle: 130 },
  
  // Blatt 3: Am Zweig unten rechts (30,68 → 24,60), etwas weiter links - umgedreht, stark nach links gedreht
  { x: 25, y: 64, angle: 110 },
  
  // Blatt 4: Am Zweig unten rechts, weiter unten und links - umgedreht, stark nach links gedreht
  { x: 23, y: 62, angle: 120 },
  
  // Blatt 5: Am Zweig links oben (42,58 → 36,48), etwas weiter links - umgedreht
  { x: 37, y: 53, angle: 160 },
  
  // Blatt 6: Am Zweig links oben, weiter oben und links - umgedreht
  { x: 35, y: 51, angle: 168 },
  
  // Blatt 7: Am Zweig mittig rechts (55,50 → 64,42), weiter unten und links
  { x: 58, y: 50, angle: 12 },
  
  // Blatt 8: Am Zweig rechts oben (65,42 → 78,34), weiter rechts
  { x: 74, y: 38, angle: 22 },
  
  // Blatt 9: Am Zweig rechts oben, weiter oben und rechts - stark nach links gedreht
  { x: 77, y: 36, angle: -15 },
  
  // Blatt 10: Am kleinen Zweig oben rechts (75,32 → 86,24), an der Spitze
  { x: 84, y: 26, angle: 3 },
];

function LeafIcon({ index, level }: { index: number; level: number }) {
  // Level ~ streak intensity (1–10) → size & color
  const baseSize = 28; // Größer für realistischere Blätter
  const size = baseSize + (level - 1) * 4; // 28–64px

  const brightness = 0.5 + level * 0.05; // 0.5–1.0
  const mainColor = level >= 8 ? '#22c55e' : level >= 5 ? '#84cc16' : '#a3e635';
  const highlightColor = level >= 8 ? '#86efac' : level >= 5 ? '#d9f99d' : '#ecfccb';

  const width = size;
  const height = size * 1.6; // Ovaler, länglicher

  return (
    <motion.div
      initial={{ scale: 0.3, opacity: 0, y: 10 }}
      animate={{ scale: 1, opacity: 1, y: 0 }}
      transition={{
        delay: 1.5 + index * 0.15, // Nach dem Ast (1.4s) + nacheinander
        type: 'spring',
        stiffness: 200,
        damping: 18,
      }}
      className="relative flex items-center justify-center"
      style={{ width: width, height: height }}
    >
      {/* Soft glow halo */}
      <div
        className="absolute rounded-full blur-md"
        style={{
          width: width * 1.5,
          height: width * 1.5,
          opacity: brightness * 0.45,
          background: 'radial-gradient(circle, rgba(34,197,94,0.8), transparent)',
        }}
      />

      {/* Leaf body (SVG für realistischere Form) */}
      <svg
        width={width}
        height={height}
        viewBox="0 0 100 160"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className="drop-shadow-lg"
        style={{
          filter: level >= 7 ? `drop-shadow(0 0 ${brightness * 8}px rgba(34, 197, 94, 0.6))` : `drop-shadow(0 2px 4px rgba(0,0,0,0.2))`,
          display: 'block',
        }}
      >
        <defs>
          <linearGradient id={`leaf-grad-${index}`} x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor={highlightColor} />
            <stop offset="40%" stopColor={mainColor} />
            <stop offset="100%" stopColor="#15803d" />
          </linearGradient>
        </defs>

        {/* Haupt-Blattform - oval, spitz zulaufend */}
        <path
          d="M50 4
             C 78 18, 96 52, 64 110
             C 55 128, 47 138, 40 132
             C 10 108, 6 66, 24 36
             C 32 22, 40 12, 50 4 Z"
          fill={`url(#leaf-grad-${index})`}
          fillOpacity={brightness}
        />
        {/* Mittelrippe */}
        <path
          d="M50 4 L50 132"
          stroke="#166534"
          strokeWidth="4"
          strokeLinecap="round"
          strokeOpacity={brightness * 0.7}
        />
        {/* Seitenadern (links) */}
        <path
          d="M50 20 L30 40 M50 40 L20 60 M50 60 L15 80"
          stroke="#166534"
          strokeWidth="2"
          strokeLinecap="round"
          strokeOpacity={brightness * 0.6}
        />
        {/* Seitenadern (rechts) */}
        <path
          d="M50 20 L70 40 M50 40 L80 60 M50 60 L85 80"
          stroke="#166534"
          strokeWidth="2"
          strokeLinecap="round"
          strokeOpacity={brightness * 0.6}
        />
      </svg>
    </motion.div>
  );
}

export function BranchProgress({ streak, className }: BranchProgressProps) {
  const clamped = Math.max(0, Math.min(streak, 10));
  const leafCount = clamped;

  return (
    <div
      className={cn(
        'relative w-full max-w-xl mx-auto aspect-[3/4]',
        'rounded-3xl border border-border/40',
        'bg-gradient-to-b from-slate-900 via-slate-950 to-slate-900',
        'shadow-[0_40px_120px_rgba(15,23,42,0.8)] overflow-hidden',
        className,
      )}
    >
      {/* Subtle background grid / tech feel */}
      <div className="pointer-events-none absolute inset-0 opacity-[0.2]">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_top,_rgba(34,197,94,0.12),_transparent_55%)]" />
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_bottom,_rgba(59,130,246,0.18),_transparent_60%)]" />
        <div className="absolute inset-0 bg-[linear-gradient(to_right,rgba(148,163,184,0.18)_1px,transparent_1px)] bg-[length:32px_32px]" />
        <div className="absolute inset-0 bg-[linear-gradient(to_bottom,rgba(148,163,184,0.14)_1px,transparent_1px)] bg-[length:32px_32px]" />
      </div>

      {/* Branch (SVG) - diagonal von unten links nach oben rechts wie im Bild */}
      <motion.svg
        className="absolute inset-0 w-full h-full"
        viewBox="0 0 100 100"
        preserveAspectRatio="none"
      >
        {/* Hauptast - diagonal von unten links (10, 85) nach oben rechts (88, 12) */}
        <motion.path
          d="M 10 85 Q 25 70, 40 58 Q 55 46, 70 36 Q 80 28, 88 12"
          stroke="#3d2817"
          strokeWidth={2.5}
          strokeLinecap="round"
          fill="none"
          initial={{ pathLength: 0, opacity: 0 }}
          animate={{ pathLength: 1, opacity: 0.95 }}
          transition={{ duration: 1.4, ease: 'easeInOut' }}
        />

        {/* Dünne Highlight-Linie für Glanz-Effekt */}
        <motion.path
          d="M 10 85 Q 25 70, 40 58 Q 55 46, 70 36 Q 80 28, 88 12"
          stroke="rgba(248,250,252,0.18)"
          strokeWidth={1}
          strokeLinecap="round"
          fill="none"
          initial={{ pathLength: 0, opacity: 0 }}
          animate={{ pathLength: 1, opacity: 0.7 }}
          transition={{ duration: 1.6, delay: 0.1, ease: 'easeInOut' }}
        />

        {/* Kleine Zweige vom Hauptast abzweigend */}
        {/* Linker Zweig unten */}
        <motion.path
          d="M 20 78 Q 16 74, 14 70"
          stroke="#3d2817"
          strokeWidth={1.6}
          strokeLinecap="round"
          fill="none"
          initial={{ pathLength: 0, opacity: 0 }}
          animate={{ pathLength: 1, opacity: 0.9 }}
          transition={{ duration: 1.0, delay: 0.5, ease: 'easeInOut' }}
        />
        
        {/* Zweig links oben */}
        <motion.path
          d="M 42 58 Q 38 52, 36 48"
          stroke="#3d2817"
          strokeWidth={1.4}
          strokeLinecap="round"
          fill="none"
          initial={{ pathLength: 0, opacity: 0 }}
          animate={{ pathLength: 1, opacity: 0.9 }}
          transition={{ duration: 1.0, delay: 0.7, ease: 'easeInOut' }}
        />
        
        {/* Zweig rechts oben */}
        <motion.path
          d="M 65 42 Q 72 38, 78 34"
          stroke="#3d2817"
          strokeWidth={1.3}
          strokeLinecap="round"
          fill="none"
          initial={{ pathLength: 0, opacity: 0 }}
          animate={{ pathLength: 1, opacity: 0.9 }}
          transition={{ duration: 1.0, delay: 0.9, ease: 'easeInOut' }}
        />
        
        {/* Kleiner Zweig oben rechts */}
        <motion.path
          d="M 75 32 Q 82 28, 86 24"
          stroke="#3d2817"
          strokeWidth={1.2}
          strokeLinecap="round"
          fill="none"
          initial={{ pathLength: 0, opacity: 0 }}
          animate={{ pathLength: 1, opacity: 0.85 }}
          transition={{ duration: 0.9, delay: 1.1, ease: 'easeInOut' }}
        />
        
        {/* Zusätzliche kleine Zweige für mehr Blätter */}
        {/* Zweig mittig rechts */}
        <motion.path
          d="M 55 50 Q 60 45, 64 42"
          stroke="#3d2817"
          strokeWidth={1.3}
          strokeLinecap="round"
          fill="none"
          initial={{ pathLength: 0, opacity: 0 }}
          animate={{ pathLength: 1, opacity: 0.85 }}
          transition={{ duration: 0.9, delay: 0.8, ease: 'easeInOut' }}
        />
        
        {/* Zweig unten rechts */}
        <motion.path
          d="M 30 68 Q 26 64, 24 60"
          stroke="#3d2817"
          strokeWidth={1.4}
          strokeLinecap="round"
          fill="none"
          initial={{ pathLength: 0, opacity: 0 }}
          animate={{ pathLength: 1, opacity: 0.85 }}
          transition={{ duration: 0.9, delay: 0.6, ease: 'easeInOut' }}
        />
      </motion.svg>

      {/* Leaves - natürlich am Ast hängend mit verschiedenen Winkeln */}
      {leafCount > 0 && (
        <div className="absolute inset-0">
          {LEAF_POINTS.slice(0, leafCount).map((point, index) => (
            <div
              key={`leaf-${index}`}
              className="absolute"
              style={{
                left: `${point.x}%`,
                top: `${point.y}%`,
                transform: `translate(-50%, -50%) rotate(${point.angle}deg)`,
                transformOrigin: '50% 20%', // Blatt hängt von oben
              }}
            >
              <LeafIcon index={index} level={index + 1} />
            </div>
          ))}
        </div>
      )}

      {/* Center label overlay (keine z-index, damit Footer darüber liegen kann) */}
      <div className="relative h-full flex flex-col items-center justify-between py-8 pointer-events-none">
        <div className="flex flex-col items-center gap-2">
          <p className="text-xs uppercase tracking-[0.2em] text-slate-400">
            Longevity Streak
          </p>
          <div className="flex items-baseline gap-2">
            <span className="text-4xl font-semibold text-slate-50">
              {clamped}
            </span>
            <span className="text-sm text-slate-400">/ 10 days</span>
          </div>
          <p className="text-xs text-slate-400 max-w-xs text-center">
            Each completed day grows a new leaf on your branch. Keep going to
            see your health landscape flourish.
          </p>
        </div>

        {/* Small progress bar at bottom for a subtle, numeric reference */}
        <div className="w-3/4">
          <div className="h-1.5 w-full rounded-full bg-slate-800/80 overflow-hidden">
            <motion.div
              className="h-full rounded-full bg-gradient-to-r from-emerald-400 via-lime-400 to-emerald-300"
              initial={{ width: 0 }}
              animate={{ width: `${(clamped / 10) * 100}%` }}
              transition={{ duration: 0.8, ease: 'easeOut' }}
            />
          </div>
        </div>
      </div>
    </div>
  );
}


