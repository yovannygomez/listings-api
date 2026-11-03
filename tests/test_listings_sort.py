import pytest


def ids(client, **params):
    response = client.get("/listings", params=params)
    assert response.status_code == 200
    return [listing["id"] for listing in response.json()]


def test_no_sort_keeps_id_order(client):
    assert ids(client) == [1, 2, 3, 4]


def test_sort_price_asc(client):
    assert ids(client, sort="price_asc") == [4, 2, 1, 3]


def test_sort_price_desc(client):
    assert ids(client, sort="price_desc") == [3, 1, 2, 4]


def test_bikes_price_asc(client):
    assert ids(client, category="bikes", sort="price_asc") == [1, 3]


def test_bikes_price_desc(client):
    assert ids(client, category="bikes", sort="price_desc") == [3, 1]


def test_furniture_price_asc(client):
    assert ids(client, category="furniture", sort="price_asc") == [4, 2]


def test_furniture_price_desc(client):
    assert ids(client, category="furniture", sort="price_desc") == [2, 4]


def test_equal_prices_stay_in_id_order_in_both_directions(client):
    response = client.post(
        "/listings", json={"title": "Kids bike", "category": "bikes", "price_cents": 35000, "city": "Toronto"}
    )
    assert response.status_code == 201
    assert response.json()["id"] == 5
    assert ids(client, sort="price_asc") == [4, 2, 1, 5, 3]
    assert ids(client, sort="price_desc") == [3, 1, 5, 2, 4]


@pytest.mark.parametrize("value", ["name", "", "PRICE_ASC"])
def test_invalid_sort_is_422(client, value):
    assert client.get("/listings", params={"sort": value}).status_code == 422


def test_invalid_sort_with_category_is_422(client):
    assert client.get("/listings", params={"category": "bikes", "sort": "bogus"}).status_code == 422


def test_unknown_category_with_sort_is_empty(client):
    response = client.get("/listings", params={"category": "toys", "sort": "price_asc"})
    assert response.status_code == 200
    assert response.json() == []
