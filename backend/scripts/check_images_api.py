"""Quick diagnostic: show image_url for each recommendation."""
import requests

r = requests.get("http://localhost:8000/recommendations", params={"user_id": "950063577", "n": 8})
data = r.json()
for item in data.get("recommendations", []):
    rank = item.get("rank", "?")
    name = (item.get("name") or "")[:40]
    cat = item.get("category_name", "")
    sub = item.get("subcategory", "")
    url = item.get("image_url", "")
    src = item.get("image_source", "")
    print(f"#{rank} {name:<40} | {cat} / {sub}")
    print(f"   image_url={url} [{src}]")
