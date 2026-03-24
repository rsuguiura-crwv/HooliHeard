import { useQuery } from "@tanstack/react-query";
import type { Insight, InsightFilters, InsightListResponse } from "@/types/insight";

// ---- Mock data ----

const MOCK_INSIGHTS: Insight[] = [
  {
    id: "ins-001",
    account_name: "Anthropic",
    insight_text:
      "Need better GPU node scheduling for large model training runs. Current queue times are 15+ minutes during peak hours which significantly impacts iteration speed for our research team.",
    product_area: "Infra",
    product_subcategory: "GPU Scheduling",
    insight_category: "Performance Issue",
    input_data_source: "Customer call transcript",
    source_tool: "gong",
    source_link: "https://app.gong.io/call/12345",
    role_present: "ML Platform Lead",
    date_of_record: "2026-03-18",
    unique_insight_status: "key_record",
    dedup_group_key: "gpu-scheduling-latency",
    created_at: "2026-03-18T14:30:00Z",
  },
  {
    id: "ins-002",
    account_name: "Meta",
    insight_text:
      "Kubernetes cluster autoscaling doesn't handle our bursty inference workloads well. We need faster scale-up from zero for serverless GPU endpoints.",
    product_area: "CKS",
    product_subcategory: "Autoscaling",
    insight_category: "Feature Request",
    input_data_source: "Support ticket",
    source_tool: "salesforce",
    source_link: "https://coreweave.my.salesforce.com/5001234",
    role_present: "Infrastructure Engineer",
    date_of_record: "2026-03-15",
    unique_insight_status: "key_record",
    dedup_group_key: "k8s-autoscale-bursty",
    created_at: "2026-03-15T10:00:00Z",
  },
  {
    id: "ins-003",
    account_name: "Microsoft",
    insight_text:
      "The platform API for managing virtual servers lacks proper pagination and filtering. When we have 500+ instances, listing them becomes unusable.",
    product_area: "Platform",
    product_subcategory: "API",
    insight_category: "API Enhancement",
    input_data_source: "Slack conversation",
    source_tool: "slack",
    source_link: "https://coreweave.slack.com/archives/C123/p456",
    role_present: "DevOps Lead",
    date_of_record: "2026-03-12",
    unique_insight_status: "key_record",
    dedup_group_key: "api-pagination",
    created_at: "2026-03-12T09:15:00Z",
  },
  {
    id: "ins-004",
    account_name: "Cohere",
    insight_text:
      "We'd love to see W&B experiment tracking integrated directly into the CoreWeave ML pipeline. Currently we have to set up the integration ourselves on every new project.",
    product_area: "W&B",
    product_subcategory: "Integration",
    insight_category: "Integration Need",
    input_data_source: "Customer feedback survey",
    source_tool: "qualtrics",
    source_link: "https://coreweave.qualtrics.com/response/789",
    date_of_record: "2026-03-10",
    unique_insight_status: "key_record",
    dedup_group_key: "wandb-pipeline-integration",
    created_at: "2026-03-10T16:00:00Z",
  },
  {
    id: "ins-005",
    account_name: "Mistral AI",
    insight_text:
      "Inference endpoint cold starts are too slow for our production use case. We need the ability to keep warm replicas without paying for full GPU allocation.",
    product_area: "AI Services",
    product_subcategory: "Inference",
    insight_category: "Feature Request",
    input_data_source: "Customer call transcript",
    source_tool: "gong",
    source_link: "https://app.gong.io/call/67890",
    role_present: "CTO",
    date_of_record: "2026-03-08",
    unique_insight_status: "key_record",
    dedup_group_key: "inference-cold-start",
    created_at: "2026-03-08T11:30:00Z",
  },
  {
    id: "ins-006",
    account_name: "Anthropic",
    insight_text:
      "GPU scheduling delays are a major blocker for us. We lose hours of compute time waiting for nodes to become available during our training windows.",
    product_area: "Infra",
    product_subcategory: "GPU Scheduling",
    insight_category: "Performance Issue",
    input_data_source: "Slack conversation",
    source_tool: "slack",
    source_link: "https://coreweave.slack.com/archives/C789/p012",
    role_present: "ML Engineer",
    date_of_record: "2026-03-20",
    unique_insight_status: "duplicate",
    dedup_group_key: "gpu-scheduling-latency",
    created_at: "2026-03-20T08:45:00Z",
  },
  {
    id: "ins-007",
    account_name: "Inflection AI",
    insight_text:
      "Documentation for setting up multi-node training with InfiniBand is incomplete. We had to figure out NCCL environment variables through trial and error.",
    product_area: "Infra",
    product_subcategory: "Documentation",
    insight_category: "Documentation Gap",
    input_data_source: "Support ticket",
    source_tool: "jira",
    source_link: "https://coreweave.atlassian.net/browse/SUP-4567",
    role_present: "Senior ML Engineer",
    date_of_record: "2026-03-05",
    unique_insight_status: "key_record",
    dedup_group_key: "infiniband-docs",
    created_at: "2026-03-05T13:00:00Z",
  },
  {
    id: "ins-008",
    account_name: "Stability AI",
    insight_text:
      "We need SOC 2 Type II compliance reports readily available. Our security team requires these for vendor assessment and it's been difficult to get them.",
    product_area: "Platform",
    product_subcategory: "Compliance",
    insight_category: "Compliance Need",
    input_data_source: "Customer call transcript",
    source_tool: "gong",
    source_link: "https://app.gong.io/call/11111",
    role_present: "CISO",
    date_of_record: "2026-03-01",
    unique_insight_status: "key_record",
    dedup_group_key: "soc2-compliance",
    created_at: "2026-03-01T15:20:00Z",
  },
  {
    id: "ins-009",
    account_name: "Character.AI",
    insight_text:
      "The pricing model for reserved GPU instances doesn't work for us. We need more flexibility — something between on-demand and 1-year commitments.",
    product_area: "Platform",
    product_subcategory: "Pricing",
    insight_category: "Pricing Concern",
    input_data_source: "Customer feedback survey",
    source_tool: "qualtrics",
    source_link: "https://coreweave.qualtrics.com/response/222",
    date_of_record: "2026-02-28",
    unique_insight_status: "key_record",
    dedup_group_key: "pricing-flexibility",
    created_at: "2026-02-28T10:00:00Z",
  },
  {
    id: "ins-010",
    account_name: "Runway ML",
    insight_text:
      "Onboarding new team members to CoreWeave is painful. The initial setup requires too many manual steps and there's no guided getting-started experience.",
    product_area: "Platform",
    product_subcategory: "Onboarding",
    insight_category: "Onboarding Friction",
    input_data_source: "Slack conversation",
    source_tool: "slack",
    source_link: "https://coreweave.slack.com/archives/C456/p789",
    role_present: "Engineering Manager",
    date_of_record: "2026-02-25",
    unique_insight_status: "key_record",
    dedup_group_key: "onboarding-pain",
    created_at: "2026-02-25T14:10:00Z",
  },
  {
    id: "ins-011",
    account_name: "Hugging Face",
    insight_text:
      "We need the ability to migrate running workloads between GPU types without downtime. Our model serving needs change and redeploying means downtime.",
    product_area: "AI Services",
    product_subcategory: "Workload Management",
    insight_category: "Migration Blocker",
    input_data_source: "Customer call transcript",
    source_tool: "gong",
    source_link: "https://app.gong.io/call/33333",
    role_present: "Platform Lead",
    date_of_record: "2026-02-20",
    unique_insight_status: "key_record",
    dedup_group_key: "live-migration",
    created_at: "2026-02-20T11:00:00Z",
  },
  {
    id: "ins-012",
    account_name: "Meta",
    insight_text:
      "We need the Kubernetes autoscaler to handle scale-from-zero much faster. Current 3-5 minute cold start for new nodes kills our SLAs.",
    product_area: "CKS",
    product_subcategory: "Autoscaling",
    insight_category: "Feature Request",
    input_data_source: "Customer call transcript",
    source_tool: "gong",
    source_link: "https://app.gong.io/call/44444",
    role_present: "SRE Lead",
    date_of_record: "2026-03-21",
    unique_insight_status: "duplicate",
    dedup_group_key: "k8s-autoscale-bursty",
    created_at: "2026-03-21T09:30:00Z",
  },
  {
    id: "ins-013",
    account_name: "Anthropic",
    insight_text:
      "The W&B integration for tracking distributed training runs across multiple nodes loses data when a node goes down. Need checkpoint-level metric persistence.",
    product_area: "W&B",
    product_subcategory: "Reliability",
    insight_category: "Bug Report",
    input_data_source: "Jira ticket",
    source_tool: "jira",
    source_link: "https://coreweave.atlassian.net/browse/SUP-5678",
    role_present: "ML Platform Engineer",
    date_of_record: "2026-03-14",
    unique_insight_status: "key_record",
    dedup_group_key: "wandb-metric-loss",
    created_at: "2026-03-14T16:45:00Z",
  },
  {
    id: "ins-014",
    account_name: "Cohere",
    insight_text:
      "Security groups and network policies are hard to configure in CKS. We need a simpler abstraction — maybe namespace-level network policies with sensible defaults.",
    product_area: "CKS",
    product_subcategory: "Networking",
    insight_category: "Security Requirement",
    input_data_source: "Support ticket",
    source_tool: "salesforce",
    source_link: "https://coreweave.my.salesforce.com/5005678",
    role_present: "Security Engineer",
    date_of_record: "2026-03-07",
    unique_insight_status: "key_record",
    dedup_group_key: "cks-network-policy",
    created_at: "2026-03-07T10:30:00Z",
  },
  {
    id: "ins-015",
    account_name: "Mistral AI",
    insight_text:
      "The AI Services dashboard UX is confusing. It's hard to find which endpoints are active vs. idle and how much each is costing us.",
    product_area: "AI Services",
    product_subcategory: "Dashboard",
    insight_category: "UX Improvement",
    input_data_source: "Customer feedback survey",
    source_tool: "qualtrics",
    source_link: "https://coreweave.qualtrics.com/response/555",
    date_of_record: "2026-03-03",
    unique_insight_status: "key_record",
    dedup_group_key: "ai-services-ux",
    created_at: "2026-03-03T12:00:00Z",
  },
];

const USE_MOCK = true;

function delay<T>(data: T, ms = 300): Promise<T> {
  return new Promise((resolve) => setTimeout(() => resolve(data), ms));
}

function filterMockInsights(filters: InsightFilters): InsightListResponse {
  let filtered = [...MOCK_INSIGHTS];

  if (filters.product_area) {
    filtered = filtered.filter((i) => i.product_area === filters.product_area);
  }
  if (filters.insight_category) {
    filtered = filtered.filter(
      (i) => i.insight_category === filters.insight_category,
    );
  }
  if (filters.account_name) {
    filtered = filtered.filter((i) =>
      i.account_name.toLowerCase().includes(filters.account_name!.toLowerCase()),
    );
  }
  if (filters.unique_insight_status) {
    filtered = filtered.filter(
      (i) => i.unique_insight_status === filters.unique_insight_status,
    );
  }
  if (filters.date_from) {
    filtered = filtered.filter((i) => i.date_of_record >= filters.date_from!);
  }
  if (filters.date_to) {
    filtered = filtered.filter((i) => i.date_of_record <= filters.date_to!);
  }

  const page = filters.page ?? 1;
  const pageSize = filters.page_size ?? 20;
  const start = (page - 1) * pageSize;
  const items = filtered.slice(start, start + pageSize);

  return {
    items,
    total: filtered.length,
    page,
    page_size: pageSize,
  };
}

// ---- Hooks ----

export function useInsights(filters: InsightFilters) {
  return useQuery<InsightListResponse>({
    queryKey: ["insights", filters],
    queryFn: () => {
      if (USE_MOCK) return delay(filterMockInsights(filters));
      return import("@/api/insights").then((m) => m.fetchInsights(filters));
    },
  });
}

export function useInsight(id: string | null) {
  return useQuery<Insight | null>({
    queryKey: ["insight", id],
    enabled: !!id,
    queryFn: () => {
      if (USE_MOCK) {
        const found = MOCK_INSIGHTS.find((i) => i.id === id) ?? null;
        return delay(found);
      }
      return import("@/api/insights").then((m) => m.fetchInsight(id!));
    },
  });
}
