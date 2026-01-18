

import json


#requests_data = [
#    # First request: simple text prompt
#    {"key": "request_1", "request": {"contents": [{"parts": [{"text": "Explain how AI works in a few words"}]}]}},
#    # Second request: multi-modal prompt with text and an image reference
#    {
#        "key": "request_2_image",
#        "request": {
#            "contents": [{
#                "parts": [
#                    {"text": "What is in this image? Describe it in detail."},
#                    {"file_data": {"file_uri": image_file.uri, "mime_type": image_file.mime_type}}
#                ]
#            }]
#        }
#    }
#]

requests_data = [
    {"key": "image_request_1", "request": {"contents": [{"parts": [{"text": "A big letter A surrounded by animals starting with the A letter"}]}],'generation_config': {'response_modalities': ['TEXT', 'IMAGE']}}}, # Be careful, for inline request it would be 'config' instead of 'generation_config'
    {"key": "image_request_2", "request": {"contents": [{"parts": [{"text": "A big letter B surrounded by animals starting with the B letter"}]}],'generation_config': {'response_modalities': ['TEXT', 'IMAGE']}}},
]

json_file_path = 'batch_image_gen_requests.json'

print(f"\nCreating JSONL file: {json_file_path}")
with open(json_file_path, 'w') as f:
    for req in requests_data:
        f.write(json.dumps(req) + '\n')