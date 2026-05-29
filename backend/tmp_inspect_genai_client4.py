import inspect
from google import genai
print('has Client', hasattr(genai, 'Client'))
print('Client:', genai.Client)
print('\n=== members ===')
print([name for name, _ in inspect.getmembers(genai.Client, predicate=inspect.isfunction) if not name.startswith('_')])
print('\n=== dir ===')
print([name for name in dir(genai.Client) if not name.startswith('_')])
print('\n=== source snippet ===')
source = inspect.getsource(genai.Client)
print(source[:4000])
