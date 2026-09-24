"""
End-to-End Offline Recommendation & Guardrails Pipeline Demonstration.
Traces: User -> Cold Check -> CF -> Content -> Hybrid -> Guardrails -> Re-ranking -> Explanation.
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.catalog import catalog
from app.recommenders.hybrid import hybrid_recommender
from app.business.guardrails import GuardrailPolicy, guardrail_evaluator
from app.business.reranker import reranker
from app.business.revenue_impact import revenue_calculator
from app.explainability.explain import explainability_engine
from app.diversity.diversity import diversity_engine


def run_pipeline_demo():
    print("================================================================================")
    print("      END-TO-END RECOMMENDATION ENGINE & BUSINESS GUARDRAIL PIPELINE DEMO       ")
    print("================================================================================")

    # Initialize catalog
    catalog.initialize_from_metadata()
    policy = GuardrailPolicy(
        min_inventory=10,
        min_margin=20.0,
        relevance_weight=0.70,
        business_weight=0.30,
        margin_weight=0.40,
        inventory_weight=0.30,
        quality_weight=0.30,
        cold_start_threshold=3,
        hard_filter_enabled=False,
    )

    # -------------------------------------------------------------------------
    # TEST SCENARIO 1: Existing Warm Shopper (with interaction history)
    # -------------------------------------------------------------------------
    warm_user_id = 111016  # An existing RetailRocket user
    print(f"\n[SCENARIO 1] Personalized Recommendation for Warm Shopper (User #{warm_user_id})")
    print("--------------------------------------------------------------------------------")
    candidates_warm = hybrid_recommender.recommend(
        user_id=warm_user_id,
        interaction_count=15,
        interacted_item_ids=[0, 1, 4, 10],
        selected_categories=["Beauty & Hygiene", "Snacks & Branded Foods"],
        limit=5,
    )

    # 1. Pure Relevance Mode
    pure_warm, _ = reranker.rank(candidates_warm, mode="pure", policy=policy, top_k=5)
    print("  --> Pure Relevance Top-3:")
    for item in pure_warm[:3]:
        exp = explainability_engine.explain(item)
        print(f"      #{item['rank']} [ID: {item['item_id']:<5}] {item['name'][:35]:<35} | Rel: {item['relevance_score']:.3f} | Margin: {item['margin_pct']}% | Inv: {item['inventory_count']}")
        print(f"         Explanation: {exp}")

    # 2. Business-Aware Re-Ranked Mode
    guarded_warm, diag = reranker.rank(candidates_warm, mode="business_aware", policy=policy, top_k=5)
    print(f"\n  --> Business-Aware Re-Ranked Top-3 (Health: {diag['health_status']}, Churn: {diag['churn_count']}):")
    for item in guarded_warm[:3]:
        exp = explainability_engine.explain(item)
        print(f"      #{item['rank']} [ID: {item['item_id']:<5}] {item['name'][:35]:<35} | Final: {item['final_score']:.3f} (Rel: {item['relevance_score']:.3f}, Biz: {item['business_score']:.3f})")
        print(f"         Explanation: {exp}")

    # -------------------------------------------------------------------------
    # TEST SCENARIO 2: Cold-Start Shopper Persona (0 historical interactions)
    # -------------------------------------------------------------------------
    cold_user_id = 999999999
    print(f"\n[SCENARIO 2] Cold-Start Recommendation for New Shopper (User #{cold_user_id})")
    print("--------------------------------------------------------------------------------")
    candidates_cold = hybrid_recommender.recommend(
        user_id=cold_user_id,
        interaction_count=0,
        selected_categories=["Sports", "Running", "Fitness"],
        limit=5,
    )
    guarded_cold, _ = reranker.rank(candidates_cold, mode="business_aware", policy=policy, top_k=5)
    for item in guarded_cold[:3]:
        exp = explainability_engine.explain(item, user_category_preferences=["Sports"], is_cold_user=True)
        print(f"      #{item['rank']} [ID: {item['item_id']:<5}] {item['name'][:35]:<35} | Final: {item['final_score']:.3f} | ColdStart: {item['is_cold_start']}")
        print(f"         Explanation: {exp}")

    # -------------------------------------------------------------------------
    # TEST SCENARIO 3: Cold-Start Item Ingestion & Counterfactual Simulation
    # -------------------------------------------------------------------------
    cold_item_id = 999999998
    print(f"\n[SCENARIO 3] Cold-Start Item Evaluation & Counterfactual Simulation (Item #{cold_item_id})")
    print("--------------------------------------------------------------------------------")
    cold_item = catalog.get_item(cold_item_id)
    print(f"  Item: '{cold_item.name}' | Price: Rs.{cold_item.price} | Margin: {cold_item.margin_pct}% | Inventory: {cold_item.inventory_count}")

    # Sensitivity Counterfactual Analysis
    cf_res = guardrail_evaluator.evaluate_counterfactual(
        relevance_score=0.75,
        margin_pct=cold_item.margin_pct,
        inventory_count=cold_item.inventory_count,
        quality_score=cold_item.quality_score,
        current_final_score=0.72,
        hypothetical_min_margin=40.0,  # Strict hypothetical margin floor
        hypothetical_inventory_count=5,  # Low inventory scenario
        policy=policy,
    )
    print(f"  Counterfactual Simulation:")
    print(f"    - Base Score: {cf_res['baseline_score']} -> Simulated Score: {cf_res['simulated_score']} ({cf_res['score_delta']:+.3f})")
    print(f"    - Penalties Triggered: {cf_res['reasons']}")
    print(f"    - {cf_res['summary']}")

    # -------------------------------------------------------------------------
    # TEST SCENARIO 4: Financial Revenue Impact & Diversity Evaluation
    # -------------------------------------------------------------------------
    print(f"\n[SCENARIO 4] Financial Impact Projection & Diversity Analysis")
    print("--------------------------------------------------------------------------------")
    sim = revenue_calculator.simulate_impact(pure_warm, guarded_warm, assumed_impressions=1000)
    print(f"  Commercial Simulation:")
    print(f"    - Pure Mode Projected Margin: Rs.{sim['pure_mode']['projected_margin_inr']} ({sim['pure_mode']['avg_margin_pct']}%)")
    print(f"    - Business-Aware Margin: Rs.{sim['business_aware_mode']['projected_margin_inr']} ({sim['business_aware_mode']['avg_margin_pct']}%)")
    print(f"    - Projected Margin Lift: {sim['projected_margin_lift_pct']:+.2f}%")

    div_score = diversity_engine.compute_intra_list_diversity(guarded_warm)
    print(f"  Intra-List Category Diversity: {div_score:.2f}")

    print("\n================================================================================")
    print("            OFFLINE PIPELINE DEMONSTRATION EXECUTED SUCCESSFULLY!               ")
    print("================================================================================")


if __name__ == "__main__":
    run_pipeline_demo()
