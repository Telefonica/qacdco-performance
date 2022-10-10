from locust import HttpUser, TaskSet, task, constant
from locust import LoadTestShape


class UserTasks(TaskSet):
    @task
    def get_root(self):
        self.client.get("/")


class WebsiteUser(HttpUser):
    wait_time = constant(0.5)
    tasks = [UserTasks]


class MultiGroupsShape(LoadTestShape):

    user_groups = [
        {"users": 2, "init_delay": 0, "startup_time": 30, "hold_load_for": 60, "shutdown": 10},
        {"users": 3, "init_delay": 70, "startup_time": 0, "hold_load_for": 230, "shutdown": 0},
        {"users": 6, "init_delay": 140, "startup_time": 30, "hold_load_for": 10, "shutdown": 0}
    ]

    def get_total_users(self, run_time):
        total_users = 0
        spawn_rate = 0
        for group in self.user_groups:
            real_start_time = group["init_delay"] + group["startup_time"]
            if ((run_time > group["init_delay"]) and (run_time < real_start_time 
                + group["hold_load_for"] + group["shutdown"])):
                if run_time < real_start_time:
                    spawn_rate = float (group["users"]/group["startup_time"])
                elif (run_time > real_start_time + group["hold_load_for"]) and (group["shutdown"] > 0.00):
                    spawn_rate = float (group["users"]/group["shutdown"])
                    total_users -= int ((run_time - real_start_time + group["hold_load_for"]) * spawn_rate)
                total_users += group["users"]
        if spawn_rate == 0.00:
            spawn_rate = total_users
        if total_users == 0:
            spawn_rate = 1
        return (total_users, spawn_rate)
    
    def tick(self):
        run_time = self.get_run_time()
        total_users = self.get_total_users(run_time)
        if total_users[0] != 0:
            return total_users
        return None

