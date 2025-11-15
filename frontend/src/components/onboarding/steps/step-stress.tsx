"use client";

import { useEffect } from "react";
import { Slider } from "@/components/ui/slider";
import type { OnboardingData } from "@/lib/onboarding-schema";

interface StepStressProps {
  data: OnboardingData;
  onUpdateField: (value: number) => void;
}

export function StepStress({ data, onUpdateField }: StepStressProps) {
  useEffect(() => {
    if (data.stressLevel === null) {
      onUpdateField(5);
    }
  }, [data.stressLevel, onUpdateField]);

  return (
    <div className="space-y-6">
      <div className="text-center">
        <div className="text-5xl font-bold mb-2">
          {data.stressLevel ?? 5}
        </div>
        <div className="text-lg text-muted-foreground">out of 10</div>
      </div>
      <Slider
        min={1}
        max={10}
        step={1}
        value={[data.stressLevel ?? 5]}
        onValueChange={([value]) => onUpdateField(value)}
        className="w-full"
      />
      <div className="flex justify-between text-xs text-muted-foreground px-1">
        <span>Not stressed</span>
        <span>Very stressed</span>
      </div>
    </div>
  );
}

