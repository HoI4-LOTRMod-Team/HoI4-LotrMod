import requests

key_path = r'C:\Users\ben32801\Documents\Paradox Interactive\Hearts of Iron IV\mod\OPR_KEY.txt'

def query_openrouter(prompt, model="openai/gpt-4o"):
    
    with open(key_path, "r") as f:
        api_key = f.read().strip()

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        json={
            "model": model,
            "messages": [{"role": "user", "content": prompt}]
        }
    )
    
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]