To walk through the features and differences between the two, we’ll make a simple test.

If you don’t have Locust installed, here are the [instructions](https://docs.locust.io/en/latest/installation.html):

##Hello World example
Let’s start with the simplest example - HelloWorld.

A JMeter example might look like this with a thread group, a sampler and a timer.

![JMeter IDE](./images/jmeter_ide.png "JMeter IDE")

To do the same thing with Locust you can use any IDE or text editor such as Notepad or vi. In this example, Visual Studio Code is being used.

![VSCode IDE](./images/vscode_ide.png "VSCode IDE")

Our equivalent HelloWorld test using Locust looks like this:
```python
class HelloWorld(HttpUser):
    wait_time = between(5, 15)

    @task
    def test(self):
        self.client.get("/")
```
*The code for this can be found [here](./examples/simple_example.py)

The objects in Locust and JMeter don’t match exactly, but when we added a thread group and an HTTP sampler in JMeter, in Locust we added a class based on HttpUser and a task (which is a function with a @task decorator).

We also added a wait_time which is like a Uniform Random Timer.

###Recording tests
If you are looking for the recorder in Locust, there isn’t one.
However if, like me, you avoid using recorders then this isn’t really a downside. But if you really do want to get a recording as a starting point, then there is a simple way of doing this.

Use the developer tools in your browser to capture what you need and save the recording as a har file.

![Save as HAR](./images/save_as_har.png "Save as HAR")

Convert the har file to a locust file using https://pypi.org/project/har-transformer/

You also might want to consider using a tool like Charles or Fiddler to capture traffic and analyse the requests and responses.

Now let’s look at running the test.
Running Hello World test
Like JMeter, Locust tests can be run purely from the command line, but by default it has a Flask-based web interface to control and monitor tests as well as download results.

To run our test using the web interface:
```python
 locust -f ".\examples\simple_example.py"
```
Then browse the web interface, by default at http://localhost:8089

![Locust Start Page](./images/vscode_web_start.png "Locust Start Page")

Here we can set how many users, and the rate to ramp up, which we would have set in the thread group in JMeter. You also set the host here. As with JMeter, you can feed these values in from the command line.

As the test progresses, we can monitor progress in the statistics, charts, failures and exceptions windows.

![charts](./images/vscode_web_charts.png "charts")

*One nice feature of Locust is being able to dynamically change the number of concurrent users.
![change user count](./images/change_user_count.png "change user count")

##Analysing results
In JMeter, we have a number of ways of viewing the results of a test. We can add a listener to view results in the GUI or output to a default listener file which can be used to produce a report or imported to other reporting tools.

The results produced in Locust, in addition to the runtime charts, there are three csv files produced.
![Download Data](./images/downoad_data.png "Download Data")
Download request statistics CSV
Download failures CSV
Download exceptions CSV

Request statistics CSV is broadly similar to an aggregate listener in JMeter.

The failures and exceptions CSVs, provide details of, unsurprisingly, failures and exceptions.

To get a report similar to the default JMeter listener, with a record for each request made, you can use the jmeter listener plugin from [locust-plugins](https://github.com/SvenskaSpel/locust-plugins/blob/master/locust_plugins/jmeter_listener.py).

To look at other features, let’s take a [more complex example.](./more_complex_example.md)