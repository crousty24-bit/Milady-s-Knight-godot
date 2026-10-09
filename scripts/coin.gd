extends Area2D
signal collected(value: int)
@export_enum("Common", "Upper", "Lower") var route: int = 0
# A defeat reward is already credited by the level. The shard presentation is noncollectible feedback.
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
		# The "+N SHARDS" text joins the level queue above the knight (RUN-021) so lines never overlap.
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
