from locust import HttpUser, User, task, between
import locust.event

class HelloWorld(HttpUser):
    test_count = 0
    test_limit = 5
    wait_time = between(5, 15)
    @task
    def test(self):
        name = "/"
        response = self.client.get("/", name=name)
        my_event.fire(name=name, response=response)

my_event = locust.event.EventHook()
def on_my_event(name, response, **kw):
    print("Event was fired with arguments: %s, %s" % (name, response))
my_event.add_listener(on_my_event)
