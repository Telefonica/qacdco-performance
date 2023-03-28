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


class StepLoadShape(LoadTestShape):

	step_time = 30
	step_load = 10
	spawn_rate = 10
	time_limit = 200
	shut_down = 30
	user_time_limit = time_limit - shut_down
	total_steps= math.floor((time_limit - shut_down)/ step_time)
	shut_down_steptime = shut_down / total_steps
	def tick(self):
		run_time = self.get_run_time()
		print (self.total_steps)
		if run_time > self.time_limit:
			return None
		current_step = math.floor(run_time / self.step_time) + 1
		if (run_time > self.user_time_limit):
			rest_time = (run_time - self.user_time_limit)
			current_step = math.floor(self.total_steps) - math.floor(rest_time/ self.shut_down_steptime) 
		return (current_step * self.step_load, self.spawn_rate)
