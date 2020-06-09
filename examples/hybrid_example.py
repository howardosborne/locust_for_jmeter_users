from locust import User, task, constant
import time
import random

class MyHybridUser(User):
    wait_time = constant(1)
    widget_count = 0

    def on_start(self):
        self.widget_maker = WidgetMaker()
        return super().on_start()
    @task
    def my_task(self):
        start_at = time.time()
        widget = self.widget_maker.get_widget()
        #pass if the widget is “good”, otherwise fail
        if widget =="good":
            self.environment.events.request_success.fire(request_type="WidgetMaker", name="make_widget", response_time=(time.time() - start_at) * 1000, response_length=len(widget))
        else:
            self.environment.events.request_failure.fire(request_type="WidgetMaker", name="make_widget", response_time=(time.time() - start_at) * 1000, response_length=len(widget), exception=widget)

#the thing we want to test the performance of
class WidgetMaker:
    widget_quality = ["good", "bad"]
    def get_widget(self):
        time.sleep(random.randint(1,5))
        return random.choices(population=self.widget_quality,weights=(80,20),k=1)[0]
