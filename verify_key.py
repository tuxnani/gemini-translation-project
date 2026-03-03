import google.generativeai as genai
import os
import sys

key = <add key here>

try:
    genai.configure(api_key=key)
    model = genai.GenerativeModel('gemini-3-flash-preview')
    response = model.generate_content("Hello")
    with open("error_log.txt", "w") as f:
        f.write("SUCCESS")
except Exception as e:
    with open("error_log.txt", "w") as f:
        f.write(f"{type(e).__name__}: {e}")
    sys.exit(1)

