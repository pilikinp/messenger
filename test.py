import models_client
import threading

client = models_client.Client('pilik', '127.0.0.1', 7777)

client.run()
