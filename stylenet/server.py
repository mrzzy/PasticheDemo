#
# server.py
# Style Transfer Server
#

import os
import api
import json
import styleopt

from PIL import Image
from flask import Flask, request
from multiprocessing import Process, Queue

from client import read_file
from util import convert_image, read_file

## Tasking
# Style transfer worker that runs style transfers task as defined by the 
# payloads queued
class StyleWorker:
    def __init__(self, queue=Queue(), verbose=True):
        self.queue = queue
        self.verbose = verbose

        # Setup workers process
        self.process = Process(target=self.run)
        self.process.start()
    
    # Run loop of worker
    def run(self):
        while True:
            # Perform style transfer for payload
            payload = self.queue.get()
    
            # Extract content and style images from payload
            content_data, style_data, tag = api.unpack_payload(payload)
            content_image = convert_image(content_data)
            style_image = convert_image(style_data)
        
            # Perform style transfer
            if self.verbose: print("[StyleWorker]: processing payload: ", tag)
            pastiche_image = styleopt.transfer_style(content_image, style_image,
                                                     image_size=(64, 64),
                                                     verbose=self.verbose)
        
            # Save results of style transfer
            if self.verbose: print("[StyleWorker]: completed payload: ", tag)
            if not os.path.exists("static/pastiche"): os.mkdir("static/pastiche")
            pastiche_image.save("static/pastiche/{}.jpg".format(tag))
            
worker = None
            
## Routes
app = Flask(__name__, static_folder="static")
# Default route "/" displays server running message, used to check server status
@app.route("/", methods=["GET"])
def route_status():
    return app.send_static_file("status.html")

## REST API
# Rest API route "/api/style" triggers style transfer given POST body payload 
@app.route("/api/style", methods=["POST"])
def route_api_style():
    print("[API call]: /api/style")
    payload = request.get_json()
    # Queue payload to perform style transfer on worker
    worker.queue.put(payload)
    # Reply okay status
    return json.dumps({"sucess": True}), api.STATUS_OK, {'ContentType':'application/json'}

# Rest API route "/api/pastiche/<tag>" attempts to retrieve pastiche for the
# given tag
@app.route("/api/pastiche/<tag>", methods=["GET"])
def route_api_pastiche(tag):
    print("[API call]: /api/pasitche for tag", tag)
    # Check if pastiche has been generated for id
    pastiche_path = "pastiche/{}.jpg".format(tag)
    if os.path.exists("static/" + pastiche_path):
        # Repond with pastiche for tag id 
        return app.send_static_file(pastiche_path), api.STATUS_OK
    else:
        return (json.dumps({"error": "Resource not available yet"}), 
                api.STATUS_NOT_READY, {'ContentType':'application/json'})

if __name__ == "__main__":
    worker = StyleWorker()
    app.run(host='0.0.0.0', port=api.SERVER_PORT)
