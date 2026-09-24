export interface User {
  user_id: number;
  signup_date: string;
  selected_categories: string[];
  is_synthetic_cold_demo: boolean;
}

export interface ProductItem {
  item_id: number;
  name: string;
  category_name: string;
  subcategory?: string;
  brand?: string;
  description?: string;
  price: number;
  image_url?: string;
  rating?: number;
  tags: string[];
  is_synthetic_cold_demo?: boolean;
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
  collaborative_score?: number;
  content_score?: number;
  relevance_score: number;
  business_score?: number;
  final_score: number;
  rank: number;
  explanation: string;
  recommendation_source: string;
  is_cold_start: boolean;
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
  updated_at: string;
}

export type RecommendationMode = 'pure' | 'business_aware';
