import unittest
import pandas as pd

from battery_optimizer import schedule_simple_battery


class TestOptimizerInputs(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestOptimizerInputs, self).__init__(*args, **kwargs)
        raw_prices = dict(
            production=[7, 2, 3, 4],
            consumption=[8, 3, 4, 5],
        )
        self.prices = pd.DataFrame(raw_prices,
                              index=pd.date_range("2000-01-01T00:00+01",
                                                  periods=len(raw_prices["consumption"]),
                                                  freq="1h", inclusive="left"))
        self.soc_start = 20
        self.soc_max = 90
        self.soc_min = 10
        self.soc_target = 40
        self.power_capacity = 10

    def test_negative_input_parameters(self):
        try:
            schedule_simple_battery(
                prices=self.prices,
                soc_start=-20,  # This should trigger a value error
                soc_max=self.soc_max,
                soc_min=self.soc_min,
                soc_target=self.soc_target,
                power_capacity=self.power_capacity,
            )

        except ValueError as e:
            assert e.__str__() == "Numeric parameters must have non-negative values"

    def test_conversion_efficiency_value(self):
        try:
            schedule_simple_battery(
                prices=self.prices,
                soc_start=self.soc_start,
                soc_max=self.soc_max,
                soc_min=self.soc_min,
                soc_target=self.soc_target,
                power_capacity=self.power_capacity,
                conversion_efficiency=1.1  # This should trigger a value error
            )

        except ValueError as e:
            assert e.__str__() == "Conversion efficiency must be less than or equal to 1"

    def test_soc_limit_values(self):
        soc_max = self.soc_min - 1
        try:
            schedule_simple_battery(
                prices=self.prices,
                soc_start=self.soc_start,
                soc_max=soc_max,  # This should trigger a value error
                soc_min=self.soc_min,
                soc_target=self.soc_target,
                power_capacity=self.power_capacity,
            )

        except ValueError as e:
            assert e.__str__() == "SoC max must be greater than SoC min"

        soc_start = self.soc_max + 1
        try:
            schedule_simple_battery(
                prices=self.prices,
                soc_start=soc_start,  # This should trigger a value error
                soc_max=self.soc_max,
                soc_min=self.soc_min,
                soc_target=self.soc_target,
                power_capacity=self.power_capacity,
            )

        except ValueError as e:
            assert e.__str__() == "Starting SoC is outside of acceptable limits"

    def test_target_soc(self):
        target_soc = 90
        try:
            schedule_simple_battery(
                prices=self.prices,
                soc_start=self.soc_start,
                soc_max=self.soc_max,
                soc_min=self.soc_min,
                soc_target=target_soc,  # This should trigger a value error
                power_capacity=self.power_capacity,
            )

        except ValueError as e:
            assert e.__str__() == "There is not enough time/power to reach the target SoC"

    def test_storage_capacity(self):
        try:
            schedule_simple_battery(
                prices=self.prices,
                soc_start=self.soc_start,
                soc_max=self.soc_max,
                soc_min=self.soc_min,
                soc_target=self.soc_target+10,  # This should trigger a value error
                power_capacity=self.power_capacity,
                storage_capacity=self.soc_target
            )

        except ValueError as e:
            assert e.__str__() == "Target SoC must not exceed the storage capacity"

        try:
            schedule_simple_battery(
                prices=self.prices,
                soc_start=self.soc_start,
                soc_max=self.soc_target+10,  # This should trigger a value error
                soc_min=self.soc_min,
                soc_target=self.soc_target,
                power_capacity=self.power_capacity,
                storage_capacity=self.soc_target
            )

        except ValueError as e:
            assert e.__str__() == "Max SoC must not exceed the storage capacity"


if __name__ == '__main__':
    unittest.main()
