export interface DashboardSummary {
  total_insights: number;
  key_records: number;
  total_accounts: number;
  sources_active: number;
}

export interface AreaCount {
  product_area: string;
  count: number;
}

export interface CategoryCount {
  insight_category: string;
  count: number;
}

export interface AccountCount {
  account_name: string;
  count: number;
}

export interface TrendPoint {
  week: string;
  count: number;
}
