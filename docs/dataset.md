# Datasets & Model Artifacts Specification

## 1. RetailRocket Dataset & Pretrained Artifacts

RetailRocket represents sequential e-commerce user behavior logs (views, addtocarts, transactions).

* **Directory**: `models/RetailRocket/`
* **Artifacts**:
  * `svd_model.joblib`: `sklearn.decomposition.TruncatedSVD` trained with $k=100$ latent components.
  * `user_factors.joblib`: Matrix of shape `(22141, 100)` containing latent factors for frequent users.
  * `item_factors.joblib`: Matrix of shape `(56987, 100)` containing latent factors for catalog items.
  * `user_encoder.joblib`: `LabelEncoder` mapping `873,314` raw user IDs to internal index slots.
  * `item_encoder.joblib`: `LabelEncoder` mapping `194,775` raw item IDs to internal index slots.

---

## 2. BigBasket Dataset & Pretrained Artifacts

BigBasket provides grocery and retail catalog metadata including titles, categories, subcategories, brands, and prices.

* **Directory**: `models/BigBasket/`
* **Artifacts**:
  * `tfidf_vectorizer.joblib`: `TfidfVectorizer` with a fitted vocabulary of `31,138` n-grams.
  * `tfidf_matrix.npz`: Scipy CSR sparse matrix `(23541, 31138)` containing 1,084,210 non-zero feature entries.
  * `product_metadata.parquet`: `23,541` product records containing:
    * `original_index`
    * `product` (title/description)
    * `category` (11 high-level categories)
    * `sub_category` (90 granular subcategories)
    * `brand`
    * `sale_price`
    * `market_price`
    * `product_id`
    * `margin_reference`

---

## 3. Catalog Integration & Item Space Mapping

* **No Direct ID Overlap**: RetailRocket item IDs and BigBasket product IDs are distinct entity spaces.
* **Unified Catalog Layer**: `backend/app/core/catalog.py` maintains an internal catalog registry mapping database entities (`items`) to their corresponding collaborative embedding index and/or content feature vector.
