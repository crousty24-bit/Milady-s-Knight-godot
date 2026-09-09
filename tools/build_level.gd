# Authoring tool: regenerate only intentionally. The saved scene is editable normally.
extends SceneTree
const WIDTH = 2240
func _initialize() -> void:
	call_deferred("build")
func add_scene(root_node: Node, parent: Node, path: String, node_name: String, pos: Vector2) -> Node:
	var n = load(path).instantiate()
	n.name = node_name
	parent.add_child(n)
	n.owner = root_node
	if n is Node2D: n.position = pos
	n.process_mode = Node.PROCESS_MODE_PAUSABLE
	return n
func build() -> void:
	var scene = Node2D.new()
	scene.name = "VerticalSlice"
	scene.set_script(load("res://scripts/level.gd"))
	scene.process_mode = Node.PROCESS_MODE_ALWAYS
	var backdrop = Node2D.new()
	backdrop.name = "Kingdom"
	backdrop.set_script(load("res://scripts/kingdom.gd"))
	scene.add_child(backdrop)
	backdrop.owner = scene
	var tileset = TileSet.new()
	tileset.tile_size = Vector2i(16, 16)
	tileset.add_physics_layer()
	tileset.set_physics_layer_collision_layer(0, 9)
	var atlas = TileSetAtlasSource.new()
	atlas.texture = load("res://assets/sprites/world_tileset.png")
	atlas.texture_region_size = Vector2i(16, 16)
	tileset.add_source(atlas, 0)
	for coords in [Vector2i(8,0), Vector2i(8,1)]:
		atlas.create_tile(coords)
		var data = atlas.get_tile_data(coords, 0)
		data.add_collision_polygon(0)
		data.set_collision_polygon_points(0, 0, PackedVector2Array([Vector2(-8,-8), Vector2(8,-8), Vector2(8,8), Vector2(-8,8)]))
	ResourceSaver.save(tileset, "res://assets/kingdom_tileset.tres")
	var terrain = TileMapLayer.new()
	terrain.name = "Terrain"
	terrain.tile_set = tileset
	scene.add_child(terrain)
	terrain.owner = scene
	# x start, x end (exclusive), floor y. The upper ferry spans a 176px gap.
	var runs = [[0,480,144],[480,544,160],[544,608,192],[608,736,224],
		[736,864,224],[912,1280,224],[1280,1344,192],[1344,1408,160],[1408,2240,144],
		[512,560,112],[592,688,48],[688,800,48],[976,1072,48],[1104,1168,80],[1200,1296,112],[1328,1376,112]]
	for run in runs:
		for x in range(run[0]/16, run[1]/16):
			var top: int = run[2]/16
			var bottom: int = 20 if run[2] >= 144 else top + 1
			for y in range(top,bottom):
				terrain.set_cell(Vector2i(x,y),0,Vector2i(8, 0 if y==top else 1))
	# A 48px shaft with 112px walls teaches repeat and alternating wall jumps.
	for x in [39,43]:
		for y in range(-4,3):
			terrain.set_cell(Vector2i(x,y),0,Vector2i(8,0 if y == -4 else 1))
	# Smooth outer limits sit beyond the playable surfaces and cannot be climbed.
	var bounds = StaticBody2D.new()
	bounds.name = "WorldBounds"
	bounds.collision_layer = 1
	scene.add_child(bounds)
	bounds.owner = scene
	for rect in [Rect2(-16,-320,16,640),Rect2(2240,-320,16,640),Rect2(0,-336,2240,16)]:
		var collider = CollisionShape2D.new()
		collider.shape = RectangleShape2D.new()
		collider.shape.size = rect.size
		collider.position = rect.get_center()
		bounds.add_child(collider)
		collider.owner = scene
	var skin = Node2D.new()
	skin.name = "TerrainSkin"
	skin.set_script(load("res://scripts/terrain_skin.gd"))
	scene.add_child(skin)
	skin.owner = scene
	add_scene(scene, scene, "res://scenes/player.tscn", "Player", Vector2(48,140))
	for group_name in ["Coins", "Enemies", "Hazards", "Platforms"]:
		var group = Node2D.new()
		group.name = group_name
		scene.add_child(group)
		group.owner = scene
		group.process_mode = Node.PROCESS_MODE_PAUSABLE
	var coin_data = [Vector3(110,132,0),Vector3(180,132,0),Vector3(260,132,0),Vector3(432,132,0),Vector3(1460,132,0),Vector3(1640,132,0),Vector3(1800,132,0),Vector3(1920,132,0),
		Vector3(536,100,1),Vector3(608,36,1),Vector3(632,-76,1),Vector3(1008,36,1),Vector3(1136,68,1),
		Vector3(680,212,2),Vector3(796,212,2),Vector3(956,212,2),Vector3(1088,212,2),Vector3(1232,212,2)]
	for i in range(coin_data.size()):
		var data = coin_data[i]
		var coin = add_scene(scene, scene.get_node("Coins"), "res://scenes/coin.tscn", "Coin%02d" % (i+1), Vector2(data.x,data.y))
		coin.route = int(data.z)
	var enemy_data = [Vector2(355,144),Vector2(755,224),Vector2(1150,224),Vector2(1740,144),Vector2(752,48),Vector2(1024,48),Vector2(1488,144),Vector2(1872,144)]
	for i in range(enemy_data.size()):
		var enemy = add_scene(scene, scene.get_node("Enemies"), "res://scenes/slime.tscn", "Slime%d" % (i+1), enemy_data[i])
		var patrol: int = 16 if i in [4,5] else (12 if i == 6 else 20)
		enemy.patrol_left = -patrol
		enemy.patrol_right = patrol
		enemy.variant = 1 if i in [2,3,5] else 0
	add_scene(scene, scene.get_node("Platforms"), "res://scenes/moving_platform.tscn", "Ferry", Vector2(816,51))
	for i in range(2):
		add_scene(scene,scene.get_node("Hazards"),"res://scenes/hazard.tscn","Thorns%d" % i,Vector2(1032 if i==0 else 1544,224 if i==0 else 144))
	var pit = Area2D.new()
	pit.name = "Pit"
	pit.collision_layer = 0
	pit.collision_mask = 2
	pit.set_script(load("res://scripts/hazard.gd"))
	pit.lethal = true
	scene.get_node("Hazards").add_child(pit)
	pit.owner = scene
	var shape = CollisionShape2D.new()
	shape.shape = RectangleShape2D.new()
	shape.shape.size = Vector2(2240,32)
	shape.position = Vector2(1120,320)
	pit.add_child(shape)
	shape.owner = scene
	add_scene(scene, scene, "res://scenes/gold_gate.tscn", "GoldGate", Vector2(2072,144))
	var exit_area = Area2D.new()
	exit_area.name = "ExitArea"
	exit_area.collision_layer = 0
	exit_area.collision_mask = 2
	scene.add_child(exit_area)
	exit_area.owner = scene
	var exit_shape = CollisionShape2D.new()
	exit_shape.shape = RectangleShape2D.new()
	exit_shape.shape.size = Vector2(50,100)
	exit_shape.position = Vector2(2160,96)
	exit_area.add_child(exit_shape)
	exit_shape.owner = scene
	var hud = add_scene(scene, scene, "res://scenes/hud.tscn", "HUD", Vector2.ZERO)
	hud.process_mode = Node.PROCESS_MODE_ALWAYS
	var music = AudioStreamPlayer.new()
	music.name = "Music"
	music.stream = load("res://assets/music/time_for_adventure.ogg")
	music.stream.loop = true
	music.volume_db = -24
	scene.add_child(music)
	music.owner = scene
	var packed = PackedScene.new()
	var result = packed.pack(scene)
	if result == OK: result = ResourceSaver.save(packed,"res://scenes/vertical_slice.tscn")
	scene.free()
	print("Build level: ", result)
	quit(result)
