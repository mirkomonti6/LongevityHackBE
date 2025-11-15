"use client";

import { useEffect } from "react";
import { Slider } from "@/components/ui/slider";
import type { OnboardingData } from "@/lib/onboarding-schema";

interface StepSleepHoursProps {
  data: OnboardingData;
  onUpdateField: (value: number) => void;
}

export function StepSleepHours({ data, onUpdateField }: StepSleepHoursProps) {
  useEffect(() => {
    if (data.sleepHours === null) {
      onUpdateField(7);
    }
  }, [data.sleepHours, onUpdateField]);

  return (
    <div className="space-y-6">
      <div className="text-center">
        <div className="text-5xl font-bold mb-2">
          {data.sleepHours ?? 7}
        </div>
        <div className="text-lg text-muted-foreground">hours</div>
      </div>
      <Slider
        min={4}
        max={9}
        step={0.5}
        value={[data.sleepHours ?? 7]}
        onValueChange={([value]) => onUpdateField(value)}
        className="w-full"
      />
    </div>
  );
}

