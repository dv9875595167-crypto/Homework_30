from hw.models import Client, Parking

from .factories import ClientFactory, ParkingFactory


def test_create_client(app, db):
    count_before = db.session.query(Client).count()
    user = ClientFactory()
    db.session.commit()
    assert user.id is not None
    assert db.session.query(Client).count() == count_before + 1


def test_create_parking(client, db):
    count_before = db.session.query(Parking).count()
    parking = ParkingFactory()
    db.session.commit()
    assert parking.id is not None
    assert parking.count_available_places <= parking.count_places
    assert db.session.query(Parking).count() == count_before + 1
