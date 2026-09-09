"""Update keyboard bindings while preserving all other Godot settings."""
from pathlib import Path
import re

p = Path(__file__).resolve().parents[1] / 'project.godot'
s = p.read_text()
# Up/down are reserved: this platformer currently only walks horizontally.
actions = {'move_left': [81], 'move_right': [68], 'move_up': [90],
           'move_down': [83], 'jump': [32], 'attack': [70],
           'interact': [69], 'restart': [82], 'pause': [4194305]}
section = re.search(r'(?ms)^\[input\]\n(.*?)(?=^\[|\Z)', s)
body = section.group(1) if section else '\n'
for action, keys in actions.items():
    events = ', '.join('Object(InputEventKey,"keycode":%s)' % k for k in keys)
    entry = f'{action}={{\n"deadzone": 0.2,\n"events": [{events}]\n}}'
    pattern = rf'(?ms)^{re.escape(action)}=\{{.*?^\}}'
    if re.search(pattern, body):
        body = re.sub(pattern, lambda _: entry, body)
    else:
        body = body.rstrip() + '\n\n' + entry + '\n\n'
if section:
    s = s[:section.start(1)] + body + s[section.end(1):]
else:
    s += '\n[input]\n' + body
p.write_text(s)
