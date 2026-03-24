export interface Insight {
  id: string;
  account_name: string;
  insight_text: string;
  product_area: string;
  product_subcategory: string;
  insight_category: string;
  input_data_source: string;
  source_tool: string;
  source_link: string;
  role_present?: string;
  date_of_record: string;
  unique_insight_status: string;
  dedup_group_key: string;
  created_at: string;
}

export interface InsightListResponse {
  items: Insight[];
  total: number;
  page: number;
  page_size: number;
}

export interface InsightFilters {
  product_area?: string;
  insight_category?: string;
  account_name?: string;
  date_from?: string;
  date_to?: string;
  unique_insight_status?: string;
  page?: number;
  page_size?: number;
}
