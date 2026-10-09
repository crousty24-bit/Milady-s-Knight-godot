extends StaticBody2D
signal revealed
signal passage_revealed
signal save_error(error: int)
@export var secret_id: String = ""
@export var fade_duration: float = 0.6
@export var cover_rect: Rect2 = Rect2()
@export var hint_style: Resource
@export var intro_enabled: bool = false
@export_range(16, 256, 1) var intro_radius: float = 64.0
var opened: bool = false
var passage_open: bool = false
var save_failed: bool = false
var progression: Node
var mask_art: Node2D
var hint_art: Node2D
func _ready() -> void:
	_build_art()
	add_to_group("durable_items")
	add_to_group("secret_walls")
	progression = get_node_or_null("/root/Progression")
	if progression != null and not secret_id.is_empty() and progression.permanent_flags.get("secret:" + secret_id, false):
		_open(false)
func receive_player_attack(_amount: float, source: int) -> bool:
	if opened or source not in [SlicePlayer.DamageSource.CONTACT_MELEE, SlicePlayer.DamageSource.PROJECTILE]: return false
	var error: int = ERR_INVALID_PARAMETER
	if progression != null and not secret_id.is_empty():
		error = progression.set_permanent_flag("secret:" + secret_id)
	if error != OK:
		save_failed = true
		save_error.emit(error)
		return false
	save_failed = false
	_open(true)
	return true
func _open(animate: bool) -> void:
	opened = true
	if animate:
		revealed.emit()
		var tween := create_tween()
		tween.tween_property(self, "modulate:a", 0.0, maxf(0.0, fade_duration))
		tween.tween_callback(_finish_open.bind(true))
	else:
		_finish_open(false)
func _finish_open(animate: bool) -> void:
	passage_open = true
	$Shape.set_deferred("disabled", true)
	hide()
	if animate: passage_revealed.emit()
# --- Presentation (RUN-019 Claude art/SFX): looks like the stone wall; the reveal crumbles while
# the existing fade runs. Already-acquired secrets stay hidden without replaying it.
const WALL = preload("res://assets/run019/world/env_secret_wall.png")
const CRUMBLE = preload("res://assets/run019/world/vfx_secret_crumble.png")
const REVEAL_SFX = preload("res://assets/sounds/run019/sfx_secret_reveal.wav")
func _build_art() -> void:
	var art := Sprite2D.new()
	art.texture = WALL
	art.hframes = 2
	art.centered = false
	art.offset = Vector2(-8, -32)
	add_child(art)
	if cover_rect.has_area():
		var terrain := get_parent().get_parent().get_node_or_null("Terrain") as TileMapLayer
		if terrain != null:
			mask_art = load("res://scripts/secret_wall_mask.gd").new()
			mask_art.name = "SecretMask"
			add_child(mask_art)
			mask_art.configure(terrain, cover_rect)
			art.hide()
	if hint_style != null:
		hint_art = load("res://scripts/secret_wall_hint.gd").new()
		hint_art.name = "SecretHint"
		add_child(hint_art)
		hint_art.configure(hint_style, Rect2(-8, -32, 16, 32))
	revealed.connect(func() -> void:
		var effect := Run019Art.fx(self, CRUMBLE, Vector2i(32, 40), 16.0, global_position, Vector2(0.5, 36.0 / 40.0), false, REVEAL_SFX, -3.0)
		if effect != null and mask_art != null:
			effect.z_index = mask_art.z_index + (2 if hint_art != null else 1))
