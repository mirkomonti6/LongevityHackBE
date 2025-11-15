"use client";

import { Input } from "@/components/ui/input";
import type { OnboardingData } from "@/lib/onboarding-schema";

interface StepAgeProps {
  data: OnboardingData;
  onUpdateField: (value: number) => void;
}

export function StepAge({ data, onUpdateField }: StepAgeProps) {
  return (
    <div className="space-y-6">
      <Input
        type="number"
        min="18"
        max="120"
        placeholder="Enter your age"
        value={data.age ?? ""}
        onChange={(e) =>
          onUpdateField(e.target.value ? Number(e.target.value) : 0)
        }
        className="h-auto text-3xl md:text-4xl text-center font-bold border-0 bg-transparent focus-visible:ring-0 focus-visible:ring-offset-0 shadow-none py-8 [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
        autoFocus
      />
      <div className="text-center text-3xl md:text-4xl font-bold">years</div>
    </div>
  );
}

