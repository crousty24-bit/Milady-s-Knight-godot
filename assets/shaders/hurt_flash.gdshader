shader_type canvas_item;

uniform float white_flash : hint_range(0.0, 1.0) = 0.0;

void fragment() {
	// COLOR already contains the sprite texture and modulation; preserve its alpha.
	COLOR.rgb = mix(COLOR.rgb, vec3(1.0), white_flash);
}
