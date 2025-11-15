"use client";

import { useEffect } from "react";
import { Slider } from "@/components/ui/slider";
import type { OnboardingData } from "@/lib/onboarding-schema";

interface StepMovementDaysProps {
  data: OnboardingData;
  onUpdateField: (value: number) => void;
}

export function StepMovementDays({
  data,
  onUpdateField,
}: StepMovementDaysProps) {
  useEffect(() => {
    if (data.movementDays === null) {
      onUpdateField(3);
    }
  }, [data.movementDays, onUpdateField]);

  return (
    <div className="space-y-6">
      <div className="text-center">
        <div className="text-5xl font-bold mb-2">
          {data.movementDays ?? 3}
        </div>
        <div className="text-lg text-muted-foreground">days per week</div>
      </div>
      <Slider
        min={0}
        max={7}
        step={1}
        value={[data.movementDays ?? 3]}
        onValueChange={([value]) => onUpdateField(value)}
        className="w-full"
      />
    </div>
  );
}

