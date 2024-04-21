import requests
import json

def llama_request(prompt, model_name):
    payload={"model":model_name, "prompt":prompt, "stream": False}
    while(True):
        try:
            r = requests.post("http://localhost:11434/api/generate", data=json.dumps(payload))
            return json.loads(r.text)["response"]
        except Exception as e:
            print(e)
            continue

if(__name__ == "__main__"):
    print(llama_request("Once upon a time", "mixtral:8x7b"))