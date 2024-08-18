from __future__ import annotations

import numpy as np
import pandas as pd
from pyomo.core import (
    ConcreteModel,
    Var,
    RangeSet,
    Param,
    Reals,
    NonNegativeReals,
    NonPositiveReals,
    Binary,
    Constraint,
    Objective,
    minimize
)
from pyomo.environ import value
from pyomo.opt import SolverFactory


def compute_soc_schedule(power_schedule: list[float], soc_start: float) -> list[float]:
    """Determine the scheduled state of charge (SoC), given a power schedule and a starting SoC.

    Does not take into account conversion efficiencies.
    """
    return [soc_start] + list(np.cumsum(power_schedule) + soc_start)


def schedule_simple_battery(
        prices: pd.DataFrame,
        soc_start: float,
        soc_max: float,
        soc_min: float,
        soc_target: float,
        power_capacity: float,
        storage_capacity: float = 100.0,
        conversion_efficiency: float = 1.0,
        top_up: bool = False
) -> tuple[float, list[float]]:
    r"""
    Schedule a simplistic battery against given consumption and production prices.

    Solves the following optimization problem:

    $$
    \min \sum_{t=0}^{T} Price_{Buy}(t)\cdot Charge(t) - Price_{Sell}(t) \cdot Discharge(t)
    $$

    s.t.

    $$
    SOC(t) = SOC(0) + \sum_{t=0}^{T} [ \eta \cdot Charge(t) - \frac{1}{\eta} \cdot Discharge(t)]
    $$

    $$
    SOC_{min} \leq SOC(t) \leq SOC_{max}
    $$
    $$
    0 \leq Charge(t) \leq Capacity
    $$
    $$
    0 \leq Discharge(t) \leq Capacity
    $$

    :param prices:                  Pandas DataFrame with columns "consumption" and "production" containing prices.
    :param soc_start:               State of charge at the start of the schedule.
    :param soc_max:                 Maximum state of charge.
    :param soc_min:                 Minimum state of charge.
    :param soc_target:              Target state of charge at the end of the schedule.
    :param power_capacity:          Power capacity for both charging and discharging.
    :param storage_capacity:        Storage capacity of the battery.
    :param conversion_efficiency:   Conversion efficiency from power to SoC and vice versa.
    :param top_up:                  Tops-up (supercharges) the battery at the end of the schedule, setting the soc_target equal to the storage_capacity.
    """

    # Check inputs for infeasibilities
    if (
            (prices < 0).any().any() or
            soc_start < 0 or
            soc_max < 0 or
            soc_min < 0 or
            soc_target < 0 or
            power_capacity < 0 or
            conversion_efficiency < 0
    ):
        raise ValueError("Numeric parameters must have non-negative values")
    if conversion_efficiency > 1:
        raise ValueError("Conversion efficiency must be less than or equal to 1")
    if soc_max <= soc_min:
        raise ValueError("SoC max must be greater than SoC min")
    if soc_start < soc_min or soc_start > soc_max:  # TODO: review if this constraint can be relaxed in the model
        raise ValueError("Starting SoC is outside of acceptable limits")
    if abs(soc_target - soc_start) > prices.shape[0] * power_capacity:
        raise ValueError("There is not enough time/power to reach the target SoC")
    if soc_target > storage_capacity:
        raise ValueError("Target SoC must not exceed the storage capacity")
    if soc_max > storage_capacity:
        raise ValueError("Max SoC must not exceed the storage capacity")

    soc_target = storage_capacity if top_up else soc_target

    model = ConcreteModel()
    model.j = RangeSet(0, len(prices.index.to_pydatetime()) - 1, doc="Set of datetimes")
    model.ems_power = Var(model.j, domain=Reals, initialize=0)
    model.device_power_down = Var(model.j, domain=NonPositiveReals, initialize=0)
    model.device_power_up = Var(model.j, domain=NonNegativeReals, initialize=0)
    model.supercharge_penalty = Var(model.j, domain=NonNegativeReals, initialize=0)

    def price_up_select(m, j):
        return prices["consumption"].iloc[j]

    def price_down_select(m, j):
        return prices["production"].iloc[j]

    model.up_price = Param(model.j, initialize=price_up_select)
    model.down_price = Param(model.j, initialize=price_down_select)

    model.device_max = Param(model.j, initialize=soc_max)
    model.device_min = Param(model.j, initialize=soc_min)

    def ems_derivative_bounds(m, j):
        return (
            -power_capacity,
            m.ems_power[j],
            power_capacity,
        )

    def device_bounds(m, j):
        stock_changes = [
            (
                m.device_power_down[k] / conversion_efficiency  # -9 power out means -10 stock change
                + m.device_power_up[k] * conversion_efficiency  # 10 power in means 9 stock change
            )
            for k in range(0, j + 1)
        ]

        # Apply soc target
        if j == len(prices) - 1:
            return soc_start + sum(stock_changes) == soc_target

        # Stay within SoC bounds
        return (
            m.device_min[j],
            soc_start + sum(stock_changes) - m.supercharge_penalty[j],
            m.device_max[j],
        )

    def device_derivative_equalities(m, j):
        """Determine aggregate flow ems_power."""
        return (
            0,
            m.device_power_up[j] + m.device_power_down[j] - m.ems_power[j],
            0,
        )

    model.device_power_up_bounds = Constraint(model.j, rule=ems_derivative_bounds)
    model.device_power_equalities = Constraint(model.j, rule=device_derivative_equalities)
    model.device_energy_bounds = Constraint(model.j, rule=device_bounds)

    # Add objective
    def cost_function(m):
        costs = 0
        for j in m.j:
            costs += m.device_power_down[j] * m.down_price[j]
            costs += m.device_power_up[j] * m.up_price[j]
            costs += m.supercharge_penalty[j] * 100
        return costs

    model.costs = Objective(rule=cost_function, sense=minimize)
    solver = SolverFactory("cbc")
    results = solver.solve(model, load_solutions=False)

    if results.solver.termination_condition == 'infeasible':
        raise ValueError("The optimization model is infeasible")
    if results.solver.termination_condition == 'unbounded':
        raise ValueError("The optimization model is unbounded")
    print(results.solver.termination_condition)

    # Load the results only if a feasible solution has been found
    if len(results.solution) > 0:
        model.solutions.load_from(results)

    planned_costs = float(value(sum([model.device_power_down[j] * model.down_price[j] +
                                     model.device_power_up[j] * model.up_price[j] for j in model.j])))
    planned_device_power = [float(model.ems_power[j].value) for j in model.j]

    return planned_costs, planned_device_power
