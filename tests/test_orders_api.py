def test_orders_api_endpoints(orders_client):  # noqa: D401
    # invalid payload
    bad = orders_client.post("/orders/", json={"amount": -5})
    assert bad.status_code == 422

    # happy path
    resp = orders_client.post("/orders/", json={"amount": 120})
    assert resp.status_code == 201
    order_id = resp.json()["id"]

    resp = orders_client.get(f"/orders/{order_id}")
    assert resp.status_code == 200
    assert resp.json()["amount"] == 120

    # unknown order
    assert orders_client.get("/orders/999").status_code == 404