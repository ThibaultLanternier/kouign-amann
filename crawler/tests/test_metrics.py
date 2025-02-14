import platform
import unittest
from time import time_ns

from app.tools.metrics import MetricRecorder


class TestMetricRecorder(unittest.TestCase):
    def test_record_metric_datetime_now(self):
        recorder = MetricRecorder(measurement_name="test")
        recorder.add_step("step_1")
        recorder.set_hash("xxxx")
        recorder.add_step("step_2")
        recorder.add_tag("picture_type", "new")

        self.assertIsNotNone(recorder.get_line())

    def test_record_metric(self):
        start_time_ns = 344433600000003000

        time_step_1 = start_time_ns + 1
        time_step_2 = start_time_ns + 4
        end_time = start_time_ns + 5

        recorder = MetricRecorder(measurement_name="test", now_ns=start_time_ns)
        recorder.add_step("step_1", time_step_1)
        recorder.set_hash("xxxx")
        recorder.add_step("step_2", time_step_2)
        recorder.add_tag("picture_type", "new")

        self.assertEqual(
            "test,hash=xxxx,picture_type=new step_1=1i,step_2=3i 344433600000003005",
            recorder.get_line(end_time),
        )

    @unittest.skipIf(
        platform.system() != "Linux",
        "No correct implementation of NanoSecond counter on Windows",
    )
    def test_record_metric_without_time_injection(self):
        recorder = MetricRecorder(measurement_name="test")
        recorder.add_step("step_1")
        recorder.set_hash("xxxx")
        recorder.add_step("step_2")
        recorder.add_tag("picture_type", "new")
        recorder.add_step("step_3")

        steps = recorder.get_steps()

        self.assertEqual('XXX', platform.system())

        self.assertGreater(steps["step_1"], 0)
        self.assertGreater(steps["step_2"], 0)
        self.assertGreater(steps["step_3"], 0)

    def test_record_metric_check_is_utc(self):
        unix_timestamp = int(time_ns())

        recorder = MetricRecorder(measurement_name="test")

        recorder.add_step("step_1")
        recorder.set_hash("xxxx")

        line_timestamp = int(recorder.get_line().split(" ")[2])

        delta = round(abs((unix_timestamp - line_timestamp) / 1e6))

        self.assertEqual(0, delta)
