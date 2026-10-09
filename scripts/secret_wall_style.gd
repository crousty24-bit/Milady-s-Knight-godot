# Secret wall hint style (RUN-021 Claude art): how the entrance of a secret wall betrays itself,
# reusable per wall, level or biome. Data only: no gameplay, collision, save or sound. Drawn by
# SecretWallHint above the SecretWallMask; the textures are white alpha masks (see
# tools/art/run021/secrets/secret_hints.py) so the colours below set the look.
class_name SecretWallStyle
extends Resource
# GLOW: faint light seeping through the joints (drawn additively).
# CRACKS: hairline crack across the courses (N4's first variant).
# TINT: entrance stones a touch warmer/paler than the masonry around.
enum Variant { GLOW, CRACKS, TINT }
@export var variant: Variant = Variant.CRACKS
# Main layer and an optional second one (crack lip, glow embers); null layers are skipped.
@export var texture: Texture2D
@export var detail_texture: Texture2D
@export var hint_color: Color = Color.WHITE
@export var detail_color: Color = Color.WHITE
# Scales the alpha of both layers.
@export_range(0.0, 1.0, 0.01) var intensity: float = 1.0
# Additive blending (light) instead of the normal mix (stone marks, tints).
@export var additive: bool = false
# Slow breathing of the hint: alpha dips by at most pulse_amount once per pulse_period; 0 = still.
@export_range(0.0, 0.5, 0.01) var pulse_amount: float = 0.0
@export_range(1.0, 12.0, 0.1) var pulse_period: float = 4.0
