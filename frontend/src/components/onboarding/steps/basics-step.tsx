"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Checkbox } from "@/components/ui/checkbox";
import type { OnboardingData, Sex, MedicalCondition } from "@/lib/onboarding-schema";

const SEX_OPTIONS: { value: Sex; label: string }[] = [
  { value: "male", label: "Male" },
  { value: "female", label: "Female" },
  { value: "other", label: "Other" },
  { value: "prefer-not-to-say", label: "Prefer not to say" },
];

const MEDICAL_CONDITIONS: { value: MedicalCondition; label: string }[] = [
  { value: "diabetes", label: "Diabetes" },
  { value: "heart-disease", label: "Heart disease" },
  { value: "hypertension", label: "Hypertension" },
  { value: "none", label: "None" },
];

interface BasicsStepProps {
  data: OnboardingData;
  onUpdateField: <K extends keyof OnboardingData>(
    field: K,
    value: OnboardingData[K]
  ) => void;
  onToggleMedicalCondition: (condition: MedicalCondition) => void;
}

export function BasicsStep({
  data,
  onUpdateField,
  onToggleMedicalCondition,
}: BasicsStepProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Basics</CardTitle>
        <CardDescription>
          Tell us about yourself. This data helps us provide appropriate
          recommendations.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label htmlFor="age">Age</Label>
            <Input
              id="age"
              type="number"
              min="18"
              max="120"
              placeholder="e.g. 35"
              value={data.age ?? ""}
              onChange={(e) =>
                onUpdateField("age", e.target.value ? Number(e.target.value) : null)
              }
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="sex">Sex</Label>
            <RadioGroup
              value={data.sex ?? ""}
              onValueChange={(value) => onUpdateField("sex", value as Sex)}
            >
              {SEX_OPTIONS.map((option) => (
                <div key={option.value} className="flex items-center space-x-2">
                  <RadioGroupItem value={option.value} id={option.value} />
                  <Label htmlFor={option.value} className="font-normal">
                    {option.label}
                  </Label>
                </div>
              ))}
            </RadioGroup>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label htmlFor="height">Height (cm)</Label>
            <Input
              id="height"
              type="number"
              min="100"
              max="250"
              placeholder="e.g. 175"
              value={data.height ?? ""}
              onChange={(e) =>
                onUpdateField(
                  "height",
                  e.target.value ? Number(e.target.value) : null
                )
              }
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="weight">Weight (kg)</Label>
            <Input
              id="weight"
              type="number"
              min="30"
              max="300"
              placeholder="e.g. 75"
              value={data.weight ?? ""}
              onChange={(e) =>
                onUpdateField(
                  "weight",
                  e.target.value ? Number(e.target.value) : null
                )
              }
            />
          </div>
        </div>

        <div className="space-y-3">
          <Label>Do you have any of these diagnosed conditions?</Label>
          <p className="text-xs text-muted-foreground">
            This app is not medical advice. Always talk to your doctor.
          </p>
          <div className="space-y-2">
            {MEDICAL_CONDITIONS.map((condition) => (
              <div key={condition.value} className="flex items-center space-x-2">
                <Checkbox
                  id={condition.value}
                  checked={data.medicalConditions.includes(condition.value)}
                  onCheckedChange={() => onToggleMedicalCondition(condition.value)}
                />
                <Label
                  htmlFor={condition.value}
                  className="text-sm font-normal cursor-pointer"
                >
                  {condition.label}
                </Label>
              </div>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

