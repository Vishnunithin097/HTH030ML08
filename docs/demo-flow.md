# Hackathon Demo Flow & Presentation Script

## Step 1: Baseline Personalized Recommendations (Existing User)
1. Navigate to the **Dashboard**.
2. Select an existing user with high interaction volume from the user dropdown.
3. Observe **Pure Recommendation Mode** (relevance driven by Collaborative SVD).
4. Switch toggle to **Business-Aware Mode**: observe high-margin items with ample inventory promoted, while out-of-stock items are penalized or filtered.
5. Click **"Why Recommended?"** to view the signal-backed explanation modal (e.g. past category interactions and collaborative affinity).

---

## Step 2: The Cold-Start Challenge (New User Persona)
1. Navigate to **Cold-Start Demo**.
2. Select or create a brand-new user with 0 interaction history (e.g., Cold Start User `999999999` with preferences in "Sports & Fitness").
3. Inspect how the engine detects `interaction_count < threshold (3)` and seamlessly triggers the **Cold-Start Content & Popularity Resolver**.
4. Observe how user-selected categories drive the initial candidate generation without relying on collaborative embeddings.

---

## Step 3: Admin Business Guardrail Customization
1. Log in as **Admin** (`admin` / `Admin@123`).
2. Navigate to **Admin Config**.
3. Adjust sliders:
   * Increase `Margin Weight` ($w_{\text{margin}}$) to 0.60.
   * Enable `Hard Filtering` for items below $min\_inventory = 10$.
4. Save configuration.
5. Return to Dashboard and observe instant re-ranking reflecting the updated business policy without restarting or retraining the ML model.

---

## Step 4: Analytics & Business Impact Validation
1. Navigate to **Analytics**.
2. Review the comparative charts:
   * Pure Mode vs. Business-Aware Mode.
   * Cumulative margin gain vs. minimal NDCG tradeoff.
   * Category diversity distribution.
