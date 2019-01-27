import os
import sys
import importlib


sys.path.append(os.path.join(os.path.dirname(__file__)))

detected_envs = {}

for key in ('PROD', 'DEV', 'TEST', 'STAGE'):
    val = os.environ.get(key)
    if val:
        detected_envs.update({key: val})

if len(detected_envs) == 0:
    env = 'DEV'
elif len(detected_envs) > 1:
    raise ValueError('No predefined environment detected!')
else:
    env = detected_envs.popitem()[0]

print('Considered {} envirnment'.format(env))

environment = importlib.import_module('{}'.format(env.lower()))

module_dict = environment.__dict__
try:
    to_import = environment.__all__
except AttributeError:
    to_import = [name for name in module_dict if not name.startswith('_')]

globals().update({name: module_dict[name] for name in to_import})
