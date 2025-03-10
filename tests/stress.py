from locust import HttpUser, task, between, LoadTestShape
import sys
import os

# === CONFIGURATION ===
BASE_URL = "http://localhost:8080/yoavlav-devopscourse"
TEST_TYPE = os.environ.get("TEST_TYPE", "load")  # set TEST_TYPE in env var

# === USER BEHAVIOR ===
class YoavAppUser(HttpUser):
    wait_time = between(1, 2)  # simulate user think time

    @task
    def load_home_page(self):
        with self.client.get("/", name="Load Home Page", catch_response=True) as response:
            if response.status_code != 200:
                response.failure(f"Failed to load home page! Status code: {response.status_code}")
            else:
                response.success()

    @task
    def load_about_page(self):
        with self.client.get("/about.jsp", name="Load About Page", catch_response=True) as response:
            if response.status_code != 200:
                response.failure(f"Failed to load about page! Status code: {response.status_code}")
            else:
                response.success()


# === LOAD PROFILE ===
class CustomShape(LoadTestShape):
    """
    Define custom load shapes to simulate:
    - max: ramp 200 users over 2 minutes
    - load: constant 50 users/sec for 5 minutes
    - stress: ramp from 10 to 200 users/sec over 4 minutes
    """

    def __init__(self):
        super().__init__()
        self.test_type = TEST_TYPE.lower()

    def tick(self):
        run_time = self.get_run_time()

        if self.test_type == "max":
            print("Running MAX USER TEST: 200 users ramped over 2 minutes")
            if run_time < 120:  # 2 minutes
                users = int((run_time / 120) * 200)
                spawn_rate = 10
                return (users, spawn_rate)
            else:
                return None

        elif self.test_type == "load":
            print("Running LOAD TEST: 50 users/sec for 5 minutes")
            if run_time < 300:  # 5 minutes
                return (50, 50)  # 50 users, 50 spawn rate
            else:
                return None

        elif self.test_type == "stress":
            print("Running STRESS TEST: Ramp from 10 to 200 users/sec over 4 minutes")
            if run_time < 240:  # 4 minutes
                users = int(10 + (run_time / 240) * (200 - 10))
                spawn_rate = 20
                return (users, spawn_rate)
            else:
                return None

        else:
            print("Unknown TEST_TYPE. Defaulting to LOAD TEST.")
            if run_time < 300:
                return (50, 50)
            else:
                return None
