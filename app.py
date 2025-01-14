from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///par_logic.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define the Provider model
class Provider(db.Model):
    __tablename__ = 'providers'
    id = db.Column(db.Integer, primary_key=True)
    provider_name = db.Column(db.String(128), nullable=False)
    npi = db.Column(db.String(20), nullable=False)
    location = db.Column(db.String(64), nullable=False)
    insurance = db.Column(db.String(64), nullable=False)
    pcp_change_requirement = db.Column(db.String(256), nullable=True)
    hfmc_contract = db.Column(db.Boolean, nullable=False)
    status = db.Column(db.String(256), nullable=False)

# Route to serve the HTML form
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle the logic for location and insurance
@app.route('/test', methods=['GET'])
def get_provider_options():
    location = request.args.get('location')
    insurance = request.args.get('insurance')

    if not location or not insurance:
        return jsonify({"error": "Both location and insurance are required!"})

    providers = Provider.query.filter(
        (Provider.location == location) | (Provider.location == "ALL"),
        Provider.insurance == insurance
    ).all()

    if not providers:
        return jsonify({"error": "No providers found for the given location and insurance."})

    out_of_contract = not providers[0].hfmc_contract

    if out_of_contract:
        facility_message = "You can only visit SCUC as your insurance is out of contract with HFMC."
        facilities = ["SCUC"]
    else:
        facility_message = "You can visit both HFMC and SCUC."
        facilities = ["HFMC", "SCUC"]

    response = {
        "facility_options": {
            "facilities": facilities,
            "message": facility_message
        },
        "pcp_change_requirement": {
            "details": providers[0].pcp_change_requirement or "No PCP change requirement.",
            "required": bool(providers[0].pcp_change_requirement)
        },
        "provider_options": [
            {"name": provider.provider_name, "npi": provider.npi}
            for provider in providers
        ]
    }

    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
