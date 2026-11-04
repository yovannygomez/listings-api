def ids(response):
    return [listing["id"] for listing in response.json()]


def test_filters_by_city(client):
    response = client.get("/listings", params={"city": "Toronto"})
    assert response.status_code == 200
    assert ids(response) == [1, 4]


def test_city_filter_is_case_insensitive_lowercase(client):
    response = client.get("/listings", params={"city": "toronto"})
    assert response.status_code == 200
    assert ids(response) == [1, 4]


def test_city_filter_is_case_insensitive_uppercase(client):
    response = client.get("/listings", params={"city": "TORONTO"})
    assert response.status_code == 200
    assert ids(response) == [1, 4]


def test_city_and_category_bikes(client):
    assert ids(client.get("/listings", params={"city": "Toronto", "category": "bikes"})) == [1]


def test_city_lowercase_and_category_furniture(client):
    assert ids(client.get("/listings", params={"city": "toronto", "category": "furniture"})) == [4]


def test_city_and_category_with_no_match(client):
    response = client.get("/listings", params={"city": "Vancouver", "category": "furniture"})
    assert response.status_code == 200
    assert response.json() == []


def test_unknown_city_returns_empty_list(client):
    response = client.get("/listings", params={"city": "Calgary"})
    assert response.status_code == 200
    assert response.json() == []


def test_partial_city_name_does_not_match(client):
    response = client.get("/listings", params={"city": "Toron"})
    assert response.status_code == 200
    assert response.json() == []


def test_city_with_leading_space_does_not_match(client):
    response = client.get("/listings?city=%20Toronto")
    assert response.status_code == 200
    assert response.json() == []


def test_empty_city_returns_empty_list(client):
    response = client.get("/listings?city=")
    assert response.status_code == 200
    assert response.json() == []


def test_no_city_lists_all_listings_unchanged(client):
    assert ids(client.get("/listings")) == [1, 2, 3, 4]


def test_category_without_city_unchanged(client):
    assert ids(client.get("/listings", params={"category": "bikes"})) == [1, 3]


def test_created_listing_keeps_city_casing_and_is_found_case_insensitively(client):
    created = client.post(
        "/listings", json={"title": "Cargo bike", "category": "bikes", "price_cents": 90000, "city": "TORONTO"}
    )
    assert created.status_code == 201
    assert created.json()["id"] == 5
    response = client.get("/listings", params={"city": "toronto"})
    assert ids(response) == [1, 4, 5]
    assert response.json()[2]["city"] == "TORONTO"
