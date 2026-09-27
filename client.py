from openai import OpenAI
# client = OpenAI()

# defaults to getting the key using os.environ.get("OPENAI_API_KEY")
# If u saved the key under a diff environment variable name, you can do something like:
client = OpenAI(
    api_key="api_key,"
)
completion = client.chat.completions.create(
  model="gpt-3.5-turbo",
  messages=[
    {"role": "system", "content": "You are a virtual assistant named jarvis skilled in general tasks like Alexa and Google Cloud"},
    {"role": "user", "content": "what is coding"}
  ]
)

print(completion.choices[0].message.content)