import os, json, time
token_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "kis_token_cache.json")
print("Path:", token_file)
if os.path.exists(token_file):
    with open(token_file, "r") as f:
        data = json.load(f)
    print("Token valid for:", 82800 - (time.time() - data.get("timestamp", 0)))
else:
    print("File not found")
