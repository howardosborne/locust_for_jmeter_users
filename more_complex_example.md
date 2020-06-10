In this example we are going to buy a product from the [Demoblaze Shop](https://www.demoblaze.com) and in doing so, learn some more about how to do things in Locust.

#### The source for this example is [here](./examples/more_complex_example.py)
```python
from locust import HttpUser, SequentialTaskSet, task, between, events
import logging

import json, random, string

class MakePurchase(SequentialTaskSet):
    
    def on_start(self):
        self.purchase_id = get_uuid()

    @task
    def home(self):
        self.client.get("/", name ="01 /")

    @task
    def get_config_json(self):
        response = self.client.get("/config.json", name="02 /config.json")
        response_json = json.loads(response.text)
        self.api_host = response_json["API_URL"]

    @task
    def get_item(self):
        response = self.client.get(self.api_host + "/entries", name="03 /entries")
        response_json = json.loads(response.text)
        self.id = response_json["Items"][0]["id"]

    @task
    def view_product(self):
        self.client.cookies["user"] = get_uuid()
        response = self.client.get("/prod.html?idp_=" + str(self.id), name="04 /prod.html?idp_")

    @task
    def view(self):
        payload = '{"id":"' + str(self.id) + '"}'
        response = self.client.post(self.api_host + "/view", payload , headers={"Content-Type": "application/json"}, name="05 /view")

    @task
    def add_to_cart(self):
        payload = '{"id":"' + self.purchase_id + '","cookie":"user=' + self.user_cookie + '","prod_id":' + str(self.id) + ',"flag":false}'
        response = self.client.post(self.api_host + "/addtocart", payload, headers={"Content-Type": "application/json"},  name="06 /addtocart")

    @task
    def view_cart(self):
        response = self.client.get("/cart.html", name="07 /cart.html")

    @task
    def post_cart(self):
        payload = '{"cookie":"user=' + self.user_cookie + '","flag":false}'
        response = self.client.post(self.api_host + "/viewcart", payload, headers={"Content-Type": "application/json"},  name="08 /viewcart")

    @task
    def delete_item(self):
        payload = '{"cookie":"user=' + self.user_cookie + '"}'
        with self.client.post(self.api_host + "/deletecart", payload, headers={"Content-Type": "application/json"},  name="09 /deletecart", catch_response=True) as response:
            if response.content != b"Delete complete":
                response.failure("delete incomplete")

class DemoBlazePurchaser(HttpUser):
    wait_time = between(2, 5)
    tasks = [MakePurchase]

def get_uuid():
    #make a random string
    r_s = ''.join(random.choices(string.ascii_lowercase + string.digits, k=32))
    #return it in a 'uuid' format
    uuid = r_s[:8] + "-" + r_s[8:12] + "-" + r_s[12:16] + "-" + r_s[16:20] + "-" + r_s[20:32]
    return uuid
```

## Tasks, tasksets and sequential tasksets
Just as samplers can be grouped together with controllers in JMeter, so tasks can be grouped with tasksets and sequential tasksets.

Tasksets are used where the execution order isn’t important and sequential tasksets where it does matter. In this example, order matters so we are adding a sequential taskset.

```python
class MakePurchase(SequentialTaskSet):
```
Tasksets can also be nested in other tasksets and weight attributes can be set to determine the relative number of times each task is called. More details are in the [Locust documentation](https://docs.locust.io/en/latest/writing-a-locustfile.html#taskset-class).

## Start up/setup
JMeter has setUp and tearDown thread groups to carry out any initialisation activity (as well as pre and post processors), to do this in Locust, add an on_start function. In the example, we will need to provide a unique identifier as a purchase id.

```python
class MakePurchase(SequentialTaskSet):
def on_start(self):
    #make a unique purchase id for later use
    self.purchase_id = get_uuid()
```

## Making custom functions
The unique identifier for purchase id would normally be done by JavaScript running in the browser and to recreate this in JMeter, we may either use a built in function such as __UUID or make groovy script and add it as a pre-processor.

With Locust, we can make a function and then call it when we need it. In this case, we create a function get_uuid

```python
def get_uuid():
    #make a random string
    r_s = ''.join(random.choices(string.ascii_lowercase + string.digits, k=32))
    #return it in a 'uuid' format
    uuid = r_s[:8] + "-" + r_s[8:12] + "-" + r_s[12:16] + "-" + r_s[16:20] + "-" + r_s[20:32]
    return uuid
```

## Naming requests
As with JMeter, where the name field of HTTP Request determines what will appear in the name field, you can also set the name for a request.
Add a name parameter to the request

```python
   @task
    def home(self):
        self.client.get("/", name ="01 /")
```

## Dealing with embedded resources
When requesting a page, you may also want to include requests to embedded resources. This doesn’t come as a standard feature in Locust, but there is a plugin in [locust plugins](https://github.com/SvenskaSpel/locust-plugins/).

Like Locust, Locust plugins can be installed using pip

```python
pip install locust-plugins
```
However, if you would like to learn how to write the code to include embedded resources, an explanation is provided [here](./embedded_resource_example.md)

## Managing cookies and headers
Cookies are managed for you by default, which is like having the cookie manager in JMeter always included.

Both headers and cookies are stored as dictionaries in the session (referenced as self.client) and can be changed for all requests or any specific request.

Let’s look at an example where a cookie has to be created with a unique value by the client and sent in a request.

```python
#create random string using the function we made for purchase ids and add to cookies dictionary
self.client.cookies["user"] = get_uuid()
```

A similar approach can be taken for headers, however, in this case, the headers have been modified directly in a request:

```python
response = self.client.post(self.api_host + "/viewcart", payload, headers={"Content-Type": "application/json"},  name="08 /viewcart")
```

#### To learn more about how cookies and headers are managed and manipulated, see the [requests page](https://requests.readthedocs.io/en/master/)

## Assertions
Assertions are made by setting catch_response to True when making a request and then evaluating the response. For example:
```python
with self.client.post(self.api_host + "/deletecart", catch_response=True) as response:
if response.content != b"Delete complete":
            	response.failure("delete incomplete")
```
When the response is marked as a failure, it is logged and presented in the failures tab

![Failures Tab](./images/failures.png "Failures Tab")

To learn about more features, see [here](./other_features.md)
