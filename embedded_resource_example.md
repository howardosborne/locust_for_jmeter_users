## How to include embedded resources in Locust manually

If you don't want to use the EmbeddedResourceManager from [locust plugins](https://github.com/SvenskaSpel/locust-plugins/), here is an example of how to do it yourself.

In the example below, we will capture the most commonly referenced resources using the [lxml library](https://lxml.de/) which allows us to find elements by xPath.

Here’s the full code:

```python
from locust import HttpUser, task, events, constant
import time
from lxml import html
import re
 
resource_paths = [
            '//link[@rel="stylesheet"]/@href',
            '//link[@rel="Stylesheet"]/@href',
            '//link[@rel="STYLESHEET"]/@href',
            "//script/@src",
            "//img/@src",
            "//source/@src",
            "//embed/@src",
            "//body/@background",
            '//input[@type="image"]/@src',
            '//input[@type="IMAGE"]/@src',
            '//input[@type="Image"]/@src',
            "//object/@data",
            "//frame/@src",
            "//iframe/@src",
        ]
 
def get_embedded_resources(response_content, filter='.*'):
    resources = []
    tree = html.fromstring(response_content)
    for resource_path in resource_paths:
        for resource in tree.xpath(resource_path):
            if re.search(filter, resource): resources.append(resource)
    return resources
    
        
class HttpUserWithContent(HttpUser):
    host = "https://www.demoblaze.com"
    wait_time = constant(1)
    
    @task
    def t(self):
        name = "/"
        response = self.client.get("/", name=name)
        resources = get_embedded_resources(response.content)
        for resource in resources:
            if re.search("^https?://", resource) == None: resource = self.host + "/" + resource          
            self.client.get(resource, name=name+"_resources")
``` 

Now let’s break it down

First, we create a list of xPath expressions which obtain stylesheets, JavaScript files, images and other embedded resources.

```python
resource_paths = [
            '//link[@rel="stylesheet"]/@href',
            '//link[@rel="Stylesheet"]/@href',
            '//link[@rel="STYLESHEET"]/@href',
            "//script/@src",
            "//img/@src",
            "//source/@src",
            "//embed/@src",
            "//body/@background",
            '//input[@type="image"]/@src',
            '//input[@type="IMAGE"]/@src',
            '//input[@type="Image"]/@src',
            "//object/@data",
            "//frame/@src",
            "//iframe/@src",
        ]
```

Then we declare a function to look for resources in a page. It takes the html response as an argument and, like the JMeter feature, also a filter to allow resources that do not match the pattern to be excluded.

```python
def get_embedded_resources(response_content, filter='.*'):
```

A list of resources is created and returned

```python
resources = []
    tree = html.fromstring(response_content)
    for resource_path in resource_paths:
        for resource in tree.xpath(resource_path):
            if re.search(filter, resource): resources.append(resource)
    return resources
```
Let’s look at an example HttpUser, which is analogous to the JMeter sampler.

```python
class HttpUserWithContent(HttpUser):
    host = "https://www.demoblaze.com"
    wait_time = constant(1)
    
    @task
    def t(self):
        name = "/"
        response = self.client.get("/", name=name)
        resources = get_embedded_resources(response.content)
        for resource in resources:
            if re.search("^https?://", resource) == None: resource = self.host + "/" + resource          
            self.client.get(resource, name=name+"_resources")
```
We have captured the response and then used our get_embedded_resources function to return a list of resources and make the resource requests.

Note: if you are using the FastHttpUser, you will need to decode the content first.

```python
content.decode("utf-8")
```

We check to see if the resource is a full or partial url and prefix the host if not (later, we will check for the use of a base tag)
```python
if re.search("^https?://", resource) == None:
```
To keep reporting simple we have provided a name argument and then appended “_resources” to it for each resource request. We can change this to provide as much or as little information as we want.
```python
name=name+"_resources"
```
When we run it, we get a breakdown like this

![Locust Dashboard](./images/locust_dashboard.png "Locust Dashboard")
