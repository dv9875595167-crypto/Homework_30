import pytest

from hw.models import Client, Parking


@pytest.mark.parametrize(
    "url",
    [
        "/clients",
        "/clients/1",
    ],
)
def test_get_routes_return_200(client, url):
    response = client.get(url)
    assert response.status_code == 200


def test_create_client(client, db):
    data = {
        "name": "Alice",
        "surname": "Smith",
        "credit_card": "1111-2222-3333-4444",
        "car_number": "XYZ987",
    }
    response = client.post("/clients", json=data)
    assert response.status_code == 201

    new_client = db.session.query(Client).filter_by(name="Alice").first()
    assert new_client is not None
    assert new_client.credit_card == "1111-2222-3333-4444"


def test_create_parking(client, db):
    data = {"address": "New Street 10", "opened": True, "count_places": 5}
    response = client.post("/parkings", json=data)
    assert response.status_code == 201

    parking = db.session.query(Parking).filter_by(address="New Street 10").first()
    assert parking is not None
    assert parking.count_available_places == 5


@pytest.mark.parking
def test_enter_parking(client, db):
    client_id = 1
    parking_id = 1
    parking_before = db.session.get(Parking, parking_id)
    free_before = parking_before.count_available_places

    response = client.post(
        "/client_parking", json={"client_id": client_id, "parking_id": parking_id}
    )
    assert response.status_code == 201

    parking_after = db.session.get(Parking, parking_id)
    assert parking_after.count_available_places == free_before - 1


@pytest.mark.parking
def test_exit_parking(client, db):

    client.post(
        "/clients",
        json={
            "name": "John",
            "surname": "Doe",
            "credit_card": "1234-5678-9012-3456",
            "car_number": "A123BC",
        },
    )

    client.post("/parkings", json={"address": "Main Street 1", "count_places": 5})

    client_id = 1
    parking_id = 1

    client.post(
        "/client_parking", json={"client_id": client_id, "parking_id": parking_id}
    )

    response = client.delete(
        "/client_parkings", json={"client_id": client_id, "parking_id": parking_id}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert "total_price" in data
