NEW_CHAIR = {"title": "Office chair", "category": "furniture", "price_cents": 5000, "city": "Toronto"}


def test_delete_returns_204_with_empty_body(client):
    response = client.delete("/listings/1")
    assert response.status_code == 204
    assert response.content == b""


def test_deleted_listing_is_404_on_get(client):
    client.delete("/listings/1")
    response = client.get("/listings/1")
    assert response.status_code == 404
    assert response.json()["detail"] == "Listing not found"


def test_deleted_listing_is_gone_from_the_list(client):
    client.delete("/listings/1")
    ids = [listing["id"] for listing in client.get("/listings").json()]
    assert ids == [2, 3, 4]
    assert 1 not in ids


def test_deleted_listing_is_gone_from_category_filter(client):
    client.delete("/listings/1")
    listings = client.get("/listings", params={"category": "bikes"}).json()
    assert [listing["id"] for listing in listings] == [3]
    assert [listing["title"] for listing in listings] == ["Road bike, carbon frame"]


def test_deleting_unknown_listing_is_404_and_changes_nothing(client):
    response = client.delete("/listings/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Listing not found"
    assert [listing["id"] for listing in client.get("/listings").json()] == [1, 2, 3, 4]


def test_deleting_twice_is_404_the_second_time(client):
    assert client.delete("/listings/2").status_code == 204
    assert client.delete("/listings/2").status_code == 404


def test_ids_are_not_reused_after_deleting_the_last_listing(client):
    assert client.delete("/listings/4").status_code == 204
    response = client.post("/listings", json=NEW_CHAIR)
    assert response.status_code == 201
    assert response.json()["id"] == 5


def test_ids_are_not_reused_after_deleting_every_listing(client):
    for listing_id in [1, 2, 3, 4]:
        assert client.delete(f"/listings/{listing_id}").status_code == 204
    response = client.post("/listings", json=NEW_CHAIR)
    assert response.status_code == 201
    assert response.json()["id"] == 5
    listings = client.get("/listings").json()
    assert [listing["id"] for listing in listings] == [5]


def test_deleting_one_listing_leaves_the_others_untouched(client):
    assert client.delete("/listings/2").status_code == 204
    assert client.get("/listings/1").json()["title"] == "Mountain bike, 21 speeds"
    assert client.get("/listings/3").json()["title"] == "Road bike, carbon frame"
    assert client.get("/listings/4").json()["title"] == "Desk lamp"


# The next two tests are meant to run in this order: the first leaves state
# behind (a deleted listing 4 and a new listing), the second checks that
# seed() in the client fixture fully resets it, including id numbering.
def test_reseed_setup_deletes_4_and_creates_a_listing(client):
    assert client.delete("/listings/4").status_code == 204
    assert client.post("/listings", json=NEW_CHAIR).status_code == 201


def test_seed_resets_deleted_listings_and_id_counter(client):
    assert [listing["id"] for listing in client.get("/listings").json()] == [1, 2, 3, 4]
    response = client.post("/listings", json=NEW_CHAIR)
    assert response.status_code == 201
    assert response.json()["id"] == 5


def test_non_integer_id_is_422(client):
    assert client.delete("/listings/abc").status_code == 422
