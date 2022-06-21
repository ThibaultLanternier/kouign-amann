from time import sleep
import unittest
from app.tools.metrics import MetricRecorder
from datetime import datetime

class TestMetricRecorder(unittest.TestCase):
    def test_record_metric_datetime_now(self):
        recorder = MetricRecorder(measurement_name="test")
        recorder.add_step("step_1")
        recorder.set_hash("xxxx")
        recorder.add_step("step_2")
        recorder.add_tag("picture_type","new")

        self.assertIsNotNone(recorder.get_line())

    def test_record_metric(self):
        start_time = datetime(1980,11,30,12,0,0,0)
        time_step_1 = datetime(1980,11,30,12,0,0,1)
        time_step_2 = datetime(1980,11,30,12,0,0,2)
        end_time = datetime(1980,11,30,12,0,0,3)

        recorder = MetricRecorder(measurement_name="test", current_datetime=start_time)
        recorder.add_step("step_1", time_step_1)
        recorder.set_hash("xxxx")
        recorder.add_step("step_2", time_step_2)
        recorder.add_tag("picture_type","new")

        self.assertEqual("test,hash=xxxx,picture_type=new step_1=1000i,step_2=1000i 344433600000003000", recorder.get_line(end_time))

    def test_record_metric_without_time_injection(self):
        recorder = MetricRecorder(measurement_name="test")
        sleep(1e-03)
        recorder.add_step("step_1")
        recorder.set_hash("xxxx")
        sleep(1e-12)
        recorder.add_step("step_2")
        recorder.add_tag("picture_type","new")
        sleep(3e-12)
        recorder.add_step("step_3")

        steps = recorder.get_steps()

        self.assertNotEqual(0, steps["step_1"])
        self.assertNotEqual(0, steps["step_2"])
        self.assertNotEqual(0, steps["step_3"])
