import type { Insight } from "@/types/insight";
import { Badge } from "@/components/shared/Badge";
import { PRODUCT_AREA_COLORS, SOURCE_TOOLS } from "@/lib/constants";
import { formatDate } from "@/lib/utils";

interface Props {
  insight: Insight | null | undefined;
  loading: boolean;
  onClose: () => void;
}

export function InsightDetail({ insight, loading, onClose }: Props) {
  return (
    <div className="fixed inset-y-0 right-0 z-50 flex">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/20 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Panel */}
      <div className="relative ml-auto flex h-full w-full max-w-lg flex-col bg-white shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-200 px-6 py-4">
          <h3 className="text-sm font-semibold text-slate-900">
            Insight Detail
          </h3>
          <button
            onClick={onClose}
            className="rounded-lg p-1.5 text-slate-400 hover:bg-slate-100 hover:text-slate-600 transition-colors"
          >
            <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18 18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {loading || !insight ? (
            <div className="space-y-4">
              <div className="h-6 w-1/3 animate-pulse rounded bg-slate-100" />
              <div className="h-32 animate-pulse rounded bg-slate-100" />
              <div className="h-6 w-1/2 animate-pulse rounded bg-slate-100" />
            </div>
          ) : (
            <>
              {/* Badges */}
              <div className="flex flex-wrap gap-2">
                <Badge
                  label={insight.product_area}
                  color={PRODUCT_AREA_COLORS[insight.product_area]}
                  variant="filled"
                />
                <Badge label={insight.insight_category} />
                <Badge
                  label={
                    insight.unique_insight_status === "key_record"
                      ? "Key Record"
                      : "Duplicate"
                  }
                  color={
                    insight.unique_insight_status === "key_record"
                      ? "#10B981"
                      : "#94a3b8"
                  }
                  variant="subtle"
                />
              </div>

              {/* Insight Text */}
              <div>
                <label className="mb-2 block text-xs font-semibold uppercase tracking-wider text-slate-400">
                  Insight
                </label>
                <p className="text-sm leading-relaxed text-slate-700">
                  {insight.insight_text}
                </p>
              </div>

              {/* Account */}
              <div className="rounded-lg border border-slate-200 p-4">
                <label className="mb-2 block text-xs font-semibold uppercase tracking-wider text-slate-400">
                  Account
                </label>
                <p className="text-sm font-semibold text-slate-900">
                  {insight.account_name}
                </p>
                {insight.role_present && (
                  <p className="mt-1 text-xs text-slate-500">
                    Contact: {insight.role_present}
                  </p>
                )}
              </div>

              {/* Source */}
              <div className="rounded-lg border border-slate-200 p-4">
                <label className="mb-2 block text-xs font-semibold uppercase tracking-wider text-slate-400">
                  Source
                </label>
                <div className="flex items-center gap-3">
                  {SOURCE_TOOLS[insight.source_tool] && (
                    <span
                      className="flex h-8 w-8 items-center justify-center rounded-lg text-sm font-bold text-white"
                      style={{
                        backgroundColor:
                          SOURCE_TOOLS[insight.source_tool].color,
                      }}
                    >
                      {SOURCE_TOOLS[insight.source_tool].icon}
                    </span>
                  )}
                  <div>
                    <p className="text-sm font-medium text-slate-700">
                      {SOURCE_TOOLS[insight.source_tool]?.label ??
                        insight.source_tool}
                    </p>
                    <p className="text-xs text-slate-500">
                      {insight.input_data_source}
                    </p>
                  </div>
                </div>
                {insight.source_link && (
                  <a
                    href={insight.source_link}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="mt-3 inline-flex items-center gap-1 text-xs font-medium text-blue-600 hover:text-blue-700"
                  >
                    View source
                    <svg className="h-3 w-3" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 6H5.25A2.25 2.25 0 0 0 3 8.25v10.5A2.25 2.25 0 0 0 5.25 21h10.5A2.25 2.25 0 0 0 18 18.75V10.5m-10.5 6L21 3m0 0h-5.25M21 3v5.25" />
                    </svg>
                  </a>
                )}
              </div>

              {/* Metadata */}
              <div className="space-y-2 text-xs text-slate-500">
                <div className="flex justify-between">
                  <span>Product Subcategory</span>
                  <span className="font-medium text-slate-700">
                    {insight.product_subcategory}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span>Date of Record</span>
                  <span className="font-medium text-slate-700">
                    {formatDate(insight.date_of_record)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span>Dedup Group</span>
                  <span className="font-mono font-medium text-slate-700">
                    {insight.dedup_group_key}
                  </span>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
