from langchain_ollama import OllamaLLM

model = OllamaLLM(model="llama3.2:1b")


while True:
    user_input = input("You: ")
    result = model.invoke(user_input)
    print(f"Bot: {result}\n")

    if user_input.lower() in ["exit","quit","stop"]:
        print("Goodbye!")
        break