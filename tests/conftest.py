from datetime import datetime, timedelta, timezone

import pytest

from hw.app import create_app
from hw.app import db as _db
from hw.models import Client, ClientParking, Parking


@pytest.fixture
def app():
    """Создаем тестовое приложение"""
    app = create_app()
    app.config.update(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        }
    )

    with app.app_context():
        _db.create_all()

        test_client = Client(
            name="Ivan",
            surname="Ivanov",
            credit_card="1234-5678-9012-3456",
            car_number="A123AA",
        )

        test_parking = Parking(
            address="Test street",
            opened=True,
            count_places=10,
            count_available_places=10,
        )

        _db.session.add(test_client)
        _db.session.add(test_parking)
        _db.session.commit()

        parking_log = ClientParking(
            client_id=test_client.id,
            parking_id=test_parking.id,
            time_in=datetime.now(timezone.utc) - timedelta(hours=2),
            time_out=datetime.now(timezone.utc) - timedelta(hours=1),
        )

        _db.session.add(parking_log)
        _db.session.commit()

        yield app

        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def client(app):
    """Фикстура для тестового клиента Flask"""
    return app.test_client()


@pytest.fixture
def db(app):
    """Фикстура для доступа к базе"""
    return _db
