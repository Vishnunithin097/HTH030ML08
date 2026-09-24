export interface User {
  user_id: number;
  signup_date?: string;
  selected_categories: string[];
  is_synthetic_cold_demo: boolean;
}

export interface CatalogItemResponse {
  item_id: number;
  name: string;
  category_name: string;
  subcategory?: string;
  brand?: string;
  description?: string;
  price: number;
  margin_pct?: number;
  inventory_count?: number;
  quality_score?: number;
  tags: string[];
  is_synthetic_cold_demo: boolean;
}

export interface RecommendationItem {
  item_id: number;
  name?: string;
  category_name?: string;
  subcategory?: string;
  brand?: string;
  price?: number;
  image_url?: string;
  rating?: number;
  margin_pct?: number;
  inventory_count?: number;
  quality_score?: number;
  collaborative_score?: number | null;
  content_score?: number | null;
  relevance_score: number;
  business_score?: number | null;
  penalty_score?: number;
  final_score: number;
  rank: number;
  explanation: string;
  recommendation_source: string;
  is_cold_start: boolean;
  penalty_reasons?: string[];
}

export interface GuardrailHealthSummary {
  mode: string;
  top_k: number;
  churn_count: number;
  filtered_items_count: number;
  suppression_rate: number;
  health_status: 'healthy' | 'moderate_churn' | 'warning_high_suppression' | string;
  health_message: string;
}

export interface GMVProjectionSummary {
  projected_gmv: number;
  projected_margin_inr: number;
  avg_margin_pct: number;
  stockout_risk_items: number;
}

export interface RecommendationResponse {
  request_id: string;
  user_id: number;
  mode: 'pure' | 'business_aware';
  cold_start: boolean;
  cold_start_type?: string | null;
  interaction_count: number;
  total_recommendations: number;
  guardrail_health: GuardrailHealthSummary;
  gmv_projection: GMVProjectionSummary;
  recommendations: RecommendationItem[];
}

export interface ExplanationResponse {
  item_id: number;
  user_id: number;
  name: string;
  category_name: string;
  brand?: string;
  relevance_score: number;
  business_score?: number | null;
  collaborative_score?: number | null;
  content_score?: number | null;
  margin_pct?: number;
  inventory_count?: number;
  quality_score?: number;
  explanation: string;
  signal_breakdown: Record<string, any>;
}

export interface CounterfactualResponse {
  item_id: number;
  user_id: number;
  baseline_score: number;
  simulated_score: number;
  score_delta: number;
  simulated_business_score: number;
  simulated_penalty: number;
  reasons: string[];
  summary: string;
}

export interface GuardrailConfig {
  config_id: number;
  min_inventory: number;
  min_margin: number;
  relevance_weight: number;
  business_weight: number;
  margin_weight: number;
  inventory_weight: number;
  quality_weight: number;
  cold_start_threshold: number;
  hard_filter_enabled: boolean;
  updated_at?: string;
}

export interface RankingMetricsResponse {
  metric_type: string;
  ndcg_at_10: number;
  precision_at_10: number;
  recall_at_10: number;
  mean_average_precision: number;
  evaluated_slate_size: number;
  ground_truth_set_size: number;
  status: string;
}

export interface BusinessMetricsResponse {
  metric_type: string;
  pure_mode_avg_margin_pct: number;
  business_aware_avg_margin_pct: number;
  projected_margin_lift_pct: number;
  pure_stockout_risk_rate: number;
  guarded_stockout_risk_rate: number;
  stockout_reduction_pct: number;
  guardrail_health_status: string;
  guardrail_churn_count: number;
  status: string;
}

export interface DiversityMetricsResponse {
  metric_type: string;
  intra_list_diversity: number;
  shannon_entropy: number;
  unique_categories_in_slate: number;
  total_catalog_categories: number;
  category_coverage_pct: number;
  status: string;
}

export type RecommendationMode = 'pure' | 'business_aware';
