import { DataTable } from "@/components/shared/DataTable";
import { Badge } from "@/components/shared/Badge";
import { PRODUCT_AREA_COLORS, SOURCE_TOOLS } from "@/lib/constants";
import { truncate, formatDate } from "@/lib/utils";
import type { Column } from "@/components/shared/DataTable";
import type { Insight } from "@/types/insight";

interface Props {
  data: Insight[];
  loading: boolean;
  onSelect: (insight: Insight) => void;
}

const columns: Column<Insight>[] = [
  {
    key: "account",
    header: "Account",
    width: "140px",
    render: (row) => (
      <span className="font-medium text-slate-900">{row.account_name}</span>
    ),
  },
  {
    key: "insight",
    header: "Insight",
    render: (row) => (
      <span className="text-slate-600">{truncate(row.insight_text, 100)}</span>
    ),
  },
  {
    key: "area",
    header: "Area",
    width: "120px",
    render: (row) => (
      <Badge
        label={row.product_area}
        color={PRODUCT_AREA_COLORS[row.product_area]}
        variant="subtle"
      />
    ),
  },
  {
    key: "category",
    header: "Category",
    width: "150px",
    render: (row) => (
      <span className="text-xs text-slate-600">{row.insight_category}</span>
    ),
  },
  {
    key: "source",
    header: "Source",
    width: "80px",
    render: (row) => {
      const tool = SOURCE_TOOLS[row.source_tool];
      if (\!tool) return <span className="text-xs text-slate-500">{row.source_tool}</span>;
      return (
        <span
          className="inline-flex h-6 w-6 items-center justify-center rounded text-[10px] font-bold text-white"
          style={{ backgroundColor: tool.color }}
          title={tool.label}
        >
          {tool.icon}
        </span>
      );
    },
  },
  {
    key: "date",
    header: "Date",
    width: "110px",
    sortable: true,
    sortKey: (row) => row.date_of_record,
    render: (row) => (
      <span className="text-xs text-slate-500 tabular-nums">
        {formatDate(row.date_of_record)}
      </span>
    ),
  },
  {
    key: "status",
    header: "Status",
    width: "100px",
    render: (row) =>
      row.unique_insight_status === "key_record" ? (
        <Badge label="Key" color="#10B981" variant="subtle" />
      ) : (
        <Badge label="Duplicate" color="#94a3b8" variant="subtle" />
      ),
  },
];

export function InsightTable({ data, loading, onSelect }: Props) {
  return (
    <div className="card overflow-hidden">
      <DataTable
        columns={columns}
        data={data}
        loading={loading}
        onRowClick={onSelect}
        emptyMessage="No insights match your filters"
      />
    </div>
  );
}
