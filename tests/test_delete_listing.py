from app.main import seed

NEW_CHAIR = {"title": "Office chair", "category": "furniture", "price_cents": 5000, "city": "Ottawa"}

SEEDED = {
    1: {"id": 1, "title": "Mountain bike, 21 speeds", "category": "bikes", "price_cents": 35000, "city": "Toronto"},
    3: {"id": 3, "title": "Road bike, carbon frame", "category": "bikes", "price_cents": 120000, "city": "Vancouver"},
    4: {"id": 4, "title": "Desk lamp", "category": "furniture", "price_cents": 1500, "city": "Toronto"},
}


def test_delete_returns_204_with_empty_body(client):
    response = client.delete("/listings/2")
    assert response.status_code == 204
    assert response.content == b""


def test_deleted_listing_is_404_on_get(client):
    client.delete("/listings/2")
    response = client.get("/listings/2")
    assert response.status_code == 404
    assert response.json()["detail"] == "Listing not found"


def test_deleted_listing_disappears_from_list(client):
    client.delete("/listings/2")
    assert [listing["id"] for listing in client.get("/listings").json()] == [1, 3, 4]


def test_deleted_listing_disappears_from_category_filter(client):
    client.delete("/listings/1")
    listings = client.get("/listings", params={"category": "bikes"}).json()
    assert [listing["id"] for listing in listings] == [3]
    assert listings[0]["title"] == "Road bike, carbon frame"


def test_deleting_unknown_listing_is_404(client):
    response = client.delete("/listings/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Listing not found"


def test_deleting_twice_is_404_the_second_time(client):
    assert client.delete("/listings/2").status_code == 204
    assert client.delete("/listings/2").status_code == 404


def test_ids_are_not_reused_after_deleting_the_newest_listing(client):
    client.delete("/listings/4")
    response = client.post("/listings", json=NEW_CHAIR)
    assert response.status_code == 201
    assert response.json()["id"] == 5
    assert client.get("/listings/4").status_code == 404


def test_next_id_is_5_after_deleting_every_listing(client):
    for listing_id in (1, 2, 3, 4):
        assert client.delete(f"/listings/{listing_id}").status_code == 204
    assert client.get("/listings").json() == []
    response = client.post("/listings", json=NEW_CHAIR)
    assert response.status_code == 201
    assert response.json()["id"] == 5


def test_other_listings_are_unchanged_after_a_delete(client):
    assert client.delete("/listings/2").status_code == 204
    for listing_id, expected in SEEDED.items():
        response = client.get(f"/listings/{listing_id}")
        assert response.status_code == 200
        assert response.json() == expected


def test_non_integer_id_is_422(client):
    assert client.delete("/listings/abc").status_code == 422


def test_seed_after_delete_restores_listings_and_resets_next_id(client):
    assert client.delete("/listings/2").status_code == 204
    seed()
    assert [listing["id"] for listing in client.get("/listings").json()] == [1, 2, 3, 4]
    assert client.post("/listings", json=NEW_CHAIR).json()["id"] == 5
