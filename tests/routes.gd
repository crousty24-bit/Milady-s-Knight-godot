extends SceneTree
const Driver = preload("res://tests/route_driver.gd")
var failures := 0
func _initialize() -> void: call_deferred("run")
func run() -> void:
	for upper in [true, false]:
		var driver = Driver.new(self)
		await driver.start()
		await driver.upper() if upper else await driver.lower()
		await driver.approach()
		await driver.finish()
		driver.release_inputs()
		var ok: bool = not driver.failed and driver.level.finished and driver.level.gold == 0 and driver.level.bonus == driver.enemy_rewards + 1 and driver.level.reward_settled and driver.level.progression.banked_bonus == driver.starting_bank + driver.level.bonus
		print("PASS " if ok else "FAIL ", "routes ", upper, " pos=", driver.player.position, " hp=", driver.player.health, " seal=", driver.level.gold, " bonus=", driver.level.bonus)
		if not ok: failures += 1
		if DisplayServer.get_name() != "headless":
			await process_frame
			await RenderingServer.frame_post_draw
			root.get_texture().get_image().save_png("res://work/routes-" + str(upper) + ".png")
		await driver.close()
	print("RESULT 2 routes checks; ", failures, " failures")
	OS.delay_msec(300)
	quit(failures)
