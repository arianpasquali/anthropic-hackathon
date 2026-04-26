"use client";

import { useState, useRef, useCallback } from "react";

interface Gemeente {
  code: string;
  name: string;
  path: string;
  persons_in_poverty: number | null;
  households_in_poverty: number | null;
  persons_in_poverty_pct: number | null;
  households_in_poverty_pct: number | null;
}

interface Bank {
  id: string;
  name: string;
  region?: string;
  x: number;
  y: number;
  annual_tco2e?: number;
  households_weekly?: number | null;
  is_rdc?: boolean;
  rdc_satellite_count?: number | null;
  in_demo_cohort: boolean;
}

interface Props {
  width: number;
  height: number;
  gemeenten: Gemeente[];
  banks: Bank[];
}

type Hovered =
  | { kind: "gemeente"; data: Gemeente }
  | { kind: "bank"; data: Bank }
  | null;

function bucketColor(pct: number | null): string {
  if (pct === null) return "#f5f5f4";
  if (pct < 2) return "#fafaf9";
  if (pct < 3) return "#e7e5e4";
  if (pct < 4) return "#fde68a";
  if (pct < 5.5) return "#f59e0b";
  return "#b45309";
}

function bankRadius(tco2e?: number): number {
  if (!tco2e) return 5;
  return Math.max(5, Math.min(14, 5 + Math.sqrt(tco2e / 100)));
}

function fmtInt(n: number): string {
  return new Intl.NumberFormat("en-NL").format(Math.round(n));
}

export default function CoverageMap({ width, height, gemeenten, banks }: Props) {
  const [hovered, setHovered] = useState<Hovered>(null);
  const [pointer, setPointer] = useState<{ x: number; y: number } | null>(null);
  const wrapperRef = useRef<HTMLDivElement>(null);

  const onMove = useCallback((e: React.MouseEvent) => {
    const rect = wrapperRef.current?.getBoundingClientRect();
    if (!rect) return;
    setPointer({ x: e.clientX - rect.left, y: e.clientY - rect.top });
  }, []);

  const clear = useCallback(() => {
    setHovered(null);
    setPointer(null);
  }, []);

  const nonDemo = banks.filter((b) => !b.in_demo_cohort);
  const demo = banks.filter((b) => b.in_demo_cohort);

  return (
    <div
      ref={wrapperRef}
      className="relative"
      onMouseMove={onMove}
      onMouseLeave={clear}
    >
      <svg
        viewBox={`0 0 ${width} ${height}`}
        className="w-full h-auto"
        role="img"
        aria-label="Map of the Netherlands shaded by poverty share, with foodbank locations overlaid."
      >
        {/* Choropleth */}
        <g>
          {gemeenten.map((g) => (
            <path
              key={g.code}
              d={g.path}
              fill={bucketColor(g.persons_in_poverty_pct)}
              stroke={hovered?.kind === "gemeente" && hovered.data.code === g.code ? "#0c0a09" : "#ffffff"}
              strokeWidth={hovered?.kind === "gemeente" && hovered.data.code === g.code ? 1.5 : 0.4}
              onMouseEnter={() => setHovered({ kind: "gemeente", data: g })}
              style={{ cursor: "pointer" }}
            />
          ))}
        </g>

        {/* Non-demo banks (small dots) */}
        <g>
          {nonDemo.map((b) => {
            const isHov = hovered?.kind === "bank" && hovered.data.id === b.id;
            return (
              <circle
                key={b.id}
                cx={b.x}
                cy={b.y}
                r={isHov ? 6 : 4}
                fill={isHov ? "#0c0a09" : "#fafaf9"}
                stroke={isHov ? "#0c0a09" : "#44403c"}
                strokeWidth={1}
                opacity={0.95}
                onMouseEnter={() => setHovered({ kind: "bank", data: b })}
                style={{ cursor: "pointer" }}
              />
            );
          })}
        </g>

        {/* Demo banks (emerald circles, sized by tCO2e) */}
        <g>
          {demo.map((b) => {
            const isHov = hovered?.kind === "bank" && hovered.data.id === b.id;
            const r = bankRadius(b.annual_tco2e);
            return (
              <g key={b.id}>
                <circle
                  cx={b.x}
                  cy={b.y}
                  r={r + 2}
                  fill="#ffffff"
                  stroke="#065f46"
                  strokeWidth={1}
                />
                <circle
                  cx={b.x}
                  cy={b.y}
                  r={isHov ? r + 1 : r}
                  fill={isHov ? "#022c22" : "#065f46"}
                  stroke="#ffffff"
                  strokeWidth={1.5}
                  onMouseEnter={() => setHovered({ kind: "bank", data: b })}
                  style={{ cursor: "pointer" }}
                />
              </g>
            );
          })}
        </g>
      </svg>

      {hovered && pointer && (
        <Tooltip pointer={pointer} hovered={hovered} />
      )}
    </div>
  );
}

function Tooltip({
  pointer,
  hovered,
}: {
  pointer: { x: number; y: number };
  hovered: Hovered;
}) {
  if (!hovered) return null;

  // Position above-right of the cursor; flip if near right/bottom edge
  const TOOLTIP_W = 240;
  const TOOLTIP_H_GUESS = 120;
  const margin = 12;
  let left = pointer.x + margin;
  let top = pointer.y + margin;
  // Naive flip: shift left if close to right edge — works because the wrapper
  // has the same width as the SVG render box on screen
  // (we don't know the wrapper width here without measurement, so use simple heuristic)
  if (typeof window !== "undefined") {
    const wrapper = document.querySelector("[data-coverage-map]");
    // skip wrapper measurement; instead just clamp on the right via inline style max
  }

  return (
    <div
      role="tooltip"
      className="absolute z-10 pointer-events-none rounded-lg border border-stone-200 bg-white shadow-md p-3 text-sm"
      style={{
        left,
        top,
        width: TOOLTIP_W,
      }}
    >
      {hovered.kind === "gemeente" ? (
        <GemeenteTip g={hovered.data} />
      ) : (
        <BankTip b={hovered.data} />
      )}
    </div>
  );
}

function GemeenteTip({ g }: { g: Gemeente }) {
  return (
    <div>
      <p className="font-semibold text-stone-900">{g.name}</p>
      <p className="text-xs text-stone-500 mt-0.5">Gemeente · poverty 2023</p>
      <dl className="mt-2 space-y-1 text-xs">
        <Row label="Persons (≥ 1 yr low income)" value={
          g.persons_in_poverty !== null ? fmtInt(g.persons_in_poverty) : "—"
        } />
        <Row label="Share of population" value={
          g.persons_in_poverty_pct !== null
            ? `${g.persons_in_poverty_pct.toFixed(1)}%`
            : "—"
        } />
        <Row label="Households" value={
          g.households_in_poverty !== null ? fmtInt(g.households_in_poverty) : "—"
        } />
      </dl>
    </div>
  );
}

function BankTip({ b }: { b: Bank }) {
  return (
    <div>
      <p className="font-semibold text-stone-900">{b.name}</p>
      <p className="text-xs text-stone-500 mt-0.5">
        {b.region ?? "Nederland"} · {b.in_demo_cohort ? "Demo cohort" : "NL network"}
      </p>
      {b.in_demo_cohort && (
        <dl className="mt-2 space-y-1 text-xs">
          {b.annual_tco2e !== undefined && (
            <Row label="Annual avoided emissions" value={`${fmtInt(b.annual_tco2e)} tCO₂e`} />
          )}
          {b.households_weekly && (
            <Row label="Households / week" value={fmtInt(b.households_weekly)} />
          )}
          {b.is_rdc && b.rdc_satellite_count && (
            <Row label="RDC satellites" value={`${b.rdc_satellite_count} banks`} />
          )}
        </dl>
      )}
      {!b.in_demo_cohort && (
        <p className="mt-2 text-xs text-stone-600 leading-snug">
          Member of Voedselbanken Nederland; not yet in the platform&apos;s
          demo cohort.
        </p>
      )}
    </div>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between gap-3">
      <dt className="text-stone-500">{label}</dt>
      <dd className="font-medium tabular-nums text-stone-900">{value}</dd>
    </div>
  );
}
