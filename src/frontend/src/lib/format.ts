const NL = "nl-NL"

export function formatNumber(value: number, opts?: Intl.NumberFormatOptions) {
  return new Intl.NumberFormat(NL, { maximumFractionDigits: 0, ...opts }).format(value)
}

export function formatEur(value: number) {
  return new Intl.NumberFormat(NL, {
    style: "currency",
    currency: "EUR",
    maximumFractionDigits: 0,
  }).format(value)
}

export function formatPercent(value: number, fractionDigits = 1) {
  return new Intl.NumberFormat(NL, {
    style: "percent",
    minimumFractionDigits: fractionDigits,
    maximumFractionDigits: fractionDigits,
  }).format(value)
}

export function formatTonnes(kg: number) {
  return formatNumber(kg / 1000, { maximumFractionDigits: 0 }) + " t"
}

export function formatTCO2e(tco2e: number) {
  return formatNumber(tco2e, { maximumFractionDigits: 0 }) + " tCO₂e"
}

export function formatKg(kg: number) {
  if (kg >= 1_000_000) return formatNumber(kg / 1_000_000, { maximumFractionDigits: 1 }) + "M kg"
  if (kg >= 1_000) return formatNumber(kg / 1_000, { maximumFractionDigits: 0 }) + "k kg"
  return formatNumber(kg) + " kg"
}
