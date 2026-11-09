from dotenv import load_dotenv
import anthropic

load_dotenv()
client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-haiku-5-5",  # copy a current model name from the docs
    max_tokens=300,
    system="You are a pirate.",
    messages=[{"role": "user", "content": "Explain what an API is in two sentences."}],
)
print(response.content[0].text)
print(response.usage)