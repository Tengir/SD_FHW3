def test_payments_api_flow(payments_client):  # noqa: D401
    # query before create
    assert payments_client.get("/payments/balance").status_code == 404

    # create account
    assert payments_client.post("/payments/").status_code == 201

    # top up wrong json
    bad = payments_client.post("/payments/topup", json={"amount": -10})
    assert bad.status_code == 422

    good = payments_client.post("/payments/topup", json={"amount": 70})
    assert good.json()["balance"] == 70

    # balance endpoint
    assert payments_client.get("/payments/balance").json() == {"balance": 70}