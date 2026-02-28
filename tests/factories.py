import random

import factory

from hw.app import db
from hw.models import Client, Parking


class ClientFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Client
        sqlalchemy_session = db.session

    name = factory.Faker("first_name", locale="en_US")
    surname = factory.Faker("last_name", locale="en_US")
    credit_card = factory.Maybe(
        factory.Faker("pybool", locale="en_US"),
        yes_declaration=factory.Faker("credit_card_number", locale="en_US"),
        no_declaration=None,
    )
    car_number = factory.Faker("text", max_nb_chars=50, locale="en_US")


class ParkingFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Parking
        sqlalchemy_session = db.session

    address = factory.Faker("address", locale="en_US")
    opened = factory.Faker("pybool", locale="en_US")
    count_places = factory.Faker("pyint", min_value=1, max_value=50, locale="en_US")
    count_available_places = factory.LazyAttribute(
        lambda obj: random.randint(0, obj.count_places)
    )
