extends SceneTree

func _initialize() -> void:
	var expected := OS.get_environment("MILADY_TEST_USER_ROOT").replace("\\", "/").simplify_path().trim_suffix("/")
	var actual := OS.get_user_data_dir().replace("\\", "/").simplify_path().trim_suffix("/")
	if OS.get_name() == "Windows":
		expected = expected.to_lower()
		actual = actual.to_lower()
	var isolated := expected.is_absolute_path() and actual.begins_with(expected + "/")
	print("USER_DATA_DIR ", OS.get_user_data_dir())
	print("PASS " if isolated else "FAIL ", "user:// belongs to the isolated test profile")
	print("RESULT 1 user data path checks; ", 0 if isolated else 1, " failures")
	quit(0 if isolated else 1)
