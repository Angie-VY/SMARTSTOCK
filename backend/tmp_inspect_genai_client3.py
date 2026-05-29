from google import genai
client = genai.Client()
print([a for a in dir(client) if not a.startswith('_')])
print('\nmodels attrs:', [a for a in dir(client.models) if not a.startswith('_')][:50])
