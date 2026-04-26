// Server-only: filesystem loader. Types and formatters live in impact-types.ts.
import "server-only";
import { promises as fs } from "fs";
import path from "path";
import type { ImpactData } from "./impact-types";

export * from "./impact-types";

let cached: ImpactData | null = null;

export async function loadImpact(): Promise<ImpactData> {
  if (cached) return cached;
  const p = path.join(process.cwd(), "public", "impact-data.json");
  const raw = await fs.readFile(p, "utf-8");
  cached = JSON.parse(raw) as ImpactData;
  return cached;
}
