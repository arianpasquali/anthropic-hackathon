"use client";

import { useEffect, useMemo, useState } from "react";

import type { AllocationPreferences } from "../../lib/types";

type Axis = keyof AllocationPreferences;

export type AllocationSlidersProps = {
  value: AllocationPreferences;
  onChange: (next: AllocationPreferences) => void;
};

const AXIS_LABELS: Record<Axis, { title: string; description: string }> = {
  max_climate_impact: {
    title: "Max climate impact",
    description: "Weight chapters by net avoided emissions per euro spent.",
  },
  max_social_need: {
    title: "Max social need",
    description:
      "Weight chapters by households served × needs index × regional bonus.",
  },
  balanced_distribution: {
    title: "Balanced distribution",
    description: "Weight chapters by total tonnage rescued.",
  },
};

/**
 * Three sliders that always sum to 1.0. Adjusting one redistributes the
 * remainder proportionally between the other two — same UX you'd find on
 * a portfolio rebalancing tool.
 */
export function AllocationSliders({ value, onChange }: AllocationSlidersProps) {
  const [internal, setInternal] = useState(value);

  useEffect(() => {
    setInternal(value);
  }, [value]);

  function updateAxis(axis: Axis, raw: number) {
    const remainder = 1 - raw;
    const others = (Object.keys(internal) as Axis[]).filter((k) => k !== axis);
    const otherSum = others.reduce((acc, k) => acc + internal[k], 0);

    const next: AllocationPreferences = { ...internal };
    next[axis] = raw;
    if (otherSum <= 0) {
      // Distribute the remainder evenly when the other two are at zero.
      others.forEach((k) => {
        next[k] = remainder / others.length;
      });
    } else {
      others.forEach((k) => {
        next[k] = (internal[k] / otherSum) * remainder;
      });
    }

    setInternal(next);
    onChange(next);
  }

  return (
    <div className="space-y-6">
      {(Object.keys(AXIS_LABELS) as Axis[]).map((axis) => {
        const label = AXIS_LABELS[axis];
        const v = internal[axis];
        return (
          <div key={axis}>
            <div className="flex items-baseline justify-between">
              <span className="text-sm font-medium">{label.title}</span>
              <span className="font-mono text-sm tabular-nums">
                {(v * 100).toFixed(0)}%
              </span>
            </div>
            <p className="text-xs text-ink/60">{label.description}</p>
            <input
              type="range"
              min={0}
              max={1}
              step={0.01}
              value={v}
              onChange={(e) => updateAxis(axis, Number(e.target.value))}
              className="mt-2 w-full"
            />
          </div>
        );
      })}
      <SumIndicator value={internal} />
    </div>
  );
}

function SumIndicator({ value }: { value: AllocationPreferences }) {
  const sum = useMemo(
    () =>
      value.max_climate_impact +
      value.max_social_need +
      value.balanced_distribution,
    [value],
  );
  const ok = Math.abs(sum - 1) < 0.01;
  return (
    <div className="rounded-md border border-ink/10 bg-white px-3 py-2 text-xs text-ink/70">
      Sum: <span className="font-mono">{sum.toFixed(2)}</span>{" "}
      {ok ? "✓" : <span className="text-red-700">— must equal 1.00</span>}
    </div>
  );
}
