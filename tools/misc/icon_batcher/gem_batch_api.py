import json
import time
from google import genai
from google.genai import types
import os
import base64
from pathlib import Path
from datetime import datetime

def load_api_key():
    # Define the search paths in order of priority
    paths_to_check = [
        "GEM_KEY.txt",            # Current working directory
        "../GEM_KEY.txt",         # One directory up
    ]
    
    for path in paths_to_check:
        if os.path.exists(path):
            with open(path, "r") as f:
                # .strip() removes any accidental spaces or newlines
                return f.read().strip()
    
    raise FileNotFoundError("GEM_KEY.txt not found in current or parent directory.")


# Initialize the client using the loaded key
api_key = load_api_key()
client = genai.Client(api_key=api_key)


def get_jobs_list():
    return client.batches.list(config={'page_size': 20})


def cancel_job(job):
    client.batches.cancel(name=job.name)


def update_job_status(job):
    return client.batches.get(name=job.name)


def retrieve(job):
    if job.state.name == 'JOB_STATE_SUCCEEDED':
        # 1. Setup the directory structure
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_dir = Path.cwd().parent / "retrievals" / timestamp
        output_dir.mkdir(parents=True, exist_ok=True)
        
        result_file_name = job.dest.file_name
        print(f"Results are in file: {result_file_name}")
        print(f"Output directory: {output_dir.resolve()}")

        print("\nDownloading and parsing result file content...")
        file_content_bytes = client.files.download(file=result_file_name)
        file_content = file_content_bytes.decode('utf-8')

        item_counter = 0

        for line in file_content.splitlines():
            if not line.strip():
                continue
                
            parsed_response = json.loads(line)
            request_key = parsed_response.get('key', 'unknown_request')

            # 2. Check for Errors in the response line
            if 'error' in parsed_response:
                err_msg = parsed_response['error'].get('message', 'Unknown error')
                err_code = parsed_response['error'].get('code', 'N/A')
                print(f"⚠️ Error in {request_key}: [{err_code}] {err_msg}")
                continue # Skip to the next line

            # 3. Process Successful Response
            # Safely navigate the nested dictionary
            try:
                candidates = parsed_response.get('response', {}).get('candidates', [])
                if not candidates:
                    print(f"ℹ️ No candidates found for {request_key}")
                    continue

                print(f"✅ Processing success: {request_key}")
                
                for part in candidates[0].get('content', {}).get('parts', []):
                    item_counter += 1
                    
                    # Handle Text Content
                    if 'text' in part:
                        filename = f"output_text_{item_counter}.md"
                        file_path = output_dir / filename
                        with open(file_path, "w", encoding="utf-8") as f:
                            f.write(part['text'])
                        print(f"   -> Saved text to: {filename}")

                    # Handle Image/Multimodal Content
                    elif 'inlineData' in part:
                        mime = part['inlineData']['mimeType']
                        ext = mime.split('/')[-1]
                        data = base64.b64decode(part['inlineData']['data'])
                        
                        filename = f"output_file_{item_counter}.{ext}"
                        file_path = output_dir / filename
                        with open(file_path, "wb") as f:
                            f.write(data)
                        print(f"   -> Saved media ({mime}) to: {filename}")

            except KeyError as e:
                print(f"ERR: Unexpected format in {request_key}: Missing key {e}")




def get_files_list():
    return client.files.list(config={'page_size': 20})

def delete_file(file):
    client.files.delete(name=file.name)

def delete_job(job):
    client.batches.delete(name=job.name)


def upload_file(filepath, name):
    image_file = client.files.upload(
        file=filepath,
        config=types.UploadFileConfig(display_name=name)
    )


def create_job(json_filepath, model_name, job_name="my-batch-job"):
    print(f"Uploading JSONL file: {json_filepath}")
    batch_input_file = client.files.upload(
        file=json_filepath,
        config=types.UploadFileConfig(display_name=job_name+"-json")
    )
    print(f"Uploaded JSONL file: {batch_input_file.name}")

    print("\nCreating batch job...")
    batch_multimodal_job = client.batches.create(
        model=model_name,
        src=batch_input_file.name,
        config={
            'display_name': job_name,
        }
    )
    print(f"Created batch job from file: {batch_multimodal_job.name}")
    print("You can now monitor the job status using its name.")