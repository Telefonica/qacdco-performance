import math
from typing_extensions import runtime
from locust import HttpUser, TaskSet, task, constant
from locust import LoadTestShape


class UserTasks(TaskSet):
	@task
	def get_root(self):
		self.client.get("/")


class WebsiteUser(HttpUser):
	wait_time = constant(0.5)
	tasks = [UserTasks]


class MultiWaves(LoadTestShape):

	peaks = [ 60, 40, 50, 80, ]
	min_users = 20
	time_limit = 100

	def tick(self):
		run_time = round(self.get_run_time())
		print (self.get_run_time())
		if run_time < self.time_limit:
			user_count = 0
			reduction_factor = 5
			peaks_len = len (self.peaks) + 1
			for peak in self.peaks:
				print(peak)
				user_count += (
					(peak - self.min_users)
					* math.e ** -(((run_time / (self.time_limit / 10 * 2 / peaks_len)) - reduction_factor) ** 2)
				)
				reduction_factor += 5
			user_count += self.min_users
			return (round(user_count), round(user_count))
		else:
			return None
