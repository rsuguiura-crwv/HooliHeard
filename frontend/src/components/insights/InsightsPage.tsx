import { useState } from "react";
import { useInsights } from "../../hooks/useInsights";
import type { InsightFilters, Insight } from "../../types/insight";
import InsightFiltersPanel from "./InsightFilters";
import InsightTable from "./InsightTable";
import InsightDetail from "./InsightDetail";

export default function InsightsPage() {
  const [filters, setFilters] = useState<InsightFilters>({
    page: 1,
    page_size: 25,
    unique_insight_status: "Key Record",
  });
  const [selectedInsight, setSelectedInsight] = useState<Insight | null>(null);

  const { data, isLoading } = useInsights(filters);

  return (
    <div className="flex h-full gap-6">
      {/* Filters Sidebar */}
      <div className="w-64 shrink-0">
        <InsightFiltersPanel filters={filters} onChange={setFilters} />
      </div>

      {/* Main Content */}
      <div className="min-w-0 flex-1 space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-slate-900">Insights</h1>
            <p className="mt-1 text-sm text-slate-500">
              {isLoading ? "Loading..." : `${data?.total ?? 0} insights found`}
            </p>
          </div>
          <button
            onClick={() => {
              window.open(`/api/insights/export?${new URLSearchParams(
                Object.entries(filters)
                  .filter(([, v]) => v != null)
                  .map(([k, v]) => [k, String(v)])
              ).toString()}`);
            }}
            className="rounded-md bg-slate-100 px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-200"
          >
            Export CSV
          </button>
        </div>

        {isLoading ? (
          <div className="flex h-64 items-center justify-center text-slate-400">
            Loading insights...
          </div>
        ) : (
          <InsightTable
            insights={data?.items ?? []}
            onSelect={setSelectedInsight}
            selectedId={selectedInsight?.id}
          />
        )}

        {/* Pagination */}
        {data && data.total > data.page_size && (
          <div className="flex items-center justify-between border-t border-slate-200 pt-4">
            <span className="text-sm text-slate-500">
              Page {data.page} of {Math.ceil(data.total / data.page_size)}
            </span>
            <div className="flex gap-2">
              <button
                disabled={data.page <= 1}
                onClick={() => setFilters((f) => ({ ...f, page: (f.page ?? 1) - 1 }))}
                className="rounded-md bg-slate-100 px-3 py-1 text-sm disabled:opacity-50"
              >
                Previous
              </button>
              <button
                disabled={data.page * data.page_size >= data.total}
                onClick={() => setFilters((f) => ({ ...f, page: (f.page ?? 1) + 1 }))}
                className="rounded-md bg-slate-100 px-3 py-1 text-sm disabled:opacity-50"
              >
                Next
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Detail Panel */}
      {selectedInsight && (
        <InsightDetail
          insight={selectedInsight}
          onClose={() => setSelectedInsight(null)}
        />
      )}
    </div>
  );
}
