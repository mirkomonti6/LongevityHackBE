"use client";

import { Button } from "@/components/ui/button";
import type { OnboardingData, WorkActivityLevel } from "@/lib/onboarding-schema";

const WORK_ACTIVITY_LEVELS: { value: WorkActivityLevel; label: string }[] = [
  { value: "sedentary", label: "Sedentary" },
  { value: "light", label: "Light activity" },
  { value: "moderate", label: "Moderate activity" },
  { value: "active", label: "Active" },
];

interface StepWorkActivityProps {
  data: OnboardingData;
  onUpdateField: (value: WorkActivityLevel) => void;
}

export function StepWorkActivity({
  data,
  onUpdateField,
}: StepWorkActivityProps) {
  return (
    <div className="space-y-3">
      {WORK_ACTIVITY_LEVELS.map((level) => (
        <Button
          key={level.value}
          variant={data.workActivityLevel === level.value ? "secondary" : "outline"}
          onClick={() => onUpdateField(level.value)}
          className="w-full h-14 text-base justify-start"
        >
          {level.label}
        </Button>
      ))}
    </div>
  );
}

