class_name OneShotFx
extends AnimatedSprite2D
# RUN-016 presentation helper: plays a horizontal strip once at a world point (optionally with a
# sound), then frees itself. Purely visual; no collision or gameplay state.
static var _frames_cache := {}

static func strip_frames(strip: Texture2D, frame_size: Vector2i, fps: float, loop: bool = false) -> SpriteFrames:
	var key := "%s|%s|%s|%s" % [strip.resource_path, frame_size, fps, loop]
	if _frames_cache.has(key): return _frames_cache[key]
	var frames := SpriteFrames.new()
	frames.set_animation_speed("default", fps)
	frames.set_animation_loop("default", loop)
	for i in range(strip.get_width() / frame_size.x):
		var region := AtlasTexture.new()
		region.atlas = strip
		region.region = Rect2(i * frame_size.x, 0, frame_size.x, frame_size.y)
		frames.add_frame("default", region)
	_frames_cache[key] = frames
	return frames

# anchor: point of the frame placed at `at` (0..1 of the frame); mirrored when flipped.
static func spawn(parent: Node, strip: Texture2D, frame_size: Vector2i, fps: float, at: Vector2, flip: bool = false, anchor: Vector2 = Vector2(0.5, 0.5), sound: AudioStream = null, volume_db: float = 0.0) -> OneShotFx:
	if parent == null or not parent.is_inside_tree(): return null
	var fx := OneShotFx.new()
	fx.sprite_frames = strip_frames(strip, frame_size, fps)
	fx.centered = false
	fx.flip_h = flip
	fx.offset = Vector2(-(1.0 - anchor.x if flip else anchor.x) * frame_size.x, -anchor.y * frame_size.y).round()
	fx.z_index = 5
	parent.add_child(fx)
	fx.global_position = at.round()
	fx.animation_finished.connect(fx._finished)
	fx.play()
	if sound != null:
		var player := AudioStreamPlayer2D.new()
		player.stream = sound
		player.volume_db = volume_db
		player.bus = &"SFX"
		fx.add_child(player)
		player.play()
	return fx

func _finished() -> void:
	hide()
	for child in get_children():
		if child is AudioStreamPlayer2D and child.playing:
			await child.finished
	queue_free()
