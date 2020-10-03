from locust import User, task, constant, events
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys


class WebdriverExample(User):
    wait_time = constant(1)
    host = "http://www.python.org"    
    def on_start(self):
        self.driver = webdriver.Chrome()

    def on_stop(self):
        self.driver.close()

    @task
    def home(self):
        start_at = time.time()
        self.driver.get(self.host)
        if "Python" in self.driver.title:
            self.environment.events.request_success.fire(request_type="WebdriverExample", name=self.host, response_time=(time.time() - start_at) * 1000, response_length=len(self.driver.page_source))
        else:
            self.environment.events.request_failure.fire(request_type="WebdriverExample", name=self.host, response_time=(time.time() - start_at) * 1000, response_length=len(self.driver.page_source), exception=self.driver.title)
        elem = self.driver.find_element_by_name("q")
        elem.clear()
        elem.send_keys("pycon")
        start_at = time.time()
        elem.send_keys(Keys.RETURN)
        if "No results found." not in self.driver.page_source:
                self.environment.events.request_success.fire(request_type="WebdriverExample", name="search pycon", response_time=(time.time() - start_at) * 1000, response_length=len(self.driver.page_source))
        else:
            self.environment.events.request_failure.fire(request_type="WebdriverExample", name="search pycon", response_time=(time.time() - start_at) * 1000, response_length=len(self.driver.page_source), exception=self.driver.page_source)
