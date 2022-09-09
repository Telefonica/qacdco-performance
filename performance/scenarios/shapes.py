from locust import LoadTestShape

class JmeterTestShape(LoadTestShape):
    stages = [
        {"duration": 75, "users": 2, "spawn_rate": 1},
        {"duration": 100, "users": 5, "spawn_rate": 1},
        {"duration": 150, "users": 3, "spawn_rate": 1},
        {"duration": 170, "users": 8, "spawn_rate": 10},
        {"duration": 300, "users": 3, "spawn_rate": 10},
    ]

    def tick(self):
        run_time = self.get_run_time()

        for stage in self.stages:
            if run_time < stage["duration"]:
                tick_data = (stage["users"], stage["spawn_rate"])
                return tick_data

        return None