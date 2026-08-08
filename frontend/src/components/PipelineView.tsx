import { useEffect, useState } from "react";
import "./PipelineView.css";

const STEPS = [
  "Embedding your question",
  "Searching the knowledge base",
  "Re-ranking results",
  "Checking confidence",
  "Generating answer",
];

const STEP_INTERVAL_MS = 500;

interface PipelineViewProps {
  active: boolean;
}

export default function PipelineView({ active }: PipelineViewProps) {
  const [currentStep, setCurrentStep] = useState(0);

  useEffect(() => {
    if (!active) {
      setCurrentStep(0);
      return;
    }

    const interval = setInterval(() => {
      setCurrentStep((prev) => (prev < STEPS.length - 1 ? prev + 1 : prev));
    }, STEP_INTERVAL_MS);

    return () => clearInterval(interval);
  }, [active]);

  if (!active) return null;

  return (
    <div className="pipeline-view">
      {STEPS.map((step, i) => (
        <div
          key={step}
          className={
            i < currentStep
              ? "pipeline-step pipeline-step--done"
              : i === currentStep
              ? "pipeline-step pipeline-step--active"
              : "pipeline-step"
          }
        >
          <span className="pipeline-dot" />
          <span>{step}</span>
        </div>
      ))}
    </div>
  );
}
