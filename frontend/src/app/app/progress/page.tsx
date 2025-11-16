'use client';

import * as React from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { useAppState } from '@/lib/app-state';
import { BranchProgress } from '@/components/progress/branch-progress';
import { cn } from '@/lib/utils';

export default function ProgressPage() {
  const { habitStatuses, resolvedHabitPlan } = useAppState();
  const [isPlanted, setIsPlanted] = React.useState(false);
  const [isAnimating, setIsAnimating] = React.useState(false);

  // Use unified streak logic based on habitStatuses and resolvedHabitPlan
  const getStreakData = () => {
    if (resolvedHabitPlan && resolvedHabitPlan.days.length > 0) {
      // Count completed days from the plan
      const completed = resolvedHabitPlan.days.filter((planDay) => {
        const status = habitStatuses.find((s) => s.date === planDay.date);
        return status?.status === 'yes' || status?.status === 'partly';
      }).length;
      return { completed, total: resolvedHabitPlan.days.length };
    }

    // Fallback: use habitStatuses directly
    const last10Statuses = habitStatuses.slice(0, 10);
    const completed = last10Statuses.filter((s) => s.status === 'yes' || s.status === 'partly').length;
    return { completed, total: 10 };
  };

  const { completed, total } = getStreakData();

  // Streak is complete when all plan days are completed
  const isComplete = completed === total;

  const handlePlantTree = () => {
    setIsAnimating(true);
    setTimeout(() => {
      setIsPlanted(true);
      setIsAnimating(false);
    }, 1000); // Animation-Dauer
  };

  // Für Animation - window height nur im Client
  const [windowHeight, setWindowHeight] = React.useState(800);
  React.useEffect(() => {
    if (typeof window !== 'undefined') {
      setWindowHeight(window.innerHeight);
    }
  }, []);

  return (
    <div className="min-h-screen px-6 py-8 pb-24 bg-background relative overflow-hidden">
      {/* Baum im Background (wenn gepflanzt) */}
      <AnimatePresence>
        {isPlanted && (
          <motion.div
            initial={{ opacity: 0, scale: 0.3 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.8, ease: 'easeOut' }}
            className="fixed inset-0 pointer-events-none z-0 flex items-end justify-center"
          >
            <div className="w-full h-full max-w-md mx-auto flex items-end justify-center pb-20">
              {/* Einfacher Baum - kann später erweitert werden */}
              <div className="relative">
                {/* Baumstamm */}
                <div className="w-16 h-48 bg-gradient-to-b from-amber-900 to-amber-950 rounded-t-lg mx-auto" />
                {/* Baumkrone */}
                <div className="absolute -top-20 left-1/2 -translate-x-1/2 w-48 h-48 rounded-full bg-gradient-to-b from-emerald-500 to-emerald-700 opacity-80" />
                <div className="absolute -top-16 left-1/2 -translate-x-1/2 w-40 h-40 rounded-full bg-gradient-to-b from-emerald-400 to-emerald-600 opacity-90" />
                <div className="absolute -top-12 left-1/2 -translate-x-1/2 w-32 h-32 rounded-full bg-gradient-to-b from-emerald-300 to-emerald-500" />
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <div className="max-w-2xl mx-auto space-y-10 relative z-10">
        <div className="space-y-3 text-center">
          <h1 className="text-3xl md:text-4xl font-semibold tracking-tight">
            Progress
          </h1>
          <p className="text-sm text-muted-foreground">
            Your 10-day habit streak visualized as a living health branch.
          </p>
        </div>

        {/* Card mit Animation - klickbar bei 10/10 Streak */}
        <AnimatePresence>
          {!isPlanted && (
            <motion.div
              initial={{ opacity: 1, scale: 1, y: 0 }}
              animate={
                isAnimating
                  ? {
                      opacity: 0,
                      scale: 0.3,
                      y: windowHeight * 0.7,
                      rotate: -5,
                    }
                  : { opacity: 1, scale: 1, y: 0, rotate: 0 }
              }
              exit={{ opacity: 0 }}
              transition={{ duration: 1, ease: 'easeInOut' }}
              className={cn(
                'mb-16 relative z-0',
                isComplete && !isAnimating && 'cursor-pointer'
              )}
              onClick={isComplete && !isAnimating ? handlePlantTree : undefined}
              whileHover={
                isComplete && !isAnimating
                  ? { scale: 1.02, transition: { duration: 0.2 } }
                  : undefined
              }
            >
              <BranchProgress streak={completed} />
            </motion.div>
          )}
        </AnimatePresence>

        {/* Success Message nach dem Pflanzen */}
        {isPlanted && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="text-center space-y-6"
          >
            {/* Grid mit 3 Cards */}
            <div className="flex gap-4 justify-center items-start">
              {/* Card 1: Baum */}
              <motion.div
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.5, type: 'spring', stiffness: 200 }}
              >
                <div className="bg-card border border-border/40 rounded-xl px-3 py-6 shadow-lg w-fit">
                  {/* Animierter Baum – stilisiert wie im Icon, aber lebendig */}
                  <motion.svg
                    width="80"
                    height="80"
                    viewBox="0 0 80 80"
                    xmlns="http://www.w3.org/2000/svg"
                    className="mx-auto"
                    initial={{ scale: 0.95 }}
                    animate={{ scale: [0.95, 1, 0.97, 0.95] }}
                    transition={{ duration: 3.5, repeat: Infinity, ease: 'easeInOut' }}
                  >
                    {/* Baumstamm – einfarbig dunkelbraun */}
                    <path
                      d="M36 50 L34 72 Q38 74 42 72 L40 50 Z"
                      fill="#5A3410"
                    />

                    {/* Kronen-Gruppe mit leichtem „Wackeln" */}
                    <motion.g
                      initial={{ y: 0, rotate: 0 }}
                      animate={{
                        y: [0, -1.5, 0, 1.5, 0],
                        rotate: [0, -1.5, 0, 1.5, 0],
                      }}
                      transition={{
                        duration: 3.5,
                        repeat: Infinity,
                        ease: 'easeInOut',
                      }}
                      style={{ transformOrigin: '40px 34px' }}
                    >
                      {/* Untere Schicht – breite, einheitlich grüne Krone */}
                      <ellipse cx="38" cy="42" rx="18" ry="12" fill="#22c55e" />
                      {/* zusätzliche Blätter unten links/rechts – gleicher Grünton */}
                      <ellipse cx="26" cy="44" rx="8" ry="9" fill="#22c55e" />
                      <ellipse cx="50" cy="44" rx="8" ry="9" fill="#22c55e" />

                      {/* Mittlere Schicht – etwas kleiner, gleiches Grün leicht variiert */}
                      <ellipse cx="30" cy="32" rx="11" ry="10" fill="#16a34a" />
                      <ellipse cx="46" cy="32" rx="11" ry="10" fill="#16a34a" />

                      {/* Obere Schicht – Kuppe, etwas heller aber klar grün */}
                      <ellipse cx="36" cy="22" rx="8" ry="8" fill="#22c55e" />
                      <ellipse cx="42" cy="22" rx="8" ry="8" fill="#22c55e" />
                    </motion.g>
                  </motion.svg>
                </div>
              </motion.div>

              {/* Card 2: Platzhalter */}
              <motion.div
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.6, type: 'spring', stiffness: 200 }}
              >
                <div className="bg-card border border-border/40 rounded-xl px-3 py-6 shadow-lg w-fit">
                  <div className="w-20 h-20 flex items-center justify-center">
                    <div className="w-12 h-12 rounded-full border-2 border-dashed border-muted-foreground/30 flex items-center justify-center">
                      <span className="text-2xl text-muted-foreground/40">🌱</span>
                    </div>
                  </div>
                </div>
              </motion.div>

              {/* Card 3: Platzhalter */}
              <motion.div
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.7, type: 'spring', stiffness: 200 }}
              >
                <div className="bg-card border border-border/40 rounded-xl px-3 py-6 shadow-lg w-fit">
                  <div className="w-20 h-20 flex items-center justify-center">
                    <div className="w-12 h-12 rounded-full border-2 border-dashed border-muted-foreground/30 flex items-center justify-center">
                      <span className="text-2xl text-muted-foreground/40">🌱</span>
                    </div>
                  </div>
                </div>
              </motion.div>
            </div>

            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.7 }}
              className="space-y-3"
            >
              <h2 className="text-2xl font-semibold text-emerald-600">
                Tree Planted!
              </h2>
              <p className="text-muted-foreground">
                Your 10-day streak has grown into a beautiful tree. Keep going to
                grow your forest!
              </p>
            </motion.div>
          </motion.div>
        )}
      </div>
    </div>
  );
}

