from pathlib import Path
p=Path(__file__).resolve().parents[1]
s='''[gd_scene load_steps=2 format=3]
[ext_resource type="Script" path="res://scripts/player.gd" id="1"]
[ext_resource type="Texture2D" path="res://assets/sprites/knight.png" id="2"]
[ext_resource type="AudioStream" path="res://assets/sounds/jump.wav" id="3"]
[ext_resource type="AudioStream" path="res://assets/sounds/hurt.wav" id="4"]
[ext_resource type="AudioStream" path="res://assets/sounds/tap.wav" id="5"]
'''
anims={'idle':[(x,0) for x in range(4)],'run':[(x,2) for x in range(8)],'jump':[(2,5)],'dead':[(x,7) for x in range(4)]}
for name,frames in anims.items():
 for i,(x,y) in enumerate(frames):s+=f'\n[sub_resource type="AtlasTexture" id="{name}{i}"]\natlas = ExtResource("2")\nregion = Rect2({x*32}, {y*32}, 32, 32)\n'
s+='\n[sub_resource type="SpriteFrames" id="frames"]\nanimations = ['
for name,frames in anims.items():
 s+='{"name": &"'+name+'", "speed": '+str(9 if name!='dead' else 6)+', "loop": '+str(name!='dead').lower()+', "frames": ['+','.join('{"duration":1.0,"texture":SubResource("'+name+str(i)+'")}' for i in range(len(frames)))+']},'
s+= ''']
[sub_resource type="CapsuleShape2D" id="body"]
radius = 5.0
height = 18.0
[sub_resource type="RectangleShape2D" id="blade"]
size = Vector2(22, 4)
[node name="Player" type="CharacterBody2D" groups=["player"]]
collision_layer = 2
collision_mask = 1
floor_snap_length = 4.0
script = ExtResource("1")
[node name="Sprite" type="AnimatedSprite2D" parent="."]
position = Vector2(0, -12)
sprite_frames = SubResource("frames")
animation = &"idle"
autoplay = "idle"
[node name="CollisionShape2D" type="CollisionShape2D" parent="."]
position = Vector2(0, -9)
shape = SubResource("body")
[node name="AttackArea" type="Area2D" parent="."]
position = Vector2(17, -12)
collision_layer = 0
collision_mask = 4
monitoring = false
[node name="Shape" type="CollisionShape2D" parent="AttackArea"]
shape = SubResource("blade")
[node name="Camera2D" type="Camera2D" parent="."]
position = Vector2(32, -38)
limit_left = 0
limit_top = -224
limit_right = 2240
limit_bottom = 304
position_smoothing_enabled = true
position_smoothing_speed = 7.0
[node name="JumpSound" type="AudioStreamPlayer" parent="."]
stream = ExtResource("3")
volume_db = -15.0
[node name="HurtSound" type="AudioStreamPlayer" parent="."]
stream = ExtResource("4")
volume_db = -12.0
[node name="SwingSound" type="AudioStreamPlayer" parent="."]
stream = ExtResource("5")
pitch_scale = 0.65
volume_db = -8.0
'''
s=s.replace('load_steps=2',f'load_steps={s.count("[ext_resource")+s.count("[sub_resource")+1}')
(p/'scenes/player.tscn').write_text(s)
