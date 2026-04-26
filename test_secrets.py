import os
s_path = os.path.join(os.path.dirname(__file__), ".streamlit", "secrets.toml")
fallback_secrets = {}
try:
    if os.path.exists(s_path):
        with open(s_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    k = k.strip()
                    v = v.split("#")[0].strip()
                    if v.startswith('"') and v.endswith('"'): v = v[1:-1]
                    elif v.startswith("'") and v.endswith("'"): v = v[1:-1]
                    fallback_secrets[k] = v
except Exception as e:
    print("Fallback parse error:", e)

print("FALLBACK KEYS:", fallback_secrets.keys())
print("FALLBACK VAL:", fallback_secrets.get("KIS_APP_KEY"))

import streamlit as st
print("ST SECRETS:", st.secrets.get("KIS_APP_KEY", "NOT_FOUND"))
val = st.secrets.get("KIS_APP_KEY", os.environ.get("KIS_APP_KEY", fallback_secrets.get("KIS_APP_KEY", "")))
print("FINAL RESULT:", val)
