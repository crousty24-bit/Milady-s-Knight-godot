extends StaticBody2D
signal contacted(player: SlicePlayer)

func _ready() -> void:
	_build_art()

func _physics_process(_delta: float) -> void:
	for body in $Contact.get_overlapping_bodies():
		if body is SlicePlayer and not body.dead:
			var away := signf(to_local(body.global_position).x)
			if is_zero_approx(away): away = -body.facing
			body.take_damage(1.0, Vector2(away * 90.0, -180.0).rotated(global_rotation), SlicePlayer.DamageSource.SOLID_TRAP)
			contacted.emit(body)

# --- Presentation (RUN-019 Claude art/SFX): snap and spores only when the contact hurts.
const SHEET = preload("res://assets/run019/world/trap_poison_plant.png")
const ANIMS = {&"idle": [0, 6, 6, true], &"snap": [6, 3, 16, false]}
const SPORES = preload("res://assets/run019/world/vfx_poison_spores.png")
const HIT_SFX = preload("res://assets/sounds/run019/sfx_poison_plant_hit.wav")
var _art: AnimatedSprite2D

func _build_art() -> void:
	_art = Run019Art.sprite(self, Run019Art.frames(SHEET, Vector2i(28, 28), ANIMS), Vector2(14, 28), &"idle")
	contacted.connect(func(player: SlicePlayer) -> void:
		if not Run019Art.just_hurt(player): return
		Run019Art.chain(_art, &"snap", &"idle")
		Run019Art.fx(self, SPORES, Vector2i(20, 16), 14.0, player.global_position + Vector2(0, -12), Vector2(0.5, 0.5), false, HIT_SFX, -5.0))
