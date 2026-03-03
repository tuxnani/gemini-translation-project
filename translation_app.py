import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import google.generativeai as genai
import os
import json
import time
import threading
import re

# Configuration for CustomTkinter
ctk.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class TranslationApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Gemini Auto-Translator")
        self.geometry("900x700")

        # Variables
        self.file_path = ctk.StringVar()
        self.api_key = ctk.StringVar()
        self.source_lang = ctk.StringVar(value="English")
        self.target_lang = ctk.StringVar(value="Telugu")
        self.model_name = ctk.StringVar(value="gemini-3-flash-preview")
        self.status_message = ctk.StringVar(value="Ready")
        self.is_processing = False
        self.stop_event = threading.Event()
        
        # Load API key if saved
        self.config_file = "config.json"
        self.load_config()

        self.create_ui()

    def create_ui(self):
        # Grid Configuration
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(5, weight=1)

        # Header
        self.header_label = ctk.CTkLabel(self, text="Gemini Auto-Translator", font=ctk.CTkFont(size=24, weight="bold"))
        self.header_label.grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 10), sticky="ew")

        # API Key Section
        self.api_label = ctk.CTkLabel(self, text="Gemini API Key:")
        self.api_label.grid(row=1, column=0, padx=20, pady=10, sticky="w")
        self.api_entry = ctk.CTkEntry(self, textvariable=self.api_key, show="*")
        self.api_entry.grid(row=1, column=1, padx=20, pady=10, sticky="ew")

        # Model Selection Section
        self.model_label = ctk.CTkLabel(self, text="Model:")
        self.model_label.grid(row=1, column=2, padx=(0, 20), pady=10, sticky="w")
        self.model_dropdown = ctk.CTkOptionMenu(self, variable=self.model_name, values=["gemini-3-flash-preview", "gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"])
        self.model_dropdown.grid(row=1, column=3, padx=(0, 20), pady=10)
        
        # File Selection Section
        self.file_label = ctk.CTkLabel(self, text="Input Text File:")
        self.file_label.grid(row=2, column=0, padx=20, pady=10, sticky="w")
        self.file_entry = ctk.CTkEntry(self, textvariable=self.file_path, state="readonly")
        self.file_entry.grid(row=2, column=1, padx=(20, 10), pady=10, sticky="ew")
        self.browse_btn = ctk.CTkButton(self, text="Browse", command=self.browse_file)
        self.browse_btn.grid(row=2, column=2, padx=20, pady=10)

        # Language Selection Section
        self.lang_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.lang_frame.grid(row=3, column=0, columnspan=3, padx=20, pady=10, sticky="ew")
        
        self.source_label = ctk.CTkLabel(self.lang_frame, text="Source Language:")
        self.source_label.pack(side="left", padx=(0, 10))
        self.source_dropdown = ctk.CTkOptionMenu(self.lang_frame, variable=self.source_lang, values=["English", "Telugu", "Hindi"])
        self.source_dropdown.pack(side="left", padx=10)

        self.arrow_label = ctk.CTkLabel(self.lang_frame, text="➔", font=ctk.CTkFont(size=18))
        self.arrow_label.pack(side="left", padx=20)

        self.target_label = ctk.CTkLabel(self.lang_frame, text="Output Language:")
        self.target_label.pack(side="left", padx=10)
        self.target_dropdown = ctk.CTkOptionMenu(self.lang_frame, variable=self.target_lang, values=["English", "Telugu", "Hindi"])
        self.target_dropdown.pack(side="left", padx=10)

        # Prompt Section
        self.prompt_label = ctk.CTkLabel(self, text="Custom Instructions (Prompt):")
        self.prompt_label.grid(row=4, column=0, padx=20, pady=(10, 0), sticky="nw")
        self.prompt_text = ctk.CTkTextbox(self, height=100)
        self.prompt_text.grid(row=5, column=0, columnspan=3, padx=20, pady=(5, 10), sticky="nsew")
        self.prompt_text.insert("1.0", "Translate the following text from {source} to {target} in a colloquial fashion. Do not add any introductory or concluding remarks. Just the translation. Maintain the original meaning and tone.")

        # Progress Section
        self.progress_bar = ctk.CTkProgressBar(self)
        self.progress_bar.grid(row=6, column=0, columnspan=3, padx=20, pady=(10, 5), sticky="ew")
        self.progress_bar.set(0)

        self.status_label = ctk.CTkLabel(self, textvariable=self.status_message, text_color="gray")
        self.status_label.grid(row=7, column=0, columnspan=3, padx=20, pady=(0, 10), sticky="ew")

        # Action Buttons
        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.grid(row=8, column=0, columnspan=3, padx=20, pady=20)

        self.start_btn = ctk.CTkButton(self.button_frame, text="Start Translation", command=self.start_thread, width=150, height=40, font=ctk.CTkFont(size=14, weight="bold"))
        self.start_btn.pack(side="left", padx=20)

        self.stop_btn = ctk.CTkButton(self.button_frame, text="Stop/Pause", command=self.stop_process, width=150, height=40, fg_color="#D32F2F", hover_color="#C62828")
        self.stop_btn.pack(side="left", padx=20)

    def browse_file(self):
        filename = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if filename:
            self.file_path.set(filename)

    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r") as f:
                    config = json.load(f)
                    self.api_key.set(config.get("api_key", ""))
            except:
                pass

    def save_config(self):
        config = {"api_key": self.api_key.get()}
        try:
            with open(self.config_file, "w") as f:
                json.dump(config, f)
        except:
            pass

    def start_thread(self):
        if not self.file_path.get():
            messagebox.showerror("Error", "Please select a file.")
            return
        if not self.api_key.get():
            messagebox.showerror("Error", "Please enter Gemini API Key.")
            return

        if self.is_processing:
            return

        # Validate API Key
        self.status_message.set("Validating API Key...")
        self.update_idletasks() # Force UI update
        if not self.validate_api_key(self.api_key.get()):
            self.status_message.set("Error: Invalid API Key")
            messagebox.showerror("Error", "Invalid API Key or Network Issue.\nPlease check your key and try again.")
            return

        self.save_config()
        self.stop_event.clear()
        self.is_processing = True
        self.start_btn.configure(state="disabled")
        self.browse_btn.configure(state="disabled")
        
        thread = threading.Thread(target=self.process_translation)
        thread.start()

    def validate_api_key(self, key):
        try:
            genai.configure(api_key=key)
            # Use currently selected model for validation
            model = genai.GenerativeModel(self.model_name.get())
            # Dry run generation to verify key
            response = model.generate_content("test")
            return True
        except Exception as e:
            print(f"API Validation Error: {e}")
            return False

    def stop_process(self):
        if self.is_processing:
            self.stop_event.set()
            self.status_message.set("Stopping after current chunk...")


    def process_translation(self):
        try:
            input_file = self.file_path.get()
            source = self.source_lang.get()
            target = self.target_lang.get()
            user_prompt = self.prompt_text.get("1.0", "end-1c")
            api_key = self.api_key.get()
            current_model_name = self.model_name.get()

            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(current_model_name)

            # Setup Processing Directories
            # Use filename and a simple hash to create a unique folder for this file's processing
            base_name = os.path.basename(input_file).replace('.txt', '')
            file_hash = str(abs(hash(input_file)))
            
            # processing/{filename_hash}/
            project_dir = os.path.join(os.path.dirname(input_file), "processing", f"{base_name}_{file_hash}")
            raw_dir = os.path.join(project_dir, "raw")
            output_dir = os.path.join(project_dir, "output")

            os.makedirs(raw_dir, exist_ok=True)
            os.makedirs(output_dir, exist_ok=True)

            self.status_message.set("Checking existing processing state...")

            # 1. Prepare Raw Chunks (if not already done)
            chunks = []
            existing_raw_files = sorted(os.listdir(raw_dir))
            
            if not existing_raw_files:
                self.status_message.set("Formatting and chunking text...")
                with open(input_file, "r", encoding="utf-8") as f:
                    raw_text = f.read()
                
                formatted_text = self.reformat_text(raw_text)
                chunks = self.chunk_text(formatted_text)
                
                # Save chunks to raw folder
                for i, chunk in enumerate(chunks):
                    chunk_file = os.path.join(raw_dir, f"chunk_{i:04d}.txt")
                    with open(chunk_file, "w", encoding="utf-8") as f:
                        f.write(chunk)
            else:
                self.status_message.set("Loading existing chunks...")
                # Load chunks from files to ensure consistency
                for filename in existing_raw_files:
                    if filename.endswith(".txt"):
                        with open(os.path.join(raw_dir, filename), "r", encoding="utf-8") as f:
                            chunks.append(f.read())

            total_chunks = len(chunks)

            # 2. Translation Loop
            processed_count = 0
            
            for i, chunk in enumerate(chunks):
                if self.stop_event.is_set():
                    self.status_message.set("Process Stopped.")
                    break

                output_file = os.path.join(output_dir, f"chunk_{i:04d}.txt")
                
                # Check if already translated
                if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
                    processed_count += 1
                    continue

                self.status_message.set(f"Translating chunk {i+1}/{total_chunks}...")
                self.progress_bar.set((i) / total_chunks)
                
                final_prompt = user_prompt.format(source=source, target=target) + "\n\nTEXT TO TRANSLATE:\n" + chunk
                
                translation = self.translate_with_retry(model, final_prompt)
                
                if translation is None:
                    self.status_message.set("Error: Failed to translate chunk. Check API/Network/Quota.")
                    return

                # Save immediately to output file
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(translation)
                
                processed_count += 1

            # 3. Final Output Assembly
            if processed_count == total_chunks:
                self.status_message.set("Combining translated files...")
                final_output_file = input_file.replace(".txt", f"_translated_{target}.txt")
                
                with open(final_output_file, "w", encoding="utf-8") as outfile:
                    for i in range(total_chunks):
                        chunk_out_path = os.path.join(output_dir, f"chunk_{i:04d}.txt")
                        if os.path.exists(chunk_out_path):
                            with open(chunk_out_path, "r", encoding="utf-8") as infile:
                                outfile.write(infile.read() + "\n\n")
                
                self.progress_bar.set(1)
                self.status_message.set(f"Done! Saved to {os.path.basename(final_output_file)}")
                messagebox.showinfo("Success", "Translation Completed Successfully!")
            else:
                 self.status_message.set(f"Paused. {processed_count}/{total_chunks} completed.")

        except Exception as e:
            self.status_message.set(f"Error: {str(e)}")
            print(f"Error detail: {e}")
            messagebox.showerror("Error", str(e))
        finally:
            self.is_processing = False
            self.start_btn.configure(state="normal")
            self.browse_btn.configure(state="normal")

    def reformat_text(self, text):
        # Merge lines: remove single newline, keep double newline (paragraph break)
        # Strategy: Replace double newline with a placeholder, remove single newlines, then restore paragraphs
        # Or simpler: Split by double newline, join each paragraph's internal lines with space, then join paragraphs with double newline
        
        paragraphs = re.split(r'\n\s*\n', text)
        cleaned_paragraphs = []
        for p in paragraphs:
            # Replace single newlines with space
            cleaned = p.replace('\n', ' ')
            # Collapse multiple spaces
            cleaned = re.sub(r'\s+', ' ', cleaned).strip()
            if cleaned:
                cleaned_paragraphs.append(cleaned)
        
        return "\n\n".join(cleaned_paragraphs)

    def chunk_text(self, text, max_chars=4000):
        # Split into chunks ensuring sentences don't break halfway
        sentences = re.split(r'(?<=[.!?|])\s+', text)
        chunks = []
        current_chunk = ""

        for sentence in sentences:
            if len(current_chunk) + len(sentence) < max_chars:
                current_chunk += sentence + " "
            else:
                chunks.append(current_chunk.strip())
                current_chunk = sentence + " "
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks

    def translate_with_retry(self, model, prompt, retries=5):
        delay = 2
        for attempt in range(retries):
            if self.stop_event.is_set():
                return None
            try:
                response = model.generate_content(prompt)
                if response.text:
                    return response.text
            except Exception as e:
                error_str = str(e)
                self.status_message.set(f"Retry {attempt+1}/{retries}: {e}")
                
                # Check for Quota Exhausted (429)
                if "429" in error_str or "quota" in error_str.lower() or "serviceunavailable" in error_str.lower():
                    # Fallback logic
                    current_model = self.model_name.get()
                    if "gemini-3" in current_model:
                         self.status_message.set("Quota exceeded. Switching to fallback: gemini-2.5-flash...")
                         self.model_name.set("gemini-2.5-flash")
                         try:
                             new_model = genai.GenerativeModel("gemini-2.5-flash")
                             response = new_model.generate_content(prompt)
                             if response.text:
                                 return response.text
                         except Exception as fallback_e:
                             self.status_message.set(f"Fallback failed too: {fallback_e}")
                
                time.sleep(delay)
                delay *= 2 # Exponential backoff
        return None

if __name__ == "__main__":
    app = TranslationApp()
    app.mainloop()
