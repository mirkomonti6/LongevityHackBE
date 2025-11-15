"use client";

import { Button } from "@/components/ui/button";
import type { GoalOption, OnboardingData } from "@/lib/onboarding-schema";

const GOAL_LABELS: Record<GoalOption, string> = {
  "more-energy": "More energy",
  longevity: "Better long-term health",
  "better-sleep": "Better sleep",
  "less-stress": "Less stress",
  "weight-metabolic": "Weight / Metabolic health",
};

interface StepGoalProps {
  data: OnboardingData;
  onToggleGoal: (goal: GoalOption) => void;
}

export function StepGoal({ data, onToggleGoal }: StepGoalProps) {
  return (
    <div className="space-y-3">
      {(Object.keys(GOAL_LABELS) as GoalOption[]).map((goal) => (
        <Button
          key={goal}
          variant={data.goals.includes(goal) ? "default" : "outline"}
          onClick={() => onToggleGoal(goal)}
          className="w-full h-14 text-base justify-start"
        >
          {GOAL_LABELS[goal]}
        </Button>
      ))}
    </div>
  );
}

