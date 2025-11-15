"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useOnboarding } from "./use-onboarding";
import { FullscreenStep } from "./fullscreen-step";
import { StepAge } from "./steps/step-age";
import { StepSex } from "./steps/step-sex";
import { StepHeight } from "./steps/step-height";
import { StepWeight } from "./steps/step-weight";
import { StepSleepHours } from "./steps/step-sleep-hours";
import { StepMovementDays } from "./steps/step-movement-days";
import { StepWorkActivity } from "./steps/step-work-activity";
import { StepLabUpload } from "./steps/step-lab-upload";
import { StepStress } from "./steps/step-stress";
import { useAppState } from "@/lib/app-state";
import type { Sex, WorkActivityLevel } from "@/lib/onboarding-schema";

export function OnboardingWizard() {
  const router = useRouter();
  const { setOnboardingData } = useAppState();
  const {
    currentStep,
    currentStepIndex,
    totalSteps,
    isComplete,
    data,
    updateField,
    nextStep,
    prevStep,
    skipLabs,
    setLabFile,
    canProceed,
  } = useOnboarding();

  useEffect(() => {
    if (isComplete) {
      setOnboardingData(data);
      router.push("/loading");
    }
  }, [isComplete, data, setOnboardingData, router]);

  if (isComplete) {
    return null;
  }

  const renderStepContent = () => {
    switch (currentStep?.id) {
      case "age":
        return (
          <StepAge
            data={data}
            onUpdateField={(value) => updateField("age", value)}
          />
        );
      case "sex":
        return (
          <StepSex
            data={data}
            onUpdateField={(value) => updateField("sex", value as Sex)}
          />
        );
      case "height":
        return (
          <StepHeight
            data={data}
            onUpdateField={(value) => updateField("height", value)}
          />
        );
      case "weight":
        return (
          <StepWeight
            data={data}
            onUpdateField={(value) => updateField("weight", value)}
          />
        );
      case "sleep-hours":
        return (
          <StepSleepHours
            data={data}
            onUpdateField={(value) => updateField("sleepHours", value)}
          />
        );
      case "movement-days":
        return (
          <StepMovementDays
            data={data}
            onUpdateField={(value) => updateField("movementDays", value)}
          />
        );
      case "work-activity":
        return (
          <StepWorkActivity
            data={data}
            onUpdateField={(value) =>
              updateField("workActivityLevel", value as WorkActivityLevel)
            }
          />
        );
      case "lab-upload":
        return <StepLabUpload data={data} onSetLabFile={setLabFile} />;
      case "stress":
        return (
          <StepStress
            data={data}
            onUpdateField={(value) => updateField("stressLevel", value)}
          />
        );
      default:
        return null;
    }
  };

  return (
    <FullscreenStep
      title={currentStep?.title || ""}
      description={currentStep?.description || ""}
      currentStep={currentStepIndex + 1}
      totalSteps={totalSteps}
      onBack={currentStepIndex > 0 ? prevStep : undefined}
      onNext={nextStep}
      canProceed={canProceed()}
    >
      {renderStepContent()}
    </FullscreenStep>
  );
}
