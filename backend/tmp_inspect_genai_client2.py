from google import genai
print('has Client', hasattr(genai, 'Client'))
print('Client:', genai.Client)
print([a for a in dir(genai.Client) if not a.startswith('_')])
