from pathlib import Path
p=Path(__file__).resolve().parents[1]
def save(name,s):
 s='[gd_scene load_steps=%d format=3]\n'%(s.count('[ext_resource')+s.count('[sub_resource')+1)+s
 (p/'scenes'/f'{name}.tscn').write_text(s)
s='''[ext_resource type="Script" path="res://scripts/slime.gd" id="1"]
[ext_resource type="Texture2D" path="res://assets/sprites/slime_green.png" id="2"]
[ext_resource type="AudioStream" path="res://assets/sounds/hurt.wav" id="3"]
'''
for i in range(4):s+=f'[sub_resource type="AtlasTexture" id="f{i}"]\natlas = ExtResource("2")\nregion = Rect2({i*24},24,24,24)\n'
s+='[sub_resource type="SpriteFrames" id="frames"]\nanimations = [{"name": &"idle", "speed": 6.0, "loop": true, "frames": ['+','.join('{"duration":1.0,"texture":SubResource("f'+str(i)+'")}' for i in range(4))+']}]\n'
s+='''[sub_resource type="RectangleShape2D" id="body"]
size = Vector2(14, 12)
[sub_resource type="RectangleShape2D" id="contact"]
size = Vector2(15, 12)
[node name="Slime" type="CharacterBody2D" groups=["enemies"]]
collision_layer = 4
collision_mask = 1
script = ExtResource("1")
[node name="Sprite" type="AnimatedSprite2D" parent="."]
position = Vector2(0, -12)
sprite_frames = SubResource("frames")
autoplay = "idle"
[node name="CollisionShape2D" type="CollisionShape2D" parent="."]
position = Vector2(0,-6)
shape = SubResource("body")
[node name="EdgeRay" type="RayCast2D" parent="."]
position = Vector2(-10,-6)
target_position = Vector2(0,16)
collision_mask = 1
[node name="ContactArea" type="Area2D" parent="."]
collision_layer = 0
collision_mask = 2
[node name="Shape" type="CollisionShape2D" parent="ContactArea"]
position = Vector2(0,-6)
shape = SubResource("contact")
[node name="HitSound" type="AudioStreamPlayer" parent="."]
stream = ExtResource("3")
pitch_scale = 1.4
volume_db = -16.0
'''
save('slime',s)
s='''[ext_resource type="Script" path="res://scripts/coin.gd" id="1"]
[ext_resource type="Texture2D" path="res://assets/sprites/coin.png" id="2"]
[ext_resource type="AudioStream" path="res://assets/sounds/coin.wav" id="3"]
'''
for i in range(12):s+=f'[sub_resource type="AtlasTexture" id="f{i}"]\natlas = ExtResource("2")\nregion = Rect2({i*16},0,16,16)\n'
s+='[sub_resource type="SpriteFrames" id="frames"]\nanimations = [{"name": &"idle", "speed": 10.0, "loop": true, "frames": ['+','.join('{"duration":1.0,"texture":SubResource("f'+str(i)+'")}' for i in range(12))+']}]\n'
s+='''[sub_resource type="CircleShape2D" id="shape"]
radius = 7.0
[node name="Coin" type="Area2D"]
collision_layer = 0
collision_mask = 2
script = ExtResource("1")
[node name="Sprite" type="AnimatedSprite2D" parent="."]
sprite_frames = SubResource("frames")
autoplay = "idle"
[node name="Shape" type="CollisionShape2D" parent="."]
shape = SubResource("shape")
[node name="Sound" type="AudioStreamPlayer" parent="."]
stream = ExtResource("3")
volume_db = -15.0
'''
save('coin',s)
save('hazard','''[ext_resource type="Script" path="res://scripts/hazard.gd" id="1"]
[sub_resource type="RectangleShape2D" id="shape"]
size = Vector2(30, 10)
[node name="Hazard" type="Area2D"]
collision_layer = 0
collision_mask = 2
script = ExtResource("1")
[node name="Shape" type="CollisionShape2D" parent="."]
position = Vector2(0, -4)
shape = SubResource("shape")
''')
save('moving_platform','''[ext_resource type="Script" path="res://scripts/moving_platform.gd" id="1"]
[sub_resource type="RectangleShape2D" id="shape"]
size = Vector2(34, 6)
[node name="MovingPlatform" type="AnimatableBody2D"]
collision_layer = 1
collision_mask = 0
script = ExtResource("1")
[node name="Shape" type="CollisionShape2D" parent="."]
shape = SubResource("shape")
one_way_collision = true
''')
save('gold_gate','''[ext_resource type="Script" path="res://scripts/gold_gate.gd" id="1"]
[ext_resource type="AudioStream" path="res://assets/sounds/coin.wav" id="2"]
[sub_resource type="RectangleShape2D" id="wall"]
size = Vector2(16, 100)
[sub_resource type="RectangleShape2D" id="area"]
size = Vector2(88, 60)
[node name="GoldGate" type="Node2D"]
script = ExtResource("1")
[node name="Barrier" type="StaticBody2D" parent="."]
collision_layer = 1
[node name="Shape" type="CollisionShape2D" parent="Barrier"]
position = Vector2(0, -48)
shape = SubResource("wall")
[node name="OfferingArea" type="Area2D" parent="."]
position = Vector2(-25, -24)
collision_layer = 0
collision_mask = 2
[node name="Shape" type="CollisionShape2D" parent="OfferingArea"]
shape = SubResource("area")
[node name="Sound" type="AudioStreamPlayer" parent="."]
stream = ExtResource("2")
pitch_scale = 0.5
volume_db = -10.0
''')
s='''[ext_resource type="Script" path="res://scripts/hud.gd" id="1"]
[ext_resource type="FontFile" path="res://assets/fonts/PixelOperator8.ttf" id="2"]
[sub_resource type="Theme" id="theme"]
default_font = ExtResource("2")
default_font_size = 8
[node name="HUD" type="CanvasLayer"]
layer = 10
script = ExtResource("1")
[node name="Top" type="ColorRect" parent="."]
offset_right = 320.0
offset_bottom = 23.0
color = Color(0.047,0.063,0.075,0.94)
mouse_filter = 2
[node name="Rule" type="ColorRect" parent="."]
offset_top = 22.0
offset_right = 320.0
offset_bottom = 23.0
color = Color(0.46,0.38,0.25,1)
mouse_filter = 2
[node name="Bottom" type="ColorRect" parent="."]
offset_top = 161.0
offset_right = 320.0
offset_bottom = 180.0
color = Color(0.047,0.063,0.075,0.94)
mouse_filter = 2
'''
def label(name,parent,x,y,w,h,text):
 return f'''[node name="{name}" type="Label" parent="{parent}"]
offset_left = {float(x)}
offset_top = {float(y)}
offset_right = {float(x+w)}
offset_bottom = {float(y+h)}
theme = SubResource("theme")
text = "{text}"
mouse_filter = 2
'''
s+=label('Health','.',8,7,90,12,'VIE')+label('Gold','.',117,7,139,12,'OR 00 / 12')+label('PauseHint','.',271,7,45,12,'ECHAP')
s+=label('Hint','.',7,165,306,14,'')+'theme_override_font_sizes/font_size = 8\nhorizontal_alignment = 1\n'
s+='''[node name="Overlay" type="ColorRect" parent="."]
visible = false
offset_top = 23.0
offset_right = 320.0
offset_bottom = 161.0
color = Color(0.035,0.044,0.055,0.91)
mouse_filter = 2
'''
s+=label('Title','Overlay',8,37,304,18,'')+'horizontal_alignment = 1\ntheme_override_colors/font_color = Color(0.94,0.8,0.5,1)\n'
s+=label('Subtitle','Overlay',8,67,304,42,'')+'horizontal_alignment = 1\n'
save('hud',s)
