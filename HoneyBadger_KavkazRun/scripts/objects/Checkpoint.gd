extends Area2D
## Mid-level checkpoint. First time the player touches it, it records the
## respawn position and raises its flag.

var _activated: bool = false

@onready var pole: Sprite2D = _ensure_pole()
@onready var flag: Sprite2D = _ensure_flag()

func _ready() -> void:
	add_to_group("checkpoint")
	_ensure_collision()
	collision_layer = 0
	collision_mask = 0
	set_collision_mask_value(2, true)
	monitoring = true
	pole.texture = _build_pole_texture()
	flag.texture = _build_flag_texture(false)
	flag.position = Vector2(8, -24)
	body_entered.connect(_on_body_entered)

func _ensure_pole() -> Sprite2D:
	var n := get_node_or_null("Pole") as Sprite2D
	if n == null:
		n = Sprite2D.new()
		n.name = "Pole"
		add_child(n)
	return n

func _ensure_flag() -> Sprite2D:
	var n := get_node_or_null("Flag") as Sprite2D
	if n == null:
		n = Sprite2D.new()
		n.name = "Flag"
		add_child(n)
	return n

func _ensure_collision() -> void:
	if get_node_or_null("Collision") == null:
		var cs := CollisionShape2D.new()
		cs.name = "Collision"
		var shape := RectangleShape2D.new()
		shape.size = Vector2(16, 64)
		cs.shape = shape
		add_child(cs)

func _build_pole_texture() -> Texture2D:
	return PixelArt.make_texture(4, 64, [[0, 0, 4, 64, Color("#9A9A9A")]])

func _build_flag_texture(active: bool) -> Texture2D:
	var col := Color("#FFD000") if active else Color("#888888")
	return PixelArt.make_texture(16, 12, [
		[0, 0, 16, 12, col],
		[0, 0, 16, 1, Color(0, 0, 0, 0.3)],
	])

func _on_body_entered(body: Node) -> void:
	if _activated or not body.is_in_group("player"):
		return
	_activated = true
	GameManager.set_checkpoint(global_position)
	flag.texture = _build_flag_texture(true)
	flag.position.y = -52
	AudioManager.play_sfx("coin")
