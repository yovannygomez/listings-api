def ids(response):
    return [listing["id"] for listing in response.json()]


def test_filters_by_city(client):
    response = client.get("/listings", params={"city": "Toronto"})
    assert response.status_code == 200
    assert ids(response) == [1, 4]
    assert [listing["title"] for listing in response.json()] == ["Mountain bike, 21 speeds", "Desk lamp"]


def test_city_filter_ignores_case(client):
    lower = client.get("/listings", params={"city": "toronto"})
    upper = client.get("/listings", params={"city": "Toronto"})
    assert lower.status_code == 200
    assert lower.json() == upper.json()
    assert ids(lower) == [1, 4]


def test_city_filter_ignores_surrounding_spaces_and_case(client):
    response = client.get("/listings?city=%20TORONTO%20")
    assert response.status_code == 200
    assert ids(response) == [1, 4]


def test_city_filter_montreal(client):
    response = client.get("/listings", params={"city": "Montreal"})
    assert response.status_code == 200
    assert ids(response) == [2]
    assert response.json()[0]["title"] == "Sofa, three seats"


def test_city_and_category_bikes(client):
    response = client.get("/listings", params={"city": "Toronto", "category": "bikes"})
    assert response.status_code == 200
    assert ids(response) == [1]


def test_city_lowercase_and_category_furniture(client):
    response = client.get("/listings", params={"city": "toronto", "category": "furniture"})
    assert response.status_code == 200
    assert ids(response) == [4]


def test_city_and_category_with_no_match_is_empty(client):
    response = client.get("/listings", params={"city": "Vancouver", "category": "furniture"})
    assert response.status_code == 200
    assert response.json() == []


def test_unknown_city_is_empty(client):
    response = client.get("/listings", params={"city": "Calgary"})
    assert response.status_code == 200
    assert response.json() == []


def test_city_must_match_exactly_not_partially(client):
    response = client.get("/listings?city=Greater%20Toronto")
    assert response.status_code == 200
    assert response.json() == []


def test_city_with_province_suffix_does_not_match(client):
    response = client.get("/listings?city=Toronto,%20ON")
    assert response.status_code == 200
    assert response.json() == []


def test_empty_city_is_rejected(client):
    assert client.get("/listings?city=").status_code == 422


def test_blank_city_is_rejected(client):
    assert client.get("/listings?city=%20%20%20").status_code == 422


def test_no_city_returns_all_listings_in_id_order(client):
    response = client.get("/listings")
    assert response.status_code == 200
    assert ids(response) == [1, 2, 3, 4]


def test_category_without_city_still_filters(client):
    response = client.get("/listings", params={"category": "bikes"})
    assert response.status_code == 200
    assert ids(response) == [1, 3]
