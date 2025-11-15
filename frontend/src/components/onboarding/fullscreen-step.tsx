"use client";

import { Button } from "@/components/ui/button";
import type { ReactNode } from "react";

interface FullscreenStepProps {
  title: string;
  description: string;
  currentStep: number;
  totalSteps: number;
  onBack?: () => void;
  onNext: () => void;
  canProceed: boolean;
  showSkip?: boolean;
  onSkip?: () => void;
  children: ReactNode;
}

export function FullscreenStep({
  title,
  description,
  currentStep,
  totalSteps,
  onBack,
  onNext,
  canProceed,
  showSkip = false,
  onSkip,
  children,
}: FullscreenStepProps) {
  return (
    <div className="fixed inset-0 flex flex-col bg-background overflow-y-auto">
      <div className="flex-1 flex flex-col items-center justify-center px-6 py-12 min-h-screen">
        <div className="w-full max-w-md space-y-8">
          <div className="space-y-4 text-center">
            <h1 className="text-3xl md:text-4xl font-bold leading-tight">
              {title}
            </h1>
            {description && (
              <p className="text-base md:text-lg text-muted-foreground">
                {description}
              </p>
            )}
          </div>

          <div className="pt-4">{children}</div>
        </div>
      </div>

      <div className="sticky bottom-0 bg-background border-t pt-4 pb-6 px-6">
        <div className="max-w-md mx-auto flex gap-3">
          {onBack && (
            <Button
              variant="outline"
              onClick={onBack}
              className="flex-1 h-12 text-base"
            >
              Back
            </Button>
          )}
          {showSkip && onSkip && (
            <Button
              variant="ghost"
              onClick={onSkip}
              className="h-12 text-base"
            >
              Skip
            </Button>
          )}
          <Button
            onClick={onNext}
            disabled={!canProceed}
            className="flex-1 h-12 text-base font-semibold"
          >
            {currentStep === totalSteps ? "Complete" : "Next"}
          </Button>
        </div>
      </div>
    </div>
  );
}

