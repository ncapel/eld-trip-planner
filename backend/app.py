from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from utils.route_planner import plan_route
from utils.hours_of_service import calculate_hos_compliance
from utils.eld_generator import generate_eld_logs

load_dotenv()

app = Flask(__name__)
CORS(app)

@app.route('/api/plan', methods=['POST'])
def create_plan():
    """
    expected JSON input
    {
        "current_location": "City, State",
        "pickup_location": "City, State",
        "dropoff_location": "City, State",
        "current_hours": 5  # Hours already used in current cycle
    }
    """
    try:
        # ! DEBUG
        app.logger.info("Received plan request")
        data = request.json
        app.logger.info(f"Request data: {data}")

        data = request.json

        # validation for the fields
        required_fields = ['current_location', 'pickup_location', 'dropoff_location', 'current_hours']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        # route planning
        route_data = plan_route(
            current_location=data['current_location'],
            pickup_location=data['pickup_location'],
            dropoff_location=data['dropoff_location']
        )

        # calculating hos compliance and stops
        hos_plan = calculate_hos_compliance(
            route_data=route_data,
            current_hours=float(data['current_hours'])
        )

        # generating the eld logs in compliance with hos ruleset
        eld_logs = generate_eld_logs(hos_plan)

        # summation of all data
        response = {
            "route": route_data,
            "hos_plan": hos_plan,
            "eld_logs": eld_logs
        }

        return jsonify(response)

    except Exception as e:
        # ! DEBUG
        app.logger.error(f"Error processing request: {str(e)}")
        import traceback
        app.logger.error(traceback.format_exc())

        return jsonify({"error": str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    # basically just using this to confirm if the app is live before continuing
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)