import { PRODUCT_AREAS, INSIGHT_CATEGORIES } from "@/lib/constants";
import type { InsightFilters as IFilters } from "@/types/insight";

interface Props {
  filters: IFilters;
  onChange: (filters: IFilters) => void;
}

export function InsightFilters({ filters, onChange }: Props) {
  const update = (key: keyof IFilters, value: string) => {
    onChange({ ...filters, [key]: value || undefined, page: 1 });
  };

  const clear = () => {
    onChange({ page: 1, page_size: 20 });
  };

  return (
    <div className="w-64 shrink-0 space-y-5">
      <div className="card p-5 space-y-5">
        <h3 className="text-sm font-semibold text-slate-900">Filters</h3>

        {/* Product Area */}
        <div>
          <label className="mb-1.5 block text-xs font-medium text-slate-500">
            Product Area
          </label>
          <select
            value={filters.product_area ?? ""}
            onChange={(e) => update("product_area", e.target.value)}
            className="w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
          >
            <option value="">All</option>
            {PRODUCT_AREAS.map((pa) => (
              <option key={pa.value} value={pa.value}>
                {pa.label}
              </option>
            ))}
          </select>
        </div>

        {/* Category */}
        <div>
          <label className="mb-1.5 block text-xs font-medium text-slate-500">
            Category
          </label>
          <select
            value={filters.insight_category ?? ""}
            onChange={(e) => update("insight_category", e.target.value)}
            className="w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
          >
            <option value="">All</option>
            {INSIGHT_CATEGORIES.map((cat) => (
              <option key={cat} value={cat}>
                {cat}
              </option>
            ))}
          </select>
        </div>

        {/* Account search */}
        <div>
          <label className="mb-1.5 block text-xs font-medium text-slate-500">
            Account
          </label>
          <input
            type="text"
            placeholder="Search accounts..."
            value={filters.account_name ?? ""}
            onChange={(e) => update("account_name", e.target.value)}
            className="w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
          />
        </div>

        {/* Date range */}
        <div>
          <label className="mb-1.5 block text-xs font-medium text-slate-500">
            Date From
          </label>
          <input
            type="date"
            value={filters.date_from ?? ""}
            onChange={(e) => update("date_from", e.target.value)}
            className="w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
          />
        </div>
        <div>
          <label className="mb-1.5 block text-xs font-medium text-slate-500">
            Date To
          </label>
          <input
            type="date"
            value={filters.date_to ?? ""}
            onChange={(e) => update("date_to", e.target.value)}
            className="w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
          />
        </div>

        {/* Dedup status */}
        <div>
          <label className="mb-1.5 block text-xs font-medium text-slate-500">
            Status
          </label>
          <div className="flex gap-1 rounded-lg bg-slate-100 p-1">
            {[
              { label: "All", value: "" },
              { label: "Key Only", value: "key_record" },
            ].map((opt) => (
              <button
                key={opt.value}
                onClick={() => update("unique_insight_status", opt.value)}
                className={`flex-1 rounded-md px-3 py-1.5 text-xs font-medium transition-colors ${
                  (filters.unique_insight_status ?? "") === opt.value
                    ? "bg-white text-slate-900 shadow-sm"
                    : "text-slate-500 hover:text-slate-700"
                }`}
              >
                {opt.label}
              </button>
            ))}
          </div>
        </div>

        <button
          onClick={clear}
          className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm font-medium text-slate-600 hover:bg-slate-50 transition-colors"
        >
          Clear All
        </button>
      </div>
    </div>
  );
}
