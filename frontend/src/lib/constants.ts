export const PRODUCT_AREAS = [
  { label: "Infra", value: "Infra", color: "#3B82F6" },
  { label: "CKS", value: "CKS", color: "#10B981" },
  { label: "Platform", value: "Platform", color: "#F59E0B" },
  { label: "AI Services", value: "AI Services", color: "#8B5CF6" },
  { label: "W&B", value: "W&B", color: "#EC4899" },
] as const;

export const PRODUCT_AREA_COLORS: Record<string, string> = {
  Infra: "#3B82F6",
  CKS: "#10B981",
  Platform: "#F59E0B",
  "AI Services": "#8B5CF6",
  "W&B": "#EC4899",
};

export const INSIGHT_CATEGORIES = [
  "Feature Request",
  "Bug Report",
  "Performance Issue",
  "Pricing Concern",
  "Documentation Gap",
  "Onboarding Friction",
  "Integration Need",
  "Scalability Concern",
  "Security Requirement",
  "UX Improvement",
  "API Enhancement",
  "Compliance Need",
  "Migration Blocker",
] as const;

export const SOURCE_TOOLS: Record<
  string,
  { icon: string; color: string; label: string }
> = {
  gong: { icon: "G", color: "#7C3AED", label: "Gong" },
  salesforce: { icon: "S", color: "#00A1E0", label: "Salesforce" },
  jira: { icon: "J", color: "#0052CC", label: "Jira" },
  slack: { icon: "#", color: "#E01E5A", label: "Slack" },
  qualtrics: { icon: "Q", color: "#1BAD4F", label: "Qualtrics" },
};
