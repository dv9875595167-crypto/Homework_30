from datetime import datetime, timezone

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///parking.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    from .models import Client, ClientParking, Parking

    with app.app_context():
        db.create_all()

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db.session.remove()

    @app.route("/clients", methods=["GET"])
    def get_clients():
        clients = Client.query.all()
        return jsonify([c.to_json() for c in clients]), 200

    @app.route("/clients/<int:client_id>", methods=["GET"])
    def get_client(client_id):
        client = db.session.get(Client, client_id)
        if not client:
            return jsonify({"error": "Client not found"}), 404
        return jsonify(client.to_json()), 200

    @app.route("/clients", methods=["POST"])
    def create_client():
        data = request.json
        new_client = Client(
            name=data["name"],
            surname=data["surname"],
            credit_card=data.get("credit_card"),
            car_number=data.get("car_number"),
        )
        db.session.add(new_client)
        db.session.commit()
        return jsonify(new_client.to_json()), 201

    @app.route("/parkings", methods=["POST"])
    def create_parking():
        data = request.json
        new_parking = Parking(
            address=data["address"],
            opened=data.get("opened", True),
            count_places=data["count_places"],
            count_available_places=data["count_places"],
        )
        db.session.add(new_parking)
        db.session.commit()
        return jsonify(new_parking.to_json()), 201

    @app.route("/client_parking", methods=["POST"])
    def enter_parking():
        data = request.json
        client_id = data["client_id"]
        parking_id = data["parking_id"]

        client = db.session.get(Client, client_id)
        parking = db.session.get(Parking, parking_id)

        if not client:
            return jsonify({"error": "Client not found"}), 404
        if not parking:
            return jsonify({"error": "Parking not found"}), 404
        if not parking.opened:
            return jsonify({"error": "Parking is closed"}), 400
        if parking.count_available_places <= 0:
            return jsonify({"error": "No available places"}), 400

        existig = ClientParking.query.filter_by(
            client_id=client_id, parking_id=parking_id, time_out=None
        ).first()
        if existig:
            return jsonify({"error": "Client already inside"}), 400

        parking.count_available_places -= 1
        entry = ClientParking(
            client_id=client_id,
            parking_id=parking_id,
            time_in=datetime.now(timezone.utc),
        )
        db.session.add(entry)
        db.session.commit()

        return jsonify({"message": "Entry recorded"}), 201

    @app.route("/client_parkings", methods=["DELETE"])
    def exit_parking():
        data = request.json
        client_id = data["client_id"]
        parking_id = data["parking_id"]

        entry = ClientParking.query.filter_by(
            client_id=client_id, parking_id=parking_id, time_out=None
        ).first()

        if not entry:
            return jsonify({"error": "Active parking session not found"}), 404

        client = db.session.get(Client, client_id)
        parking = db.session.get(Parking, parking_id)

        if not client.credit_card:
            return jsonify({"error": "No credit card linked"}), 400

        entry.time_out = datetime.now(timezone.utc)
        parking.count_available_places += 1

        time_in_utc = entry.time_in
        if entry.time_in.tzinfo is None:
            time_in_utc = entry.time_in.replace(tzinfo=timezone.utc)
        duration = (entry.time_out - time_in_utc).total_seconds() / 3600
        price_per_hour = 100
        total_price = round(duration * price_per_hour, 2)

        db.session.commit()

        return jsonify({"message": "Exit recorded", "total_price": total_price}), 200

    return app
