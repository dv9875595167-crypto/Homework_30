import random
import factory
from faker import Faker as FakerLib

from hw.app import db
from hw.models import Client, Parking

fake = FakerLib(locale="en_US")

class ClientFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Client
        sqlalchemy_session = db.session

    name = factory.LazyFunction(fake.first_name)
    surname = factory.LazyFunction(fake.last_name)
    credit_card = factory.Maybe(
        factory.LazyFunction(lambda: fake.boolean()),
        yes_declaration=factory.LazyFunction(fake.credit_card_number),
        no_declaration=None,
    )
    car_number = factory.LazyFunction(lambda: fake.text(max_nb_chars=50))

class ParkingFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Parking
        sqlalchemy_session = db.session

    address = factory.LazyFunction(fake.address)
    opened = factory.LazyFunction(lambda: fake.boolean())
    count_places = factory.LazyFunction(lambda: fake.random_int(min=1, max=50))
    count_available_places = factory.LazyAttribute(
        lambda obj: random.randint(0, obj.count_places)
    )