import math
from locust import HttpUser, TaskSet, task, constant
from locust import LoadTestShape


class UserTasks(TaskSet):
	@task
	def get_root(self):
		self.client.get("/")


class WebsiteUser(HttpUser):
	wait_time = constant(0.5)
	tasks = [UserTasks]


class LoadShape(LoadTestShape):

	total_users = 30
	spawn_rate = 3
	time_limit = 200
	shut_down = 30
	def tick(self):
		run_time = self.get_run_time()
		if run_time > self.time_limit + self.shut_down:
			return None
		if (run_time < self.time_limit):
			return (self.total_users, self.spawn_rate)
		users_to_stop = math.floor(self.total_users/self.shut_down * (run_time - self.time_limit))
		actual_users = self.total_users - users_to_stop
		return ( actual_users, self.spawn_rate)
