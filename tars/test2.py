import pyttsx3
import tkinter as tk
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
import threading

# Initialize pyttsx3 TTS engine
engine = pyttsx3.init()

# Set properties for voice speed and volume
engine.setProperty("rate", 180)  # Speed (default 200)
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
        self.root.geometry("800x500")
        self.root.configure(bg="black")
        self.context = ""  # Store conversation history
        self.user_inputs = []  # Store user inputs

        # Create main frame
        self.main_frame = tk.Frame(root, bg="black")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Chat display area
        self.chat_display = tk.Text(self.main_frame, wrap=tk.WORD, bg="black", fg="lightgreen", font=("Courier", 10), state=tk.DISABLED, height=20, width=50)
        self.chat_display.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.chat_display.insert(tk.END, "T.A.R.S: How can I assist you?\n\n")

        # User Inputs Section
        self.user_inputs_label = tk.Label(self.main_frame, text="User Inputs", bg="black", fg="white", font=("Courier", 12, "bold"))
        self.user_inputs_label.grid(row=0, column=1, padx=10, pady=5, sticky="n")
        self.history_list = tk.Listbox(self.main_frame, bg="black", fg="white", font=("Courier", 10), height=20, width=30)
        self.history_list.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        # User input field
        self.input_field = tk.Entry(self.main_frame, bg="black", fg="white", font=("Courier", 12))
        self.input_field.grid(row=1, column=0, columnspan=2, padx=20, pady=20, sticky="ew")
        self.input_field.bind("<Return>", self.process_input)

        # Configure grid weights
        self.main_frame.columnconfigure(0, weight=3)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(0, weight=3)
        self.main_frame.rowconfigure(1, weight=0)

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
        else:
            self.chat_display.insert(tk.END, "\n\n")  # Add a blank line after each conversation

    def process_input(self, event=None):
        user_input = self.input_field.get().strip()
        if not user_input:
            return

        self.user_inputs.append(user_input)
        self.history_list.insert(tk.END, f"{len(self.user_inputs)}. {user_input}")

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

        threading.Thread(target=self.speak, args=(result,)).start()
        self.type_text(f"T.A.R.S: {result}\n\n", "lightgreen")  # Extra new line after response

        self.input_field.delete(0, tk.END)  # Clear input box

    def update_chat(self, message, color):
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, message + "\n\n", "message")  # Extra new line
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
