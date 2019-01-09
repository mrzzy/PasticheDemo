#
# Style Transfer 
# REST API functionality
#

import json
import uuid
from base64 import b64encode, b64decode

SERVER_PORT = 8008
#SERVER_URL = "http://127.0.0.1:{}".format(SERVER_PORT)
SERVER_URL = "http://153.20.56.64:{}".format(SERVER_PORT)

TAG_KEY = "tag_uuid_str"
CONTENT_KEY = "content_base64_jpeg"
STYLE_KEY = "style_base64_jpeg"

STATUS_OK = 200
STATUS_NOT_READY = 202
    
# Pack style transfer payload for the given content and style image data
# Returns a JSON representation of the payload and an uuid that uniquely tags
# the payload
def pack_payload(content_data, style_data, tag_id):
    payload = {
        TAG_KEY: tag_id,
        # Encode image data 
        CONTENT_KEY: b64encode(content_data).decode("utf-8"),
        STYLE_KEY: b64encode(style_data).decode("utf-8") 
    }
    
    return json.dumps(payload)

# Unpack the style transfer payload given as payload json
# Returns the content and style image data, and uuid tag that uniquely tags the
# payload
def unpack_payload(payload_json):
    payload = json.loads(payload_json)

    # Decode image data 
    content_data = b64decode(payload[CONTENT_KEY])
    style_data = b64decode(payload[STYLE_KEY])
    
    # Obtain payload tag
    tag_id = payload[TAG_KEY]
    
    return content_data, style_data, tag_id
