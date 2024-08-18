from flask import Flask, request
import json
import pandas as pd
from datetime import datetime

from battery_optimizer import schedule_simple_battery, compute_soc_schedule

app = Flask(__name__)


@app.route("/")
def home():
    return "Simple BESS Scheduling Optimization API"


@app.route("/schedule", methods=["GET"])
def schedule():
    try:
        # Get the JSON data from the request
        data = request.get_json()

        prices_df = pd.DataFrame.from_dict(data.get("prices"))
        prices_df.index = [datetime.strptime(x, "%Y-%m-%dT%H:%M:%S%z") for x in prices_df.index]

        results = schedule_simple_battery(prices=prices_df,
                                          soc_start=data.get("soc_start"),
                                          soc_max=data.get("soc_max"),
                                          soc_min=data.get("soc_min"),
                                          soc_target=data.get("soc_target"),
                                          power_capacity=data.get("power_capacity"),
                                          storage_capacity=data.get("storage_capacity", 100.0),
                                          conversion_efficiency=data.get("conversion_efficiency", 1.0),
                                          top_up=data.get("top_up", False))

        # Return the optimization results as JSON
        return json.dumps({
            "status": "success",
            "results": {
                "optimal_cost": float(results[0]),
                "optimal_power_schedule": results[1],
                "optimal_soc_schedule": compute_soc_schedule(results[1], float(data.get("soc_start")))
            }
        }), 200
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": str(e)
        }), 500


if __name__ == '__main__':
    app.run(debug=True)
