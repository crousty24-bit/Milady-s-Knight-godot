extends Area2D
signal collected(value: int)
@export_enum("Common", "Upper", "Lower") var route: int = 0
# A defeat reward is already credited by the level. This reuses the coin art as feedback.
var bonus_feedback: int = 0
var picked_up: bool = false
var elapsed: float = 0.0
# RUN-016 presentation (Claude): kill rewards are shards, shown in violet (docs/06), not as gold.
const SHARD_TEXTURE = preload("res://assets/sprites/item_shard.png")
const SHARD_BURST = preload("res://assets/sprites/vfx_shard_burst.png")
const SHARD_SFX = preload("res://assets/sounds/sfx_shard_gain.tres")
func _ready() -> void:
	body_entered.connect(_on_body_entered)
	elapsed = position.x * 0.08
	if bonus_feedback > 0:
		picked_up = true
		monitoring = false
		$Shape.set_deferred("disabled", true)
		$Sprite.hide()
		var shard := AnimatedSprite2D.new()
		shard.sprite_frames = OneShotFx.strip_frames(SHARD_TEXTURE, Vector2i(10, 12), 12.0, true)
		shard.play()
		add_child(shard)
		var at := global_position
		var world := get_parent()
		(func() -> void: OneShotFx.spawn(world, SHARD_BURST, Vector2i(20, 20), 18.0, at)).call_deferred()
		$Sound.stream = SHARD_SFX
		$Sound.play()
		var label := Label.new()
		label.text = "+%d SHARDS" % bonus_feedback
		label.add_theme_color_override("font_color", Color(0.753, 0.541, 0.831))
		label.add_theme_color_override("font_shadow_color", Color(0.09, 0.075, 0.106))
		label.add_theme_constant_override("shadow_offset_x", 1)
		label.add_theme_constant_override("shadow_offset_y", 1)
		label.add_theme_font_override("font", preload("res://assets/fonts/PixelOperator8.ttf"))
		label.add_theme_font_size_override("font_size", 8)
		label.position = Vector2(-20, -18)
		label.mouse_filter = Control.MOUSE_FILTER_IGNORE
		add_child(label)
		var tween := create_tween().set_parallel()
		tween.tween_property(self, "position:y", position.y - 18.0, 0.65)
		tween.tween_property(self, "modulate:a", 0.0, 0.3).set_delay(0.35)
		tween.chain().tween_callback(queue_free)
func _process(delta: float) -> void:
	elapsed += delta
	$Sprite.position.y = sin(elapsed * 3.0) * 1.5
func _on_body_entered(body: Node2D) -> void:
	if picked_up or not body is SlicePlayer or body.dead: return
	picked_up = true
	$Shape.set_deferred("disabled", true)
	# Gold burst where the coin was (tools/art/vfx.py), then nothing remains.
	$Sprite.play("collect")
	$Sprite.animation_finished.connect($Sprite.hide, CONNECT_ONE_SHOT)
	$Sound.play()
	collected.emit(1)
	await $Sound.finished
	queue_free()
