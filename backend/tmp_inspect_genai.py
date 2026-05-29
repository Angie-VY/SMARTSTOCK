import google
from google import genai
print('google module:', google.__name__)
print('genai module:', genai.__name__)
print('has Client', hasattr(genai, 'Client'))
print('has Model', hasattr(genai, 'Model'))
print('has TextModel', hasattr(genai, 'TextModel'))
print([a for a in dir(genai) if 'Client' in a or 'Model' in a][:20])
