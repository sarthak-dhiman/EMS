from locust import HttpUser, task, between


class WebsiteUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        # Optionally obtain a token here via auth endpoint
        self.client.headers.update({"Authorization": "Bearer DEMO_TOKEN"})

    @task(3)
    def list_tasks(self):
        self.client.get("/tasks")

    @task(1)
    def create_task(self):
        self.client.post("/tasks/", json={"title": "load-test", "description": "auto"})
