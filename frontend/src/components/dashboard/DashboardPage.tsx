import { useSearchParams } from "react-router-dom";
import { StatCard } from "@/components/shared/Card";
import { FilterBar } from "./FilterBar";
import { InsightsByArea } from "./InsightsByArea";
import { InsightsByCategory } from "./InsightsByCategory";
import { TrendChart } from "./TrendChart";
import { TopAccountsTable } from "./TopAccountsTable";
import {
  useSummary,
  useByArea,
  useByCategory,
  useByAccount,
  useTrend,
} from "@/hooks/useDashboard";
import { formatNumber } from "@/lib/utils";
import type { InsightFilters } from "@/types/insight";

export function DashboardPage() {
  const [searchParams] = useSearchParams();

  const filters: InsightFilters = {
    product_area: searchParams.get("product_area") ?? undefined,
    insight_category: searchParams.get("insight_category") ?? undefined,
  };

  const summary = useSummary();
  const byArea = useByArea(filters);
  const byCategory = useByCategory(filters);
  const byAccount = useByAccount(filters);
  const trend = useTrend(filters);

  return (
    <div className="space-y-6">
      {/* Filters */}
      <FilterBar />

      {/* Summary Stats */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Total Insights"
          value={
            summary.isLoading
              ? "..."
              : formatNumber(summary.data?.total_insights ?? 0)
          }
          subtitle="Across all sources"
          icon={
            <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 18v-5.25m0 0a6.01 6.01 0 0 0 1.5-.189m-1.5.189a6.01 6.01 0 0 1-1.5-.189m3.75 7.478a12.06 12.06 0 0 1-4.5 0m3.75 2.383a14.406 14.406 0 0 1-3 0M14.25 18v-.192c0-.983.658-1.823 1.508-2.316a7.5 7.5 0 1 0-7.517 0c.85.493 1.509 1.333 1.509 2.316V18" />
            </svg>
          }
        />
        <StatCard
          title="Key Records"
          value={
            summary.isLoading
              ? "..."
              : formatNumber(summary.data?.key_records ?? 0)
          }
          subtitle="Unique, deduplicated"
          icon={
            <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75 11.25 15 15 9.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
            </svg>
          }
        />
        <StatCard
          title="Accounts"
          value={
            summary.isLoading
              ? "..."
              : formatNumber(summary.data?.total_accounts ?? 0)
          }
          subtitle="Contributing feedback"
          icon={
            <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M18 18.72a9.094 9.094 0 0 0 3.741-.479 3 3 0 0 0-4.682-2.72m.94 3.198.001.031c0 .225-.012.447-.037.666A11.944 11.944 0 0 1 12 21c-2.17 0-4.207-.576-5.963-1.584A6.062 6.062 0 0 1 6 18.719m12 0a5.971 5.971 0 0 0-.941-3.197m0 0A5.995 5.995 0 0 0 12 12.75a5.995 5.995 0 0 0-5.058 2.772m0 0a3 3 0 0 0-4.681 2.72 8.986 8.986 0 0 0 3.74.477m.94-3.197a5.971 5.971 0 0 0-.94 3.197M15 6.75a3 3 0 1 1-6 0 3 3 0 0 1 6 0Zm6 3a2.25 2.25 0 1 1-4.5 0 2.25 2.25 0 0 1 4.5 0Zm-13.5 0a2.25 2.25 0 1 1-4.5 0 2.25 2.25 0 0 1 4.5 0Z" />
            </svg>
          }
        />
        <StatCard
          title="Sources Active"
          value={
            summary.isLoading
              ? "..."
              : String(summary.data?.sources_active ?? 0)
          }
          subtitle="Gong, SF, Jira, Slack, Qualtrics"
          icon={
            <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M13.19 8.688a4.5 4.5 0 0 1 1.242 7.244l-4.5 4.5a4.5 4.5 0 0 1-6.364-6.364l1.757-1.757m13.35-.622 1.757-1.757a4.5 4.5 0 0 0-6.364-6.364l-4.5 4.5a4.5 4.5 0 0 0 1.242 7.244" />
            </svg>
          }
        />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <InsightsByArea data={byArea.data} loading={byArea.isLoading} />
        <InsightsByCategory
          data={byCategory.data}
          loading={byCategory.isLoading}
        />
      </div>

      {/* Trend */}
      <TrendChart data={trend.data} loading={trend.isLoading} />

      {/* Accounts */}
      <TopAccountsTable data={byAccount.data} loading={byAccount.isLoading} />
    </div>
  );
}
