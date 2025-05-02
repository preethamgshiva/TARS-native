import pyttsx3
import tkinter as tk
from tkinter import scrolledtext
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
import threading
import time
import random

# Initialize pyttsx3 TTS engine
engine = pyttsx3.init()
engine.setProperty("rate", 150)  # Speed
engine.setProperty("volume", .5)  # Volume
voices = engine.getProperty("voices")
engine.setProperty("voice", voices[0].id)

# Define chatbot model
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
        self.root.geometry("600x600")
        self.root.configure(bg="black")
        self.context = ""  # Store conversation history

        # Chat display area
        self.chat_display = scrolledtext.ScrolledText(root, wrap=tk.WORD, bg="black", fg="lightgreen", font=("Courier", 8))
        self.chat_display.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        self.chat_display.insert(tk.END, "T.A.R.S: How can I assist you?\n")
        self.chat_display.config(state=tk.DISABLED)

        # User input field
        self.input_field = tk.Entry(root, bg="black", fg="white", font=("Courier", 12))
        self.input_field.pack(padx=20, pady=20, fill=tk.X)
        self.input_field.bind("<Return>", self.process_input)

        # Retro-style Avatar
        self.avatar_canvas = tk.Canvas(root, width=80, height=80, bg="black", highlightthickness=0)
        self.avatar_canvas.place(x=500, y=10)
        self.draw_avatar()

        # Handle window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def speak(self, text):
        """Make TARS speak the text."""
        engine.say(text)
        engine.runAndWait()

    def process_input(self, event=None):
        user_input = self.input_field.get().strip()
        if not user_input:
            return

        self.update_chat(f"You: {user_input}", "white")

        if user_input.lower() in ["exit", "quit", "bye"]:
            self.update_chat("T.A.R.S: Goodbye!", "lightgreen")
            self.root.after(2000, self.root.destroy)
            return
        
        if user_input.lower() in ["thank you", "tq"]:
            self.update_chat("Anytime")

        if user_input.lower() == "clear context":
            self.context = ""

        # Get response from chatbot
        result = chain.invoke({"context": self.context, "question": user_input})
        self.context += f"\nYou: {user_input}\n\nT.A.R.S: {result}\n\n\n"

        # Start speaking and animate avatar
        threading.Thread(target=self.speak, args=(result,)).start()
        self.animate_avatar()
        self.update_chat(f"T.A.R.S: {result}", "lightgreen")
        self.input_field.delete(0, tk.END)

    def update_chat(self, message, color):
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, message + "\n", "message")
        self.chat_display.tag_config("message", foreground=color)
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.yview(tk.END)

    def draw_avatar(self):
        """Draws a simple retro pixelated avatar."""
        self.avatar_canvas.create_rectangle(20, 10, 60, 50, outline="lightgreen", width=2)  # Head
        self.avatar_canvas.create_rectangle(30, 50, 50, 70, outline="lightgreen", width=2)  # Body
        self.avatar_canvas.create_line(30, 55, 20, 70, fill="lightgreen", width=2)  # Left Arm
        self.avatar_canvas.create_line(50, 55, 60, 70, fill="lightgreen", width=2)  # Right Arm
        self.avatar_canvas.create_line(35, 70, 35, 80, fill="lightgreen", width=2)  # Left Leg
        self.avatar_canvas.create_line(45, 70, 45, 80, fill="lightgreen", width=2)  # Right Leg

    def animate_avatar(self):
        """Simple animation effect by toggling eyes."""
        for _ in range(3):
            self.avatar_canvas.create_oval(30, 20, 35, 25, fill="lightgreen", outline="lightgreen")  # Left Eye
            self.avatar_canvas.create_oval(45, 20, 50, 25, fill="lightgreen", outline="lightgreen")  # Right Eye
            self.root.update()
            time.sleep(0.2)
            self.avatar_canvas.create_rectangle(30, 20, 35, 25, fill="black", outline="black")  # Blink Left Eye
            self.avatar_canvas.create_rectangle(45, 20, 50, 25, fill="black", outline="black")  # Blink Right Eye
            self.root.update()
            time.sleep(0.2)

    def on_close(self):
        engine.stop()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = TARSChatbot(root)
    root.mainloop()
