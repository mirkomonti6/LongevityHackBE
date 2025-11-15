"use client";

import { Button } from "@/components/ui/button";
import type { OnboardingData, Sex } from "@/lib/onboarding-schema";

const SEX_OPTIONS: { value: Sex; label: string }[] = [
  { value: "male", label: "Male" },
  { value: "female", label: "Female" },
  { value: "other", label: "Other" },
  { value: "prefer-not-to-say", label: "Prefer not to say" },
];

interface StepSexProps {
  data: OnboardingData;
  onUpdateField: (value: Sex) => void;
}

export function StepSex({ data, onUpdateField }: StepSexProps) {
  return (
    <div className="space-y-3">
      {SEX_OPTIONS.map((option) => (
        <Button
          key={option.value}
          variant={data.sex === option.value ? "secondary" : "outline"}
          onClick={() => onUpdateField(option.value)}
          className="w-full h-14 text-base justify-start"
        >
          {option.label}
        </Button>
      ))}
    </div>
  );
}

