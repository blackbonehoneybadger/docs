class_name LevelGenerator
extends RefCounted
## Builds World 1 (Adygea) entirely in code: background, ground, platforms,
## breakable stone, coins, enemies, checkpoint and the end flag. Gameplay nodes
## are constructed from their scripts so the level never depends on the
## generated .tscn files being present.

const LEVEL_WIDTH: float = 4800.0
const LEVEL_HEIGHT: float = 720.0
const GROUND_Y: float = 600.0
const TILE: float = 48.0

const COLOR_GROUND := Color("#3D7A3D")
const COLOR_GROUND_DIRT := Color("#5A3D22")
const COLOR_PLATFORM := Color("#5B3A1E")
const COLOR_SKY := Color("#87CEEB")
const COLOR_MOUNTAIN := Color("#5B8E5B")

const COIN_SCRIPT := "res://scripts/objects/Coin.gd"
const CHECKPOINT_SCRIPT := "res://scripts/objects/Checkpoint.gd"
const LEVELEND_SCRIPT := "res://scripts/objects/LevelEnd.gd"
const STONEBLOCK_SCRIPT := "res://scripts/objects/StoneBlock.gd"
const FOREST_SPIRIT_SCRIPT := "res://scripts/enemies/ForestSpirit.gd"
const STONE_SNAIL_SCRIPT := "res://scripts/enemies/StoneSnail.gd"
const CAVE_BAT_SCRIPT := "res://scripts/enemies/CaveBat.gd"
const TURRET_SCRIPT := "res://scripts/enemies/Turret.gd"
const QUESTION_BLOCK_SCRIPT := "res://scripts/objects/QuestionBlock.gd"
const WEAPON_PICKUP_SCRIPT := "res://scripts/objects/WeaponPickup.gd"
const POWERUP_SCRIPT := "res://scripts/objects/PowerUpItem.gd"

var player_spawn: Vector2 = Vector2(120, 520)

## Populates `root` with the whole level. Returns the player spawn position.
func build(root: Node2D) -> Vector2:
	_build_background(root)
	_build_ground(root)
	_build_platforms(root)
	_build_breakables(root)
	_build_coins(root)
	_build_question_blocks(root)
	_build_pickups(root)
	_build_enemies(root)
	_build_turrets(root)
	_build_checkpoint(root)
	_build_level_end(root)
	return player_spawn

# ------------------------------- background ----------------------------------

func _build_background(root: Node2D) -> void:
	var sky := ColorRect.new()
	sky.color = COLOR_SKY
	sky.position = Vector2(-200, -400)
	sky.size = Vector2(LEVEL_WIDTH + 400, LEVEL_HEIGHT + 600)
	sky.z_index = -100
	sky.mouse_filter = Control.MOUSE_FILTER_IGNORE
	root.add_child(sky)

	# Repeating mountain silhouettes.
	for i in range(0, int(LEVEL_WIDTH / 400.0) + 1):
		var base_x := i * 400.0
		var mountain := Polygon2D.new()
		mountain.color = COLOR_MOUNTAIN
		mountain.polygon = PackedVector2Array([
			Vector2(base_x, GROUND_Y),
			Vector2(base_x + 200, GROUND_Y - 260),
			Vector2(base_x + 400, GROUND_Y),
		])
		mountain.z_index = -90
		root.add_child(mountain)

# --------------------------------- terrain -----------------------------------

func _build_ground(root: Node2D) -> void:
	# Two pits force jumping; fall into a pit = death plane below.
	var segments := [
		Vector2(0, 1200),
		Vector2(1320, 600),
		Vector2(2040, 1560),
		Vector2(3720, 1080),
	]
	for seg in segments:
		_make_solid(root, Rect2(seg.x, GROUND_Y, seg.y, LEVEL_HEIGHT - GROUND_Y),
			COLOR_GROUND, COLOR_GROUND_DIRT)

func _build_platforms(root: Node2D) -> void:
	# At least 8 platforms at varied heights.
	var platforms := [
		Rect2(360, 504, 144, 24),
		Rect2(620, 432, 144, 24),
		Rect2(900, 360, 120, 24),
		Rect2(1180, 456, 168, 24),
		Rect2(1480, 384, 144, 24),
		Rect2(1800, 312, 120, 24),
		Rect2(2520, 456, 168, 24),
		Rect2(2820, 372, 144, 24),
		Rect2(3180, 300, 120, 24),
		Rect2(3960, 432, 168, 24),
		Rect2(4260, 360, 144, 24),
	]
	for p in platforms:
		_make_solid(root, p, COLOR_PLATFORM, COLOR_PLATFORM.darkened(0.2))

func _build_breakables(root: Node2D) -> void:
	var spots := [Vector2(1180, GROUND_Y - 48), Vector2(2820, 324), Vector2(3960, 384)]
	for s in spots:
		var block := _instance_script(STONEBLOCK_SCRIPT, StaticBody2D.new())
		block.position = s
		root.add_child(block)

# --------------------------------- pickups -----------------------------------

func _build_coins(root: Node2D) -> void:
	# 24 coins (>= 20 required), arched over platforms and across gaps.
	var coin_positions: Array[Vector2] = []
	# Arc over early platforms.
	for base in [Vector2(360, 470), Vector2(620, 398), Vector2(900, 326)]:
		for i in 3:
			coin_positions.append(base + Vector2(i * 40, -10 * sin(i)))
	# Across the first pit.
	for i in 4:
		coin_positions.append(Vector2(1380 + i * 50, 520))
	# Mid-level ground run.
	for i in 6:
		coin_positions.append(Vector2(2120 + i * 70, 540))
	# Over high platforms.
	for base in [Vector2(2820, 330), Vector2(3180, 258), Vector2(4260, 318)]:
		for i in 2:
			coin_positions.append(base + Vector2(i * 40, 0))
	for pos in coin_positions:
		var coin := _instance_script(COIN_SCRIPT, Area2D.new())
		coin.position = pos
		root.add_child(coin)

# --------------------------------- enemies -----------------------------------

func _build_enemies(root: Node2D) -> void:
	# 3x StoneSnail (ground), 2x ForestSpirit (flying), 2x CaveBat (flying).
	for pos in [Vector2(700, 560), Vector2(2300, 560), Vector2(3500, 560)]:
		_spawn_enemy(root, STONE_SNAIL_SCRIPT, pos)
	for pos in [Vector2(1000, 300), Vector2(3000, 280)]:
		_spawn_enemy(root, FOREST_SPIRIT_SCRIPT, pos)
	for pos in [Vector2(1600, 340), Vector2(4000, 320)]:
		_spawn_enemy(root, CAVE_BAT_SCRIPT, pos)

func _spawn_enemy(root: Node2D, script_path: String, pos: Vector2) -> void:
	var enemy := _instance_script(script_path, CharacterBody2D.new())
	enemy.position = pos
	root.add_child(enemy)

func _build_turrets(root: Node2D) -> void:
	# 2x Contra-style turrets on the ground.
	for pos in [Vector2(1500, 552), Vector2(3300, 552)]:
		_spawn_enemy(root, TURRET_SCRIPT, pos)

# ----------------------- Mario-3 ? blocks and pickups ------------------------

func _build_question_blocks(root: Node2D) -> void:
	# [position, content]; placed above platforms so they're bump-reachable.
	var blocks := [
		[Vector2(456, 472), "coin"],
		[Vector2(700, 372), "weapon"],
		[Vector2(1500, 320), "power"],
		[Vector2(2880, 312), "coin"],
		[Vector2(3180, 240), "weapon"],
	]
	for entry in blocks:
		var block := _instance_script(QUESTION_BLOCK_SCRIPT, StaticBody2D.new())
		block.set("content", entry[1])
		block.position = entry[0]
		root.add_child(block)

func _build_pickups(root: Node2D) -> void:
	var weapon := _instance_script(WEAPON_PICKUP_SCRIPT, Area2D.new())
	weapon.position = Vector2(2600, 436)
	root.add_child(weapon)
	var honey := _instance_script(POWERUP_SCRIPT, Area2D.new())
	honey.position = Vector2(3990, 410)
	root.add_child(honey)

# ---------------------------- checkpoint / end -------------------------------

func _build_checkpoint(root: Node2D) -> void:
	var cp := _instance_script(CHECKPOINT_SCRIPT, Area2D.new())
	cp.position = Vector2(2400, GROUND_Y - 32)
	root.add_child(cp)

func _build_level_end(root: Node2D) -> void:
	var flag := _instance_script(LEVELEND_SCRIPT, Area2D.new())
	flag.position = Vector2(4700, GROUND_Y - 40)
	root.add_child(flag)

# --------------------------------- helpers -----------------------------------

func _make_solid(root: Node2D, rect: Rect2, top_color: Color, body_color: Color) -> void:
	var body := StaticBody2D.new()
	body.position = rect.position
	var cs := CollisionShape2D.new()
	var shape := RectangleShape2D.new()
	shape.size = rect.size
	cs.shape = shape
	cs.position = rect.size * 0.5
	body.add_child(cs)

	var fill := ColorRect.new()
	fill.color = body_color
	fill.size = rect.size
	fill.mouse_filter = Control.MOUSE_FILTER_IGNORE
	body.add_child(fill)

	var top := ColorRect.new()
	top.color = top_color
	top.size = Vector2(rect.size.x, minf(12.0, rect.size.y))
	top.mouse_filter = Control.MOUSE_FILTER_IGNORE
	body.add_child(top)

	root.add_child(body)

func _instance_script(script_path: String, fallback: Node) -> Node:
	var node := fallback
	var script: Script = load(script_path)
	if script != null:
		node.set_script(script)
	return node
