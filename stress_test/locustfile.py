from locust import HttpUser, between, task


class APIUser(HttpUser):
    wait_time = between(1, 5)

    # Put your stress tests here.
    # See https://docs.locust.io/en/stable/writing-a-locustfile.html for help.
    # TODO
    
    @task
    def index(self):
        self.client.get("http://localhost/")

    @task(2)
    def predict(self):
        data = {"file": open("dog.jpeg","rb")}
        self.client.post("/predict", files=data)
