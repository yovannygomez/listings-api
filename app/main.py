"""A small marketplace listings API: the repository the ticket-to-pr
pipeline works on. Data lives in memory; the point is the code and its tests."""

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

app = FastAPI(title="Listings API")


class NewListing(BaseModel):
    title: str = Field(min_length=3, max_length=120)
    category: str
    price_cents: int = Field(ge=0)
    city: str


class Listing(NewListing):
    id: int


LISTINGS: dict[int, Listing] = {}


def seed() -> None:
    LISTINGS.clear()
    for item in [
        NewListing(title="Mountain bike, 21 speeds", category="bikes", price_cents=35000, city="Toronto"),
        NewListing(title="Sofa, three seats", category="furniture", price_cents=20000, city="Montreal"),
        NewListing(title="Road bike, carbon frame", category="bikes", price_cents=120000, city="Vancouver"),
        NewListing(title="Desk lamp", category="furniture", price_cents=1500, city="Toronto"),
    ]:
        create_listing(item)


@app.get("/listings")
def list_listings(
    category: str | None = None,
    min_price: int | None = Query(default=None, ge=0),
    max_price: int | None = Query(default=None, ge=0),
) -> list[Listing]:
    if min_price is not None and max_price is not None and min_price > max_price:
        raise HTTPException(status_code=422, detail="min_price must be less than or equal to max_price")
    listings = list(LISTINGS.values())
    if min_price is not None:
        listings = [x for x in listings if x.price_cents >= min_price]
    if max_price is not None:
        listings = [x for x in listings if x.price_cents <= max_price]
    if category is not None:
        listings = [listing for listing in listings if listing.category == category]
    return sorted(listings, key=lambda listing: listing.id)


@app.get("/listings/{listing_id}")
def get_listing(listing_id: int) -> Listing:
    if listing_id not in LISTINGS:
        raise HTTPException(status_code=404, detail="Listing not found")
    return LISTINGS[listing_id]


@app.post("/listings", status_code=201)
def create_listing(new: NewListing) -> Listing:
    listing = Listing(id=max(LISTINGS, default=0) + 1, **new.model_dump())
    LISTINGS[listing.id] = listing
    return listing


seed()
