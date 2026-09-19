export function contextTitle(value: unknown): string {
  if (!value || typeof value !== "object") {
    return "—";
  }
  const record = value as Record<string, unknown>;
  const candidate = record.ID ?? record.Id ?? record.id ?? record.Name ?? record.name;
  return candidate == null || candidate === "" ? "—" : String(candidate);
}
