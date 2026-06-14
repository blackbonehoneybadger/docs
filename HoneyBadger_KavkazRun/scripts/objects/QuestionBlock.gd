extends StaticBody2D
## Mario-3 "?" block. Bumping it from below (head-first while rising) pops out
## its contents — a coin, a weapon power-up or a honey jar — then goes inert.
## Set `content` ("coin" | "weapon" | "power") before adding it to the tree.

@export var content: String = "coin"

var _used: bool = false
@onready var sprite: Sprite2D = _ensure_sprite()

func _ready() -> void:
	add_to_group("question_block")
	_ensure_collision()
	_ensure_bump_zone()
	sprite.texture = _build_texture(false)
	sprite.centered = false

func _ensure_sprite() -> Sprite2D:
	var n := get_node_or_null("Sprite") as Sprite2D
	if n == null:
		n = Sprite2D.new()
		n.name = "Sprite"
		add_child(n)
	return n

func _ensure_collision() -> void:
	if get_node_or_null("Collision") == null:
		var cs := CollisionShape2D.new()
		cs.name = "Collision"
		var shape := RectangleShape2D.new()
		shape.size = Vector2(32, 32)
		cs.shape = shape
		cs.position = Vector2(16, 16)
		add_child(cs)

func _ensure_bump_zone() -> void:
	var zone := Area2D.new()
	zone.name = "BumpZone"
	zone.collision_layer = 0
	zone.collision_mask = 0
	zone.set_collision_mask_value(2, true)  # player body
	zone.monitoring = true
	var cs := CollisionShape2D.new()
	var shape := RectangleShape2D.new()
	shape.size = Vector2(28, 10)
	cs.shape = shape
	cs.position = Vector2(16, 34)  # just below the block
	zone.add_child(cs)
	add_child(zone)
	zone.body_entered.connect(_on_bump)

func _build_texture(used: bool) -> Texture2D:
	var face := Color("#6A6A72") if used else Color("#E8A82A")
	var edge := Color("#3A3A40") if used else Color("#A8761A")
	var mark := Color("#3A3A40") if used else Color("#FFFFFF")
	return PixelArt.make_texture(32, 32, [
		[0, 0, 32, 32, edge],
		[2, 2, 28, 28, face],
		[13, 8, 6, 4, mark],   # "?" top
		[17, 12, 2, 4, mark],
		[14, 16, 4, 3, mark],
		[14, 22, 4, 4, mark],  # dot
	])

func _on_bump(body: Node) -> void:
	if _used or not body.is_in_group("player"):
		return
	var v: Variant = body.get("velocity")
	if not (v is Vector2) or v.y >= 0.0:
		return  # must be rising into the block
	_used = true
	sprite.texture = _build_texture(true)
	# Little upward nudge of the block.
	var tween := create_tween()
	tween.tween_property(sprite, "position", Vector2(0, -6), 0.06)
	tween.tween_property(sprite, "position", Vector2(0, 0), 0.08)
	_spawn_content()

func _spawn_content() -> void:
	match content:
		"weapon":
			_spawn_pickup("res://scripts/objects/WeaponPickup.gd")
		"power":
			_spawn_pickup("res://scripts/objects/PowerUpItem.gd")
		_:
			GameManager.add_coin(1)
			AudioManager.play_sfx("coin")

func _spawn_pickup(script_path: String) -> void:
	var item := Area2D.new()
	item.set_script(load(script_path))
	get_parent().add_child(item)
	item.global_position = global_position + Vector2(16, -2)
	var tween := item.create_tween()
	tween.tween_property(item, "global_position",
		global_position + Vector2(16, -22), 0.25).set_trans(Tween.TRANS_QUAD)
