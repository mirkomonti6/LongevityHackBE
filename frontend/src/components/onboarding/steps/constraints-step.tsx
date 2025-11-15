"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import type { OnboardingData, TimeInvestment } from "@/lib/onboarding-schema";

const TIME_INVESTMENT_OPTIONS: { value: TimeInvestment; label: string }[] = [
  { value: "5", label: "5 minutes" },
  { value: "10", label: "10 minutes" },
  { value: "15", label: "15 minutes" },
  { value: "20+", label: "20+ minutes" },
];

interface ConstraintsStepProps {
  data: OnboardingData;
  onUpdateNestedField: <K extends keyof OnboardingData["constraints"]>(
    field: K,
    value: boolean
  ) => void;
  onUpdateField: <K extends keyof OnboardingData>(
    field: K,
    value: OnboardingData[K]
  ) => void;
}

export function ConstraintsStep({
  data,
  onUpdateNestedField,
  onUpdateField,
}: ConstraintsStepProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Constraints & Preferences</CardTitle>
        <CardDescription>
          What's currently not possible for you? This helps us provide realistic
          recommendations.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="space-y-3">
          <Label>Which of these are hard limits for you right now?</Label>
          <div className="space-y-2">
            <div className="flex items-center space-x-2">
              <Checkbox
                id="no-gym"
                checked={data.constraints.noGym}
                onCheckedChange={(checked) =>
                  onUpdateNestedField("noGym", checked === true)
                }
              />
              <Label htmlFor="no-gym" className="text-sm font-normal cursor-pointer">
                I can't go to a gym
              </Label>
            </div>
            <div className="flex items-center space-x-2">
              <Checkbox
                id="no-diet-change"
                checked={data.constraints.noDietChange}
                onCheckedChange={(checked) =>
                  onUpdateNestedField("noDietChange", checked === true)
                }
              />
              <Label
                htmlFor="no-diet-change"
                className="text-sm font-normal cursor-pointer"
              >
                I can't change my diet a lot
              </Label>
            </div>
            <div className="flex items-center space-x-2">
              <Checkbox
                id="no-early-bedtime"
                checked={data.constraints.noEarlyBedtime}
                onCheckedChange={(checked) =>
                  onUpdateNestedField("noEarlyBedtime", checked === true)
                }
              />
              <Label
                htmlFor="no-early-bedtime"
                className="text-sm font-normal cursor-pointer"
              >
                I can't go to bed before 23:00
              </Label>
            </div>
            <div className="flex items-center space-x-2">
              <Checkbox
                id="no-meditation"
                checked={data.constraints.noMeditation}
                onCheckedChange={(checked) =>
                  onUpdateNestedField("noMeditation", checked === true)
                }
              />
              <Label
                htmlFor="no-meditation"
                className="text-sm font-normal cursor-pointer"
              >
                I don't want meditation / breathwork
              </Label>
            </div>
          </div>
        </div>

        <div className="space-y-3">
          <Label>How much time can you realistically invest per day?</Label>
          <RadioGroup
            value={data.timeInvestment ?? ""}
            onValueChange={(value) =>
              onUpdateField("timeInvestment", value as TimeInvestment)
            }
          >
            {TIME_INVESTMENT_OPTIONS.map((option) => (
              <div key={option.value} className="flex items-center space-x-2">
                <RadioGroupItem value={option.value} id={option.value} />
                <Label htmlFor={option.value} className="font-normal">
                  {option.label}
                </Label>
              </div>
            ))}
          </RadioGroup>
        </div>
      </CardContent>
    </Card>
  );
}

