## Setting a proxy
Some tests need to use a proxy server.

However, this is not the only reason for changing your proxy settings. Tools such as [Fiddler](https://www.telerik.com/fiddler) or [Charles](https://www.charlesproxy.com/) can help analyse and debug the traffic between your test and the server. To do this, you would need to set the tool as a proxy. Fiddler by default run on port 8888.

To set a proxy in Locust for all requests, add the following lines:
```python
#setting a proxy which is running on localhost at port 8888
def on_start():
self.client.proxies = { "http"  : "http://localhost:8888", "https" : "https://localhost:8888"}
self.client.verify = False
```

## Pre and post processors
In any task, you can write what you like before or after a request - it’s just python. When you want to add more structure and reuse code, you can make custom functions as with the get_uuid example earlier.

There is also an in-built event hook system available. Here is an example:

```python
class HelloWorld(HttpUser):
    wait_time = constant(1)

    @task
    def test(self):
        response = self.client.get("/")
       #fire the event
        my_event.fire("/", response)

#create an event hook 
my_event = locust.event.EventHook()

#make a function which is called by the hook
def on_my_event(name, response):
    print("Event was fired with arguments: %s, %s" % (name, response))

#now listen for the event to be fired
my_event.add_listener(on_my_event)
```

## Other protocols
There is a growing list of other protocols supported in [locust plugins](https://github.com/SvenskaSpel/locust-plugins/) but a nice feature of Locust is that you can just use the User class and then can test pretty much anything. Here is an example testing a made-up ‘WidgetMaker’:

```python
class MyHybridUser(User):
    wait_time = constant(1)

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
```

The results of running this look like this:
![Widget Maker Results](./images/locust_hybrid_results.png "Widget Maker Results")

### Using Selenium Webdriver
We can extend what we did with the WidgetMaker to do things like testing using Selenium Webdriver.
Here's an example:
```python
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

``` 
And the results look like this:
![Webdriver Results](./images/webdriver.png "Webdriver Results")

## Variables and scope
A common frustration with JMeter is the way variables (and parameters) are stored and used. Because this is plain old python, you can store and retrieve variables of any type, in any format with any level of scope.

If you are new to python, it is well worth taking some time to learn about variable scoping. Here is a nice [walkthrough](https://www.w3schools.com/python/python_scope.asp).

## CSV data
In JMeter you may well have driven your tests using the [CSV Data Set Config](https://jmeter.apache.org/usermanual/component_reference.html#CSV_Data_Set_Config).
To get the same functionality in Locust you have a couple of options.
First there is a csv plugin available at [locust-plugins](https://github.com/SvenskaSpel/locust-plugins/). This plugin makes use of the [csv library](https://docs.python.org/3/library/csv.html) and provides an iterator to loop through the csv file and when it reaches the end of the file, return to the beginning.
The code for this is below.
```python
import csv

class CSVReader:
    "Read test data from csv file using an iterator"

    def __init__(self, file):
        try:
            file = open(file)
        except TypeError:
            pass  # "file" was already a pre-opened file-like object
        self.file = file
        self.reader = csv.reader(file)

    def __next__(self):
        try:
            return next(self.reader)
        except StopIteration:
            # reuse file on EOF
            self.file.seek(0, 0)
            return next(self.reader)
```
If you are looking for different behaviour, such as stopping the test at the end of the file, then you can do this yourself quite easily. Using the csv.DictReader allows field names to be used which will default to the first line of the csv file.

```python
import csv

with open('name_of_csv_file.csv', newline='') as csvfile:
    csvreader = csv.DictReader.reader(csvfile, delimiter=',')
    for row in csvreader:
        #get values by field name
```

## Monitoring
There is no feature for capturing server metrics such as the performance monitor plugin.

## Distributed testing
If you run distributed tests in JMeter, you can do the same in Locust. Start the master with the --master flag and for each load generator, run with the --worker and --master-host flags set.
