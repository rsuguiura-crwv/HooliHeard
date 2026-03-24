import type {
  DashboardSummary,
  AreaCount,
  CategoryCount,
  AccountCount,
  TrendPoint,
} from "@/types/dashboard";
import type { InsightFilters } from "@/types/insight";
import { apiFetch, buildQueryString } from "./client";

export async function fetchSummary(): Promise<DashboardSummary> {
  return apiFetch<DashboardSummary>("/dashboard/summary");
}

export async function fetchByArea(
  filters?: InsightFilters,
): Promise<AreaCount[]> {
  const qs = buildQueryString(
    (filters ?? {}) as Record<string, string | number | undefined>,
  );
  return apiFetch<AreaCount[]>(`/dashboard/by-area${qs}`);
}

export async function fetchByCategory(
  filters?: InsightFilters,
): Promise<CategoryCount[]> {
  const qs = buildQueryString(
    (filters ?? {}) as Record<string, string | number | undefined>,
  );
  return apiFetch<CategoryCount[]>(`/dashboard/by-category${qs}`);
}

export async function fetchByAccount(
  filters?: InsightFilters,
): Promise<AccountCount[]> {
  const qs = buildQueryString(
    (filters ?? {}) as Record<string, string | number | undefined>,
  );
  return apiFetch<AccountCount[]>(`/dashboard/by-account${qs}`);
}

export async function fetchTrend(
  filters?: InsightFilters,
): Promise<TrendPoint[]> {
  const qs = buildQueryString(
    (filters ?? {}) as Record<string, string | number | undefined>,
  );
  return apiFetch<TrendPoint[]>(`/dashboard/trend${qs}`);
}
