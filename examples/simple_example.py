from locust import HttpUser, User, task, between

class HelloWorld(HttpUser):
    wait_time = between(5, 15)

    @task
    def test(self):
        self.client.get("/")
