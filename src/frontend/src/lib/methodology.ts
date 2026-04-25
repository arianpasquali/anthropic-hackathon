// FRAME methodology constants — sources documented in /methodology page.

export const EMISSION_FACTORS = {
  produce: 1.0,    // FAO Food Wastage Footprint (2013), Table 4.2
  bakery: 1.5,     // WRAP Courtauld Commitment 2030
  dry_goods: 2.0,  // FAO FWF cereals + Poore & Nemecek (2018)
  prepared: 3.0,   // Poore & Nemecek (2018)
  dairy: 3.2,      // FAO FWF + RIVM Dutch dairy LCA
  eggs: 4.5,       // FAO FWF + Dutch egg sector data
  meat: 8.5,       // FAO FWF (2013) weighted Dutch meat consumption mix
} as const

// NL counterfactual: incineration with energy recovery — RIVM Afvalmonitor 2024 + CBS
export const CF_NL = 0.93

export const EMISSION_FACTOR_SOURCES: Record<keyof typeof EMISSION_FACTORS, string> = {
  produce: "FAO FWF (2013) Table 4.2",
  bakery: "WRAP Courtauld Commitment 2030",
  dry_goods: "FAO FWF + Poore & Nemecek (2018)",
  prepared: "Poore & Nemecek (2018)",
  dairy: "FAO FWF + RIVM Dutch dairy LCA",
  eggs: "FAO FWF + Dutch egg sector",
  meat: "FAO FWF (2013) weighted NL consumption mix",
}

export const CATEGORY_LABELS: Record<keyof typeof EMISSION_FACTORS, string> = {
  produce: "Produce",
  bakery: "Bakery",
  dry_goods: "Dry goods",
  prepared: "Prepared",
  dairy: "Dairy",
  eggs: "Eggs",
  meat: "Meat",
}
