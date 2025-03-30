import openai

openai.api_key = "your_grok_api_key"

prompt = """
Compare the following Figma design and actual website properties:

Figma Button:
- Text: "Sign Up"
- Color: "#FF5733"

Website Button:
- Text: "Register"
- Color: "#FF0000"

Generate test cases to validate the differences.
"""

response = openai.ChatCompletion.create(
    model="grok-1",
    messages=[{"role": "system", "content": prompt}]
)

print(response["choices"][0]["message"]["content"])
