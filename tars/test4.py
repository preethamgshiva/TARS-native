import pyttsx3
import tkinter as tk
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
import threading
import time

# Initialize pyttsx3 TTS engine
engine = pyttsx3.init()

# Set properties for voice speed and volume
engine.setProperty("rate", 200)  # Speed (default 200)
engine.setProperty("volume", 1)  # Volume level (0.0 to 1.0)

# Try to set a robotic voice (voice settings might differ by system)
voices = engine.getProperty("voices")
engine.setProperty("voice", voices[0].id)  # Use index to pick a voice

# Define the chatbot model
template = """
Answer the question below.

Here is the conversation history: {context}

Question: {question}

Answer:
"""

model = OllamaLLM(model="llama3.2:1b")
prompt = ChatPromptTemplate.from_template(template)
chain = prompt | model

class TARSChatbot:
    def __init__(self, root):
        self.root = root
        self.root.title("T.A.R.S.")
        self.root.geometry("500x500")
        self.root.configure(bg="black")
        self.context = ""  # Store conversation history
        self.timer_running = False

        # Chat display area without scrollbar
        self.chat_display = tk.Text(root, wrap=tk.WORD, bg="black", fg="lightgreen", font=("Courier", 12), state=tk.DISABLED)
        self.chat_display.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        self.chat_display.insert(tk.END, "T.A.R.S: How can I assist you?\n\n")
        self.chat_display.config(state=tk.DISABLED)

        # User input field
        self.input_field = tk.Entry(root, bg="black", fg="white", font=("Courier", 12))
        self.input_field.pack(padx=20, pady=20, fill=tk.X)
        self.input_field.bind("<Return>", self.process_input)

        # Handle window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def speak(self, text):
        """Make TARS speak the text."""
        engine.say(text)
        engine.runAndWait()

    def type_text(self, text, color, index=0):
        """Displays text one character at a time for typing effect."""
        if index < len(text):
            self.chat_display.config(state=tk.NORMAL)
            self.chat_display.insert(tk.END, text[index], "message")
            self.chat_display.tag_config("message", foreground=color)
            self.chat_display.config(state=tk.DISABLED)
            self.chat_display.yview(tk.END)  # Auto-scroll
            self.root.after(50, self.type_text, text, color, index + 1)

    def process_input(self, event=None):
        user_input = self.input_field.get().strip()
        if not user_input:
            return

        self.update_chat(f"You: {user_input}", "white")

        if user_input.lower() in ["exit", "quit", "bye"]:
            self.update_chat("T.A.R.S: Goodbye!", "lightgreen")
            self.root.after(2000, self.root.destroy)  # Close window after 2s
            return

        if user_input.lower() == "clear context":
            self.context = ""

        if user_input.lower().startswith("start timer"):
            self.start_timer()
            return

        # Get response from chatbot
        result = chain.invoke({"context": self.context, "question": user_input})
        self.context += f"\nYou: {user_input}\n\nT.A.R.S: {result}\n\n\n"

        # Start speaking and typing at the same time
        threading.Thread(target=self.speak, args=(result,)).start()
        self.type_text(f"T.A.R.S: {result}\n\n", "lightgreen")
        self.input_field.delete(0, tk.END)  # Clear input box

    def start_timer(self):
        """Starts a timer and displays elapsed time in the chat display."""
        if not self.timer_running:
            self.timer_running = True
            threading.Thread(target=self.run_timer, daemon=True).start()

    def run_timer(self):
        start_time = time.time()
        while self.timer_running:
            elapsed_time = int(time.time() - start_time)
            self.update_chat(f"T.A.R.S: Timer running... {elapsed_time} seconds", "lightgreen")
            time.sleep(1)

    def update_chat(self, message, color):
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, message + "\n", "message")
        self.chat_display.tag_config("message", foreground=color)
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.yview(tk.END)  # Auto-scroll

    def on_close(self):
        """Close the application and stop the speech engine."""
        engine.stop()  # Stop any ongoing speech
        self.timer_running = False  # Stop the timer
        self.root.destroy()  # Close the GUI

# Run the chatbot GUI
if __name__ == "__main__":
    root = tk.Tk()
    app = TARSChatbot(root)
    root.mainloop()
