"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { useRef, ChangeEvent } from "react";
import type { OnboardingData } from "@/lib/onboarding-schema";

interface BloodTestStepProps {
  data: OnboardingData;
  onUpdateField: <K extends keyof OnboardingData>(
    field: K,
    value: OnboardingData[K]
  ) => void;
  onSetLabFile: (file: File | null) => void;
  onSkip: () => void;
}

export function BloodTestStep({
  data,
  onUpdateField,
  onSetLabFile,
  onSkip,
}: BloodTestStepProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0] || null;
    if (file && file.type === "application/pdf") {
      onSetLabFile(file);
    } else if (file) {
      alert("Please upload a PDF file");
    } else {
      onSetLabFile(null);
    }
  };

  const handleRemoveFile = () => {
    onSetLabFile(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Blood Test (optional)</CardTitle>
        <CardDescription>
          Upload your lab report PDF or enter values manually. Our AI will
          extract the values from your PDF automatically.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="lab-pdf">Upload Lab Report PDF</Label>
            <div className="flex items-center gap-4">
              <Input
                ref={fileInputRef}
                id="lab-pdf"
                type="file"
                accept=".pdf"
                onChange={handleFileChange}
                className="cursor-pointer"
              />
              {data.labPdfFile && (
                <div className="flex items-center gap-2">
                  <span className="text-sm text-muted-foreground">
                    {data.labPdfFile.name}
                  </span>
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    onClick={handleRemoveFile}
                  >
                    Remove
                  </Button>
                </div>
              )}
            </div>
            <p className="text-xs text-muted-foreground">
              Upload your latest lab report PDF. We'll extract the blood values
              automatically.
            </p>
          </div>

          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <span className="w-full border-t" />
            </div>
            <div className="relative flex justify-center text-xs uppercase">
              <span className="bg-card px-2 text-muted-foreground">Or</span>
            </div>
          </div>

          <div className="space-y-2">
            <div className="flex items-center space-x-2">
              <input
                type="checkbox"
                id="manual-entry"
                checked={data.manualEntry}
                onChange={(e) =>
                  onUpdateField("manualEntry", e.target.checked)
                }
                className="h-4 w-4 rounded border-gray-300"
              />
              <Label htmlFor="manual-entry" className="cursor-pointer">
                Enter values manually
              </Label>
            </div>
          </div>
        </div>

        {data.manualEntry && (
          <div className="space-y-4 pt-4 border-t">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="hba1c">HbA1c (%)</Label>
                <Input
                  id="hba1c"
                  type="number"
                  step="0.1"
                  min="3"
                  max="15"
                  placeholder="e.g. 5.2"
                  value={data.hba1c ?? ""}
                  onChange={(e) =>
                    onUpdateField(
                      "hba1c",
                      e.target.value ? Number(e.target.value) : null
                    )
                  }
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="ldl">LDL (mg/dL)</Label>
                <Input
                  id="ldl"
                  type="number"
                  min="0"
                  max="300"
                  placeholder="e.g. 120"
                  value={data.ldl ?? ""}
                  onChange={(e) =>
                    onUpdateField(
                      "ldl",
                      e.target.value ? Number(e.target.value) : null
                    )
                  }
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="hdl">HDL (mg/dL)</Label>
                <Input
                  id="hdl"
                  type="number"
                  min="0"
                  max="150"
                  placeholder="e.g. 60"
                  value={data.hdl ?? ""}
                  onChange={(e) =>
                    onUpdateField(
                      "hdl",
                      e.target.value ? Number(e.target.value) : null
                    )
                  }
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="triglycerides">Triglycerides (mg/dL)</Label>
                <Input
                  id="triglycerides"
                  type="number"
                  min="0"
                  max="1000"
                  placeholder="e.g. 100"
                  value={data.triglycerides ?? ""}
                  onChange={(e) =>
                    onUpdateField(
                      "triglycerides",
                      e.target.value ? Number(e.target.value) : null
                    )
                  }
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="crp">CRP (mg/L)</Label>
                <Input
                  id="crp"
                  type="number"
                  step="0.1"
                  min="0"
                  max="50"
                  placeholder="e.g. 1.5"
                  value={data.crp ?? ""}
                  onChange={(e) =>
                    onUpdateField(
                      "crp",
                      e.target.value ? Number(e.target.value) : null
                    )
                  }
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="resting-heart-rate">Resting heart rate (bpm)</Label>
                <Input
                  id="resting-heart-rate"
                  type="number"
                  min="40"
                  max="120"
                  placeholder="e.g. 65"
                  value={data.restingHeartRate ?? ""}
                  onChange={(e) =>
                    onUpdateField(
                      "restingHeartRate",
                      e.target.value ? Number(e.target.value) : null
                    )
                  }
                />
              </div>
            </div>
          </div>
        )}

        <div className="pt-4 border-t">
          <Button variant="outline" onClick={onSkip} className="w-full">
            Skip
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
