import pyttsx3
import tkinter as tk
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
import threading
from tkinter import scrolledtext

# Initialize pyttsx3 TTS engine
engine = pyttsx3.init()

# Set properties for voice speed and volume
engine.setProperty("rate", 200)  # Speed (default 200)
engine.setProperty("volume", .5)  # Volume level (0.0 to 1.0)

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
        self.root.geometry("500x300")  # Changed to remove the default scrollbar width
        self.context = ""  # Store conversation history
        self.chat_display = None  # To store the text in the chat window

        # Chat display area
        self.chat_display = scrolledtext.ScrolledText(root, bg="black", fg="lightgreen", font=("Courier", 12))
        self.chat_display.pack(padx=10, pady=10)
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

    def type_text(self, text, color):
        """Displays text one character at a time for typing effect."""
        if self.chat_display:
            return

        self.chat_display = self.root.create_window(10, 100, anchor='nw', width=500, height=200)  # Create the chat window
        for char in text:
            self.chat_display.insert(tk.END, char)
            self.chat_display.tag_config("message", foreground=color)
            self.chat_display.config(state=tk.DISABLED)
            self.chat_display.yview(tk.END)  # Auto-scroll

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

        # Get response from chatbot
        result = chain.invoke({"context": self.context, "question": user_input})
        self.context += f"\nYou: {user_input}\n\nT.A.R.S: {result}\n\n\n"

        # Start speaking and typing at the same time
        # Thread to speak the text
        threading.Thread(target=self.speak, args=(result,)).start()
        

        # Start the typing effect of the text
        self.type_text(f"T.A.R.S: {result}\n\n", "lightgreen")

        self.input_field.delete(0, tk.END)  # Clear input box

    def update_chat(self, message, color):
        if self.chat_display:
            return

        self.chat_display = self.root.create_window(10, 100, anchor='nw', width=500, height=200)
        for line in message.split('\n'):
            self.chat_display.insert(tk.END, line + "\n")
            self.chat_display.tag_config("message", foreground=color)
            self.chat_display.config(state=tk.DISABLED)
            self.chat_display.yview(tk.END)  # Auto-scroll

    def on_close(self):
        """Close the application and stop the speech engine."""
        engine.stop()  # Stop any ongoing speech
        self.root.destroy()  # Close the GUI

# Run the chatbot GUI
if __name__ == "__main__":
    root = tk.Tk()
    app = TARSChatbot(root)
    root.mainloop()