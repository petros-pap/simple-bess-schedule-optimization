# Simple BESS scheduling optimization

An optimization framework written in Python using Pyomo for scheduling a simple battery energy storage system (BESS). The framework aims to maximize economic returns or minimize operational costs by determining the optimal charge and discharge schedule based on a given .

## Table of Contents
- [Installation](#installation)
- [Input Data](#input-data)
- [Usage](#usage)
- [Examples](#examples)
- [Dependencies](#dependencies)



## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/petros-pap/simple-bess-schedule-optimization.git
    cd simple-bess-schedule-optimization
    ```

2. Create a virtual environment (optional but recommended):
    ```bash
    python -m venv venv
    source venv/bin/activate  
   ```

3. Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

## Input Data

- **prices**:                  Pandas DataFrame with columns "consumption" and "production" time series data.
- **soc_start**:               State of charge at the start of the schedule.
- **soc_max**:                 Maximum state of charge.
- **soc_min**:                 Minimum state of charge.
- **soc_target**:              Target state of charge at the end of the schedule.
- **power_capacity**:          Power capacity for both charging and discharging.
- **conversion_efficiency**:   Conversion efficiency from power to SoC and vice versa.

## Usage

### API calls

Below are examples to use the optimizer through API calls:

- Through CMD:
   ```bash
   curl -X GET -H "Content-Type: application/json" -d '{"prices": {"production": {"2000-01-01T00:00:00+0100": 7, "2000-01-01T01:00:00+0100": 2, "2000-01-01T02:00:00+0100": 3, "2000-01-01T03:00:00+0100": 4}, "consumption": {"2000-01-01T00:00:00+0100": 8, "2000-01-01T01:00:00+0100": 3, "2000-01-01T02:00:00+0100": 4, "2000-01-01T03:00:00+0100": 5}}, "soc_start": 20.0, "soc_max": 90.0, "soc_min": 10.0, "soc_target": 40.0, "power_capacity": 10.0}' http://127.0.0.1:5000/schedule
   ```
- With python (using requests): ```python examples/example_app.py```
- With any REST API development tool (e.g. [Insomnia](https://insomnia.rest/)):
  - Method: `GET` 
  - URL: http://127.0.0.1:5000/schedule
  - Body: ```{
  "prices": {
    "production": {
      "2000-01-01T00:00:00+0100": 7,
      "2000-01-01T01:00:00+0100": 2,
      "2000-01-01T02:00:00+0100": 3,
      "2000-01-01T03:00:00+0100": 4
    },
    "consumption": {
      "2000-01-01T00:00:00+0100": 8,
      "2000-01-01T01:00:00+0100": 3,
      "2000-01-01T02:00:00+0100": 4,
      "2000-01-01T03:00:00+0100": 5
    }
  },
  "soc_start": 20,
  "soc_max": 90,
  "soc_min": 10,
  "soc_target": 40,
  "power_capacity": 10
}```

### API Output

If no error occurs, the output will be a JSON file with the following structure:
```
{
  "status": "success",
  "results": {
    "optimal_cost": float,
    "optimal_power_schedule": list[float],
    "optimal_soc_schedule": list[float]
  }
}
```
Otherwise, the output will have the following structure:
```
{
  "status": "error",
  "message": str
}
```

## Dependencies

- Python v3.12
- Pyomo v6.7.3
- NumPy v1.26.4
- Pandas v2.2.2
- Flask v3.0.3

Install the dependencies using:
```bash
pip install -r requirements.txt