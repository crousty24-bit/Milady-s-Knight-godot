# RUN-021: N4 music wiring check (stream, loop, bus, pause/resume, loop wrap, level enter/exit voices).
# Usage: bash work/run021/check.sh audio-check --headless --script res://tools/art/run021/audio_check.gd
extends SceneTree
const LEVEL := "res://scenes/forbidden_graveyard.tscn"
const MUSIC := "res://assets/run021/audio/music_n4_forbidden_graveyard.ogg"
var checks := 0
var failures := 0
func _initialize() -> void: call_deferred("run")
func check(ok: bool, label: String) -> void:
	checks += 1
	print("PASS " if ok else "FAIL ", label)
	if not ok: failures += 1
func frames(count: int) -> void:
	for i in count:
		await process_frame
func seconds(duration: float) -> void:
	var end := Time.get_ticks_msec() + int(duration * 1000.0)
	while Time.get_ticks_msec() < end: await process_frame
func music_voices() -> Array:
	var found: Array = []
	for node in root.find_children("*", "AudioStreamPlayer", true, false):
		var player := node as AudioStreamPlayer
		if player.bus == &"Music" and player.playing: found.append(player)
	return found
func run() -> void:
	var progress = root.get_node("Progression")
	progress.persistence_enabled = false
	progress.new_game()
	var level: Node2D = load(LEVEL).instantiate()
	var music := level.get_node("Music") as AudioStreamPlayer
	check(music.stream != null and music.stream.resource_path == MUSIC, "Music stream = " + str(music.stream.resource_path if music.stream else null))
	check(music.bus == &"Music", "Music bus = " + str(music.bus))
	check(is_equal_approx(music.volume_db, -24.0), "Music volume_db = %.1f (baseline -24.0, unchanged)" % music.volume_db)
	var stream := music.stream as AudioStreamOggVorbis
	check(stream != null and stream.loop, "stream.loop = " + str(stream.loop if stream else null))
	check(stream != null and absf(stream.loop_offset - 5.564) < 0.001, "stream.loop_offset = %.3f" % (stream.loop_offset if stream else -1.0))
	check(stream != null and absf(stream.get_length() - 185.274) < 0.01, "stream length = %.3f s" % (stream.get_length() if stream else -1.0))
	root.add_child(level)
	current_scene = level
	await frames(5)
	check(music.playing, "level enter: Music playing")
	check(music_voices().size() == 1, "level enter: exactly one playing voice on bus Music (%d)" % music_voices().size())
	var ambient := level.get_node("Ambient") as AudioStreamPlayer
	check(ambient.playing and ambient.bus == &"Ambient", "Ambient playing on bus Ambient (separate voice)")
	await seconds(0.5)
	var before := music.get_playback_position()
	check(before > 0.2, "playback advances (%.2f s)" % before)
	# Pause / resume through the SceneTree pause used by the level pause menu and modals.
	# The level root is PROCESS_MODE_ALWAYS (as in N3), so Music/Ambient keep playing under a tree pause:
	# the checks assert that behaviour (no restart, no duplicate voice, no stuck pause) and its consistency.
	check(level.process_mode == Node.PROCESS_MODE_ALWAYS and music.can_process(), "level root ALWAYS: Music keeps processing under pause (by design, as before)")
	paused = true
	await frames(3)
	var held := music.get_playback_position()
	check(not music.stream_paused and music.playing, "tree paused: Music still playing, stream_paused = " + str(music.stream_paused))
	await seconds(0.5)
	var after_pause := music.get_playback_position()
	check(after_pause > held + 0.3, "tree paused: continuous playback, no restart (%.2f -> %.2f)" % [held, after_pause])
	check(music_voices().size() == 1, "tree paused: still exactly one voice (%d)" % music_voices().size())
	paused = false
	await frames(3)
	await seconds(0.5)
	check(music.playing and music.get_playback_position() > after_pause + 0.3 and music_voices().size() == 1, "tree resumed: continuous, one voice (%.2f -> %.2f)" % [after_pause, music.get_playback_position()])
	# Loop wrap: start 0.4 s before the end, the position must return to the loop offset.
	music.play(stream.get_length() - 0.4)
	await seconds(1.0)
	var wrapped := music.get_playback_position()
	check(music.playing and wrapped > 5.5 and wrapped < 7.5, "loop wrap: playing, position %.2f s (expected near loop_offset 5.564 + ~0.6)" % wrapped)
	# Level exit: _exit_tree stops Music and Ambient; no leftover voice.
	level.queue_free()
	await frames(5)
	check(music_voices().size() == 0, "level exit: no playing voice on bus Music (%d)" % music_voices().size())
	# Re-enter (retry / second visit): still exactly one voice.
	var second: Node2D = load(LEVEL).instantiate()
	root.add_child(second)
	current_scene = second
	await frames(5)
	check(music_voices().size() == 1, "re-enter: exactly one playing voice (%d)" % music_voices().size())
	second.queue_free()
	await frames(5)
	check(music_voices().size() == 0, "second exit: no playing voice (%d)" % music_voices().size())
	await seconds(0.3)
	print("RESULT checks=%d failures=%d" % [checks, failures])
	quit(1 if failures > 0 else 0)
