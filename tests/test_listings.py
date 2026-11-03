def test_lists_all_listings_in_id_order(client):
    response = client.get("/listings")
    assert response.status_code == 200
    assert [listing["id"] for listing in response.json()] == [1, 2, 3, 4]


def test_filters_by_category(client):
    titles = [listing["title"] for listing in client.get("/listings", params={"category": "bikes"}).json()]
    assert titles == ["Mountain bike, 21 speeds", "Road bike, carbon frame"]


def test_gets_one_listing(client):
    assert client.get("/listings/2").json()["city"] == "Montreal"


def test_unknown_listing_is_404(client):
    assert client.get("/listings/99").status_code == 404


def test_creates_a_listing(client):
    response = client.post(
        "/listings", json={"title": "Snow boots", "category": "clothing", "price_cents": 4000, "city": "Calgary"}
    )
    assert response.status_code == 201
    assert response.json()["id"] == 5


def test_rejects_a_negative_price(client):
    response = client.post(
        "/listings", json={"title": "Free couch", "category": "furniture", "price_cents": -1, "city": "Ottawa"}
    )
    assert response.status_code == 422
