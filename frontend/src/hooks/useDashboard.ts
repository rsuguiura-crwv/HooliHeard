import { useQuery } from "@tanstack/react-query";
import type {
  DashboardSummary,
  AreaCount,
  CategoryCount,
  AccountCount,
  TrendPoint,
} from "@/types/dashboard";
import type { InsightFilters } from "@/types/insight";

// ---- Mock data for standalone demo ----

const MOCK_SUMMARY: DashboardSummary = {
  total_insights: 1247,
  key_records: 483,
  total_accounts: 64,
  sources_active: 5,
};

const MOCK_BY_AREA: AreaCount[] = [
  { product_area: "Infra", count: 387 },
  { product_area: "CKS", count: 264 },
  { product_area: "Platform", count: 218 },
  { product_area: "AI Services", count: 241 },
  { product_area: "W&B", count: 137 },
];

const MOCK_BY_CATEGORY: CategoryCount[] = [
  { insight_category: "Feature Request", count: 198 },
  { insight_category: "Bug Report", count: 142 },
  { insight_category: "Performance Issue", count: 127 },
  { insight_category: "Pricing Concern", count: 96 },
  { insight_category: "Documentation Gap", count: 89 },
  { insight_category: "Onboarding Friction", count: 84 },
  { insight_category: "Integration Need", count: 112 },
  { insight_category: "Scalability Concern", count: 78 },
  { insight_category: "Security Requirement", count: 71 },
  { insight_category: "UX Improvement", count: 63 },
  { insight_category: "API Enhancement", count: 58 },
  { insight_category: "Compliance Need", count: 74 },
  { insight_category: "Migration Blocker", count: 55 },
];

const MOCK_BY_ACCOUNT: AccountCount[] = [
  { account_name: "Anthropic", count: 87 },
  { account_name: "Meta", count: 74 },
  { account_name: "Microsoft", count: 68 },
  { account_name: "Cohere", count: 52 },
  { account_name: "Mistral AI", count: 47 },
  { account_name: "Inflection AI", count: 41 },
  { account_name: "Stability AI", count: 38 },
  { account_name: "Character.AI", count: 34 },
  { account_name: "Runway ML", count: 31 },
  { account_name: "Hugging Face", count: 28 },
];

const MOCK_TREND: TrendPoint[] = [
  { week: "2026-01-05", count: 42 },
  { week: "2026-01-12", count: 55 },
  { week: "2026-01-19", count: 48 },
  { week: "2026-01-26", count: 67 },
  { week: "2026-02-02", count: 73 },
  { week: "2026-02-09", count: 61 },
  { week: "2026-02-16", count: 89 },
  { week: "2026-02-23", count: 94 },
  { week: "2026-03-02", count: 78 },
  { week: "2026-03-09", count: 102 },
  { week: "2026-03-16", count: 118 },
  { week: "2026-03-23", count: 95 },
];

const USE_MOCK = true;

function delay<T>(data: T, ms = 300): Promise<T> {
  return new Promise((resolve) => setTimeout(() => resolve(data), ms));
}

// ---- Hooks ----

export function useSummary() {
  return useQuery<DashboardSummary>({
    queryKey: ["dashboard", "summary"],
    queryFn: () => {
      if (USE_MOCK) return delay(MOCK_SUMMARY);
      return import("@/api/dashboard").then((m) => m.fetchSummary());
    },
  });
}

export function useByArea(filters?: InsightFilters) {
  return useQuery<AreaCount[]>({
    queryKey: ["dashboard", "by-area", filters],
    queryFn: () => {
      if (USE_MOCK) {
        let data = MOCK_BY_AREA;
        if (filters?.product_area) {
          data = data.filter((d) => d.product_area === filters.product_area);
        }
        return delay(data);
      }
      return import("@/api/dashboard").then((m) => m.fetchByArea(filters));
    },
  });
}

export function useByCategory(filters?: InsightFilters) {
  return useQuery<CategoryCount[]>({
    queryKey: ["dashboard", "by-category", filters],
    queryFn: () => {
      if (USE_MOCK) {
        let data = MOCK_BY_CATEGORY;
        if (filters?.insight_category) {
          data = data.filter(
            (d) => d.insight_category === filters.insight_category,
          );
        }
        return delay(data);
      }
      return import("@/api/dashboard").then((m) =>
        m.fetchByCategory(filters),
      );
    },
  });
}

export function useByAccount(filters?: InsightFilters) {
  return useQuery<AccountCount[]>({
    queryKey: ["dashboard", "by-account", filters],
    queryFn: () => {
      if (USE_MOCK) return delay(MOCK_BY_ACCOUNT);
      return import("@/api/dashboard").then((m) =>
        m.fetchByAccount(filters),
      );
    },
  });
}

export function useTrend(filters?: InsightFilters) {
  return useQuery<TrendPoint[]>({
    queryKey: ["dashboard", "trend", filters],
    queryFn: () => {
      if (USE_MOCK) return delay(MOCK_TREND);
      return import("@/api/dashboard").then((m) => m.fetchTrend(filters));
    },
  });
}
