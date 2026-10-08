class_name Run019Art
# RUN-019 presentation helper: SpriteFrames built from the generated sheets in assets/run019/
# (frame tables follow tools/art/run019/*.py) plus detached effects/sounds that outlive their
# source. Purely visual; no collision, damage, reward or save state.
static var _cache := {}

# anims: {name: [first, count, fps, loop]}; row selects a sheet line of cell height.
static func frames(sheet: Texture2D, cell: Vector2i, anims: Dictionary, row: int = 0) -> SpriteFrames:
	var key := "%s|%s|%d" % [sheet.resource_path, cell, row]
	if _cache.has(key): return _cache[key]
	var result := SpriteFrames.new()
	result.remove_animation(&"default")
	for anim in anims:
		var spec: Array = anims[anim]
		result.add_animation(anim)
		result.set_animation_speed(anim, spec[2])
		result.set_animation_loop(anim, spec[3])
		for i in range(spec[0], spec[0] + spec[1]):
			var region := AtlasTexture.new()
			region.atlas = sheet
			region.region = Rect2(i * cell.x, row * cell.y, cell.x, cell.y)
			result.add_frame(anim, region)
	_cache[key] = result
	return result

# Sprite whose cell is placed by `anchor` (pixel of the cell put on the node origin).
static func sprite(owner: Node, sprite_frames: SpriteFrames, anchor: Vector2, first: StringName, z: int = 0) -> AnimatedSprite2D:
	var art := AnimatedSprite2D.new()
	art.name = &"Art"
	art.sprite_frames = sprite_frames
	art.centered = false
	art.offset = -anchor
	art.z_index = z
	owner.add_child(art)
	art.play(first)
	return art

# Plays `next` once the transitional animation ends (ignored if something else took over).
static func chain(art: AnimatedSprite2D, transition: StringName, next: StringName) -> void:
	art.play(transition)
	var follow := func() -> void:
		if art.animation == transition: art.play(next)
	if art.animation_finished.is_connected(follow): return
	art.animation_finished.connect(follow, CONNECT_ONE_SHOT)

static func holder(node: Node) -> Node:
	var tree := node.get_tree() if node.is_inside_tree() else null
	if tree == null: return null
	var scene := tree.current_scene
	return scene if scene != null and scene != node and not node.is_ancestor_of(scene) else node.get_parent()

# Detached one-shot animation of a multi-animation sheet (enemy deaths); fades out at the end.
static func spawn_anim(from: Node, sprite_frames: SpriteFrames, anim: StringName, at: Vector2, anchor: Vector2, flip: bool, linger: float = 0.5, fade: float = 0.35) -> AnimatedSprite2D:
	var parent := holder(from)
	if parent == null or not parent.is_inside_tree(): return null
	var art := AnimatedSprite2D.new()
	art.sprite_frames = sprite_frames
	art.centered = false
	art.flip_h = flip
	art.offset = -anchor
	art.process_mode = Node.PROCESS_MODE_PAUSABLE
	parent.add_child(art)
	art.global_position = at.round()
	art.play(anim)
	art.animation_finished.connect(func() -> void:
		var tween := art.create_tween()
		tween.tween_interval(linger)
		tween.tween_property(art, "modulate:a", 0.0, fade)
		tween.tween_callback(art.queue_free), CONNECT_ONE_SHOT)
	return art

# Detached strip effect (OneShotFx) placed relative to `from`'s scene.
static func fx(from: Node, strip: Texture2D, cell: Vector2i, fps: float, at: Vector2, anchor: Vector2 = Vector2(0.5, 0.5), flip: bool = false, sound: AudioStream = null, volume_db: float = 0.0) -> OneShotFx:
	var effect := OneShotFx.spawn(holder(from), strip, cell, fps, at, flip, anchor, sound, volume_db)
	if effect != null: effect.process_mode = Node.PROCESS_MODE_PAUSABLE
	return effect

# Hearing radius shared by every world SFX (RUN-021 audio pass). The 640x360 view at the 1.2x camera zoom
# shows ~533x300 px, so 360 px ends just past the screen edges: linear falloff, about -12 dB at the side
# edges, silent beyond. Off-screen turrets, impacts and enemies no longer reach the player.
const SFX_MAX_DISTANCE := 360.0

# Positional sound left in the scene so it survives the source being freed.
static func sound(from: Node, stream: AudioStream, at: Vector2, volume_db: float = -6.0) -> void:
	var parent := holder(from)
	if stream == null or parent == null or not parent.is_inside_tree(): return
	var player := AudioStreamPlayer2D.new()
	player.stream = stream
	player.volume_db = volume_db
	player.max_distance = SFX_MAX_DISTANCE
	player.bus = &"SFX"
	player.process_mode = Node.PROCESS_MODE_PAUSABLE
	parent.add_child(player)
	player.global_position = at
	player.finished.connect(player.queue_free)
	player.play()

# Attached positional sound player (follows its owner while it lives).
static func voice(owner: Node, stream: AudioStream, volume_db: float = -6.0) -> AudioStreamPlayer2D:
	var player := AudioStreamPlayer2D.new()
	player.stream = stream
	player.volume_db = volume_db
	player.max_distance = SFX_MAX_DISTANCE
	player.bus = &"SFX"
	owner.add_child(player)
	return player

# True right after SlicePlayer.take_damage actually applied damage this physics step.
static func just_hurt(player: Node) -> bool:
	return player is SlicePlayer and not player.dead and is_equal_approx(player.invulnerability, SlicePlayer.INVULNERABILITY_DURATION)
