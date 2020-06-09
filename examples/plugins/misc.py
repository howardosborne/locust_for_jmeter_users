import locust.event

my_event = locust.event.EventHook()
def on_my_event(name, response, **kw):
    print("Event was fired with arguments: %s, %s" % (name, response))
my_event.add_listener(on_my_event)
