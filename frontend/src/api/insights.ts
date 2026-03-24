import type { InsightFilters, InsightListResponse, Insight } from "@/types/insight";
import { apiFetch, buildQueryString } from "./client";

export async function fetchInsights(
  filters: InsightFilters,
): Promise<InsightListResponse> {
  const qs = buildQueryString(filters as Record<string, string | number | undefined>);
  return apiFetch<InsightListResponse>(`/insights${qs}`);
}

export async function fetchInsight(id: string): Promise<Insight> {
  return apiFetch<Insight>(`/insights/${id}`);
}

export async function exportInsightsCsv(
  filters: InsightFilters,
): Promise<Blob> {
  const qs = buildQueryString(filters as Record<string, string | number | undefined>);
  const res = await fetch(`/api/insights/export${qs}`);
  if (!res.ok) throw new Error("Export failed");
  return res.blob();
}
