import type { SearchIntent } from "@/domain/schemas";

const makes = ["Toyota", "Nissan", "Mercedes-Benz", "BMW", "Lexus", "Ford", "Porsche", "Volkswagen", "Land Rover", "Honda"];
const bodyTypes = ["SUV", "Sedan", "Coupe", "Hatchback", "Pickup", "Convertible"];
const cities = ["Dubai", "Abu Dhabi", "Sharjah", "Ajman"];

export function interpretFixturePrompt(prompt: string): { mode: "fixture"; intent: SearchIntent; summary: string } {
  const normalized = prompt.toLowerCase();
  const intent: SearchIntent = {};
  const make = makes.find((item) => normalized.includes(item.toLowerCase().replace("-", " ")) || normalized.includes(item.toLowerCase()));
  const bodyType = bodyTypes.find((item) => normalized.includes(item.toLowerCase()));
  const city = cities.find((item) => normalized.includes(item.toLowerCase()));
  const budgetMatch = normalized.match(/(?:under|below|max(?:imum)?|up to)\s*(?:aed)?\s*([\d,]+)\s*(k)?/);
  const yearMatch = normalized.match(/(20\d{2})\s*(?:or newer|and newer|\+)/);
  if (make) intent.make = [make];
  if (bodyType) intent.bodyType = [bodyType];
  if (city) intent.city = [city];
  if (normalized.includes("gcc")) intent.specifications = ["GCC"];
  if (budgetMatch) intent.priceMax = Number(budgetMatch[1].replaceAll(",", "")) * (budgetMatch[2] ? 1000 : 1);
  if (yearMatch) intent.yearMin = Number(yearMatch[1]);
  if (/accident[- ]free|clean/.test(normalized)) intent.conditionPreferences = ["Accident history stated"];
  const preference = intent.conditionPreferences?.length ? " Condition language is treated as a preference until a source states evidence." : "";
  return { mode: "fixture", intent, summary: `Fixture interpreter found ${Object.keys(intent).length} requirement groups.${preference}` };
}
