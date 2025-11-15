"use client";

import { Button } from "@/components/ui/button";
import type { AgeRange, OnboardingData } from "@/lib/onboarding-schema";

const AGE_RANGES: { value: AgeRange; label: string }[] = [
  { value: "18-25", label: "18-25" },
  { value: "26-35", label: "26-35" },
  { value: "36-45", label: "36-45" },
  { value: "46-55", label: "46-55" },
  { value: "56-65", label: "56-65" },
  { value: "65+", label: "65+" },
];

interface StepAgeRangeProps {
  data: OnboardingData;
  onUpdateField: (value: AgeRange) => void;
}

export function StepAgeRange({ data, onUpdateField }: StepAgeRangeProps) {
  return (
    <div className="grid grid-cols-2 gap-3">
      {AGE_RANGES.map((range) => (
        <Button
          key={range.value}
          variant={data.ageRange === range.value ? "default" : "outline"}
          onClick={() => onUpdateField(range.value)}
          className="h-14 text-base"
        >
          {range.label}
        </Button>
      ))}
    </div>
  );
}

