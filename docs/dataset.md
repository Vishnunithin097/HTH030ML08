# Datasets & Model Artifacts Specification (Phase 2 Verified)

## 1. RetailRocket Dataset & Pretrained Artifacts

The RetailRocket dataset captures user implicit behavior events (`view`, `addtocart`, `transaction`) across catalog items.

### Pretrained Artifact Specifications:
* **Directory**: `models/RetailRocket/`
* **Artifacts & Properties**:
  * `svd_model.joblib`: `sklearn.decomposition.TruncatedSVD`
    * **Components**: $k = 100$
    * **Algorithm**: Randomized SVD
  * `user_factors.joblib`: `ndarray (float64)`
    * **Shape**: `(22141, 100)`
    * **Purpose**: Latent embeddings for frequent/active users.
  * `item_factors.joblib`: `ndarray (float64)`
    * **Shape**: `(56987, 100)`
    * **Purpose**: Latent embeddings for catalog items with sufficient interaction density.
  * `user_encoder.joblib`: `sklearn.preprocessing.LabelEncoder`
    * **Vocabulary Size**: `873,314` user IDs
    * **ID DataType**: `int64`
    * **Sample Raw User IDs**: `[0, 1, 2, 3, 4]`
  * `item_encoder.joblib`: `sklearn.preprocessing.LabelEncoder`
    * **Vocabulary Size**: `194,775` item IDs
    * **ID DataType**: `int64`
    * **Sample Raw Item IDs**: `[3, 4, 6, 15, 16]`

---

## 2. BigBasket Dataset & Pretrained Artifacts

The BigBasket dataset provides e-commerce retail catalog metadata with product titles, hierarchy, brands, and pricing.

### Pretrained Artifact Specifications:
* **Directory**: `models/BigBasket/`
* **Artifacts & Properties**:
  * `tfidf_vectorizer.joblib`: `sklearn.feature_extraction.text.TfidfVectorizer`
    * **Vocabulary Size**: `31,138` unique n-grams / tokens.
  * `tfidf_matrix.npz`: `scipy.sparse.csr_matrix`
    * **Shape**: `(23541, 31138)`
    * **Non-zero entries (nnz)**: `1,084,210`
    * **DataType**: `float64`
  * `product_metadata.parquet`: Apache Parquet dataframe
    * **Total Row Count**: `23,541` records
    * **Columns & Exact Types**:
      * `original_index` (`int64`): Original source row offset.
      * `product` (`str` / `object`): Full product title and descriptions.
      * `category` (`str` / `object`): 11 top-level categories (e.g. *Beauty & Hygiene*, *Kitchen, Garden & Pets*, *Cleaning & Household*, *Gourmet & World Food*, *Foodgrains, Oil & Masala*, *Snacks & Branded Foods*, *Beverages*, *Bakery, Cakes & Dairy*, *Baby Care*, *Fruits & Vegetables*).
      * `sub_category` (`str` / `object`): 90 granular subcategories.
      * `brand` (`str` / `object`): 2,266 unique brands.
      * `sale_price` (`float64`): Current selling price (₹3.00 to ₹12,500.00).
      * `market_price` (`float64`): MRP price (₹3.00 to ₹12,500.00).
      * `product_id` (`int64`): Zero-indexed identifier from `0` to `23,540`.
      * `margin_reference` (`float64`): Margin discount ratio `(market_price - sale_price) / market_price`.

---

## 3. Catalog Integration & Item Space Decision

### Problem Statement:
RetailRocket item IDs (`0` to `194,774`) and BigBasket product IDs (`0` to `23,540`) belong to **two entirely separate source datasets** with no shared natural key (e.g. UPC/EAN).

### Decision & Architecture:
1. **Zero False Equivalence**: Under no circumstances is `RetailRocket item_id == BigBasket product_id` assumed.
2. **Unified Catalog Manager (`backend/app/core/catalog.py`)**:
   * Internal Catalog Items (`items` table) store unified product definitions.
   * `CatalogManager` maps database `item_id` to its corresponding collaborative SVD index `(item_factors)` and/or content TF-IDF matrix row `(tfidf_matrix)`.
   * For BigBasket items (`item_id` in range 0..23,540), content TF-IDF is natively aligned.
   * For items with collaborative factors, `item_encoder.transform([item_id])` maps to the SVD factor index.
3. **Cold-Start Partitioning**:
   * Cold-start demo items (`item_id = 999999998`) and users (`user_id = 999999999`) have 0 interactions, explicit category tags, and are flagged `is_synthetic_cold_demo = TRUE`.
