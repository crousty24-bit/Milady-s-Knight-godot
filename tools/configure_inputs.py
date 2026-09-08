from pathlib import Path
p=Path(__file__).resolve().parents[1]/'project.godot'
s=p.read_text().split('\n[input]')[0]
actions={'move_left':[81,65,4194319],'move_right':[68,4194321],'jump':[32],'attack':[74,88],'interact':[69],'restart':[82],'pause':[4194305]}
s+='\n[input]\n'
for action,keys in actions.items():
 events=', '.join('Object(InputEventKey,"keycode":%s)'%k for k in keys)
 s+=f'\n{action}={{\n"deadzone": 0.2,\n"events": [{events}]\n}}\n'
p.write_text(s)
