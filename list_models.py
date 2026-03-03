import google.generativeai as genai
import os

key = "AIzaSyBUtbhllzZSx-8BXmYwTa2Fo3CzrHAugXM"
genai.configure(api_key=key)

try:
    print("Listing models...")
    models = list(genai.list_models())
    with open("available_models.txt", "w") as f:
        found_any = False
        for m in models:
            if 'generateContent' in m.supported_generation_methods:
                f.write(f"{m.name}\n")
                found_any = True
        
        if not found_any:
            f.write("No models found that support generateContent.\n")
            
    print("Models listed in available_models.txt")

except Exception as e:
    with open("available_models.txt", "w") as f:
        f.write(f"Error listing models: {e}")
    print(f"Error: {e}")
