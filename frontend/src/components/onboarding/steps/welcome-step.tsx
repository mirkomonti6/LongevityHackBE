"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import type { GoalOption, OnboardingData } from "@/lib/onboarding-schema";

const GOAL_LABELS: Record<GoalOption, string> = {
  "more-energy": "More energy",
  longevity: "Better long-term health / Longevity",
  "better-sleep": "Better sleep",
  "less-stress": "Less stress",
  "weight-metabolic": "Weight / Metabolic health",
};

interface WelcomeStepProps {
  data: OnboardingData;
  onToggleGoal: (goal: GoalOption) => void;
}

export function WelcomeStep({ data, onToggleGoal }: WelcomeStepProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>What brings you here?</CardTitle>
        <CardDescription>
          Select all goals that are relevant to you.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {(Object.keys(GOAL_LABELS) as GoalOption[]).map((goal) => (
          <div key={goal} className="flex items-center space-x-2">
            <Checkbox
              id={goal}
              checked={data.goals.includes(goal)}
              onCheckedChange={() => onToggleGoal(goal)}
            />
            <Label
              htmlFor={goal}
              className="text-sm font-normal cursor-pointer"
            >
              {GOAL_LABELS[goal]}
            </Label>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}

