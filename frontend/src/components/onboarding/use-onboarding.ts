"use client";

import { useState, useCallback } from "react";
import {
  type OnboardingData,
  INITIAL_ONBOARDING_DATA,
  ONBOARDING_STEPS,
} from "@/lib/onboarding-schema";

export function useOnboarding() {
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [data, setData] = useState<OnboardingData>(INITIAL_ONBOARDING_DATA);

  const currentStep =
    currentStepIndex < ONBOARDING_STEPS.length
      ? ONBOARDING_STEPS[currentStepIndex]
      : null;
  const totalSteps = ONBOARDING_STEPS.length;
  const isComplete = currentStepIndex >= totalSteps;

  const updateField = useCallback(
    <K extends keyof OnboardingData>(
      field: K,
      value: OnboardingData[K]
    ) => {
      setData((prev) => ({ ...prev, [field]: value }));
    },
    []
  );

  const nextStep = useCallback(() => {
    if (currentStepIndex < totalSteps) {
      setCurrentStepIndex((prev) => prev + 1);
    }
  }, [currentStepIndex, totalSteps]);

  const prevStep = useCallback(() => {
    if (currentStepIndex > 0) {
      setCurrentStepIndex((prev) => prev - 1);
    }
  }, [currentStepIndex]);

  const skipLabs = useCallback(() => {
    nextStep();
  }, [nextStep]);

  const setLabFile = useCallback((file: File | null) => {
    setData((prev) => ({
      ...prev,
      labPdfFile: file,
    }));
  }, []);

  const canProceed = useCallback(() => {
    const step = currentStep;
    if (!step) return false;

    if (step.id === "lab-upload") {
      return true;
    }

    for (const field of step.fields) {
      if (field === "age" && (data.age === null || data.age === 0)) return false;
      if (field === "sex" && data.sex === null) return false;
      if (field === "height" && (data.height === null || data.height === 0))
        return false;
      if (field === "weight" && (data.weight === null || data.weight === 0))
        return false;
      if (field === "sleepHours" && data.sleepHours === null) return false;
      if (field === "movementDays" && data.movementDays === null) return false;
      if (field === "workActivityLevel" && data.workActivityLevel === null)
        return false;
      if (field === "stressLevel" && data.stressLevel === null) return false;
    }

    return true;
  }, [currentStep, data]);

  return {
    currentStepIndex,
    currentStep,
    totalSteps,
    isComplete,
    data,
    updateField,
    nextStep,
    prevStep,
    skipLabs,
    setLabFile,
    canProceed,
  };
}

