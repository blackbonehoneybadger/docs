extends Area2D
## End-of-level flag. On player contact, notifies the active level.

var _triggered: bool = false

@onready var pole: Sprite2D = _ensure_pole()
@onready var flag: Sprite2D = _ensure_flag()

func _ready() -> void:
	add_to_group("level_end")
	_ensure_collision()
	collision_layer = 0
	collision_mask = 0
	set_collision_mask_value(2, true)
	monitoring = true
	pole.texture = PixelArt.make_texture(4, 80, [[0, 0, 4, 80, Color("#C0C0C0")]])
	flag.texture = PixelArt.make_texture(20, 16, [
		[0, 0, 20, 16, Color("#E03030")],
		[4, 4, 12, 8, Color("#FFFFFF")],
	])
	flag.position = Vector2(10, -32)
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
		shape.size = Vector2(20, 80)
		cs.shape = shape
		add_child(cs)

func _on_body_entered(body: Node) -> void:
	if _triggered or not body.is_in_group("player"):
		return
	_triggered = true
	for level in get_tree().get_nodes_in_group("level"):
		if level.has_method("complete_level"):
			level.complete_level()
