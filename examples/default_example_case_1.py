import pandas as pd

from battery_optimizer import schedule_simple_battery, compute_soc_schedule

raw_prices = dict(
    production=[7, 2, 3, 4, 1, 6, 7, 2, 3, 4, 1, 6, 7, 2, 3, 4, 1, 6, 7, 2, 3, 4, 1, 6],
    consumption=[8, 3, 4, 5, 2, 7, 8, 3, 4, 5, 2, 7, 8, 3, 4, 5, 2, 7, 8, 3, 4, 5, 2, 7],
)
soc_start=20
soc_max=90
soc_min=10
soc_target=90
power_capacity=10
prices = pd.DataFrame(raw_prices, index=pd.date_range("2000-01-01T00:00+01", periods=len(raw_prices["consumption"]), freq="1h", inclusive="left"))
costs, power_schedule = schedule_simple_battery(
    prices=prices,
    soc_start=soc_start,
    soc_max=soc_max,
    soc_min=soc_min,
    soc_target=soc_target,
    power_capacity=power_capacity,
)
soc_schedule = compute_soc_schedule(power_schedule, soc_start=soc_start)
print(f"Costs: {costs}")
print(f"Power schedule: {power_schedule}")
print(f"SoC schedule: {soc_schedule}")