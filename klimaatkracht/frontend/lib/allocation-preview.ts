/**
 * JS mirror of backend/app/services/allocation_engine.py.
 *
 * Same algorithm, same numerics — identical inputs must produce identical
 * outputs to within floating-point noise. The parity test in
 * tests/allocation-preview.test.ts asserts this against a Python-generated
 * fixture; that's the spine of Invariant 5 ("frontend allocation preview
 * matches backend").
 */

import type {
  AllocationPreferences,
  AllocationResult,
  ChapterSnapshot,
} from "./types";

export class AllocationPreferencesError extends Error {}

export function validatePreferences(prefs: AllocationPreferences): void {
  const total =
    prefs.max_climate_impact + prefs.max_social_need + prefs.balanced_distribution;
  if (Math.abs(total - 1.0) > 0.001) {
    throw new AllocationPreferencesError(
      `Preferences must sum to 1.0, got ${total}`,
    );
  }
}

function normalize(values: Record<string, number>): Record<string, number> {
  const total = Object.values(values).reduce((a, b) => a + b, 0);
  if (total <= 0) {
    return Object.fromEntries(Object.keys(values).map((k) => [k, 0]));
  }
  return Object.fromEntries(
    Object.entries(values).map(([k, v]) => [k, v / total]),
  );
}

export function computeAllocation(
  chapters: ChapterSnapshot[],
  preferences: AllocationPreferences,
  amountEur: number,
): Record<string, AllocationResult> {
  validatePreferences(preferences);

  const climateW = normalize(
    Object.fromEntries(chapters.map((c) => [c.id, c.net_avoided_tco2e])),
  );
  const socialW = normalize(
    Object.fromEntries(
      chapters.map((c) => [
        c.id,
        c.households_served_quarter * c.needs_score * c.regional_bonus,
      ]),
    ),
  );
  const balancedW = normalize(
    Object.fromEntries(chapters.map((c) => [c.id, c.total_tonnes])),
  );

  const blendedRaw = Object.fromEntries(
    chapters.map((c) => [
      c.id,
      climateW[c.id] * preferences.max_climate_impact +
        socialW[c.id] * preferences.max_social_need +
        balancedW[c.id] * preferences.balanced_distribution,
    ]),
  );
  const blended = normalize(blendedRaw);

  return Object.fromEntries(
    chapters.map((c) => [
      c.id,
      {
        chapter_id: c.id,
        weight: blended[c.id],
        amount_eur: amountEur * blended[c.id],
        axis_weights: {
          climate: climateW[c.id],
          social: socialW[c.id],
          balanced: balancedW[c.id],
        },
      },
    ]),
  );
}
