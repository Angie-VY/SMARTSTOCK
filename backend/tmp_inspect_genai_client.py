from google import genai
print([a for a in dir(genai.Client) if not a.startswith('_')])
