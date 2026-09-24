"""
Product Image API Controller.
Exposes endpoints for product image lookup, source tracking, and image status reporting.
"""
from typing import Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.core.image_provider import image_provider

router = APIRouter(prefix="/images", tags=["Images"])


class ImageLookupResponse(BaseModel):
    product_id: int
    image_url: str
    source: str
    confidence: str
    image_status: str


@router.get("/product/{product_id}", response_model=ImageLookupResponse)
async def get_product_image_info(product_id: int):
    """
    Returns image metadata and resolved URL for a given product ID.
    """
    res = image_provider.resolve_product_image(product_id=product_id)
    return ImageLookupResponse(
        product_id=product_id,
        image_url=res["image_url"],
        source=res.get("image_source", "unknown"),
        confidence=res.get("match_confidence", "none"),
        image_status=res.get("image_status", "fallback"),
    )
