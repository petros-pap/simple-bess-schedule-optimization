# Simple BESS scheduling optimization

An optimization framework written in Python using Pyomo for scheduling a simple battery energy storage system (BESS). The framework aims to maximize economic returns or minimize operational costs by determining the optimal charge and discharge schedule based on a given .

## Table of Contents
- [Installation](#installation)
- [Usage](#usage)
- [Input Data](#input-data)
- [Output](#output)
- [Examples](#examples)
- [Dependencies](#dependencies)



## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/simple-bess-scheduling.git
    cd simple-bess-scheduling
    ```

2. Create a virtual environment (optional but recommended):
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1. Prepare your input data (see [Input Data](#input-data) for details).
2. Run the optimization script:
    ```bash
    python optimize_bess_schedule.py
    ```
3. The optimal schedule will be generated and saved as specified in the output settings.

### Command-line Arguments

- `--input`: Path to the input data file (default: `input_data.csv`).
- `--output`: Path to save the output results (default: `output_schedule.csv`).
- `--objective`: Objective of the optimization (`cost` or `revenue`, default: `cost`).

## Input Data

The input data file should be in CSV format and contain the following columns:
- **Time**: Timestamp or time index for each period.
- **Price**: Electricity price for each time period.
- **Demand**: (Optional) Power demand in each period, if relevant.

Ensure that the input data is properly formatted as per the above structure. An example input file is provided in the `data/` directory.

## Output

The output will be a CSV file containing the optimal charge/discharge schedule with the following columns:
- **Time**: Timestamp or time index.
- **Charge/Discharge**: Amount of power to charge (+) or discharge (-) the battery in each time period.
- **State of Charge (SOC)**: The battery's state of charge at the end of each period.

## Examples

Example scripts and data files are provided in the `examples/` directory to demonstrate typical use cases and how to interpret the results.

## Dependencies

- Python v3.12
- Pyomo v6.7.3
- NumPy v1.26.4
- Pandas v2.2.2

Install the dependencies using:
```bash
pip install -r requirements.txt