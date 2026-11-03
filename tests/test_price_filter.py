MIN_MAX_DETAIL = {"detail": "min_price must be less than or equal to max_price"}


def ids(response):
    return [listing["id"] for listing in response.json()]


def test_no_params_returns_all_listings(client):
    response = client.get("/listings")
    assert response.status_code == 200
    assert ids(response) == [1, 2, 3, 4]


def test_category_without_price_params_is_unchanged(client):
    response = client.get("/listings", params={"category": "bikes"})
    assert response.status_code == 200
    assert ids(response) == [1, 3]


def test_min_price_is_inclusive(client):
    response = client.get("/listings", params={"min_price": 20000})
    assert response.status_code == 200
    assert ids(response) == [1, 2, 3]


def test_max_price_is_inclusive(client):
    response = client.get("/listings", params={"max_price": 20000})
    assert response.status_code == 200
    assert ids(response) == [2, 4]


def test_min_and_max_price_bounds_are_inclusive(client):
    response = client.get("/listings", params={"min_price": 1500, "max_price": 35000})
    assert response.status_code == 200
    assert ids(response) == [1, 2, 4]


def test_category_with_min_price(client):
    response = client.get("/listings", params={"category": "bikes", "min_price": 100000})
    assert response.status_code == 200
    assert ids(response) == [3]


def test_category_with_max_price(client):
    response = client.get("/listings", params={"category": "furniture", "max_price": 1500})
    assert response.status_code == 200
    assert ids(response) == [4]


def test_equal_min_and_max_price(client):
    response = client.get("/listings", params={"min_price": 20000, "max_price": 20000})
    assert response.status_code == 200
    assert ids(response) == [2]


def test_min_price_zero_returns_all(client):
    response = client.get("/listings", params={"min_price": 0})
    assert response.status_code == 200
    assert ids(response) == [1, 2, 3, 4]


def test_range_with_no_matches_returns_empty_list(client):
    response = client.get("/listings", params={"min_price": 40000, "max_price": 100000})
    assert response.status_code == 200
    assert response.json() == []


def test_min_price_above_max_price_is_422(client):
    response = client.get("/listings", params={"min_price": 100, "max_price": 50})
    assert response.status_code == 422
    assert response.json() == MIN_MAX_DETAIL


def test_min_price_above_max_price_with_category_is_422(client):
    response = client.get("/listings", params={"category": "bikes", "min_price": 200000, "max_price": 100})
    assert response.status_code == 422
    assert response.json() == MIN_MAX_DETAIL


def test_negative_min_price_is_422(client):
    assert client.get("/listings", params={"min_price": -1}).status_code == 422


def test_negative_max_price_is_422(client):
    assert client.get("/listings", params={"max_price": -5}).status_code == 422


def test_negative_max_price_uses_validation_error_not_min_max_message(client):
    response = client.get("/listings", params={"min_price": 5, "max_price": -1})
    assert response.status_code == 422
    assert response.json() != MIN_MAX_DETAIL
    assert isinstance(response.json()["detail"], list)


def test_non_numeric_min_price_is_422(client):
    assert client.get("/listings", params={"min_price": "abc"}).status_code == 422


def test_decimal_max_price_is_422(client):
    assert client.get("/listings", params={"max_price": "12.50"}).status_code == 422


def test_empty_min_price_is_422(client):
    assert client.get("/listings?min_price=").status_code == 422
