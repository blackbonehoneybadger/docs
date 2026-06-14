extends Area2D
## Contra-style weapon power-up. On contact upgrades the player's weapon level
## (single → spread → rapid).

var _taken: bool = false
var _time: float = 0.0

@onready var sprite: Sprite2D = _ensure_sprite()

func _ready() -> void:
	add_to_group("weapon_pickup")
	_ensure_collision()
	sprite.texture = _build_texture()
	collision_layer = 0
	collision_mask = 0
	set_collision_mask_value(2, true)  # player body
	monitoring = true
	body_entered.connect(_on_body_entered)

func _process(delta: float) -> void:
	_time += delta
	sprite.position.y = sin(_time * 3.0) * 2.0

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
		shape.size = Vector2(18, 14)
		cs.shape = shape
		add_child(cs)

func _build_texture() -> Texture2D:
	var box := Color("#C0392B")
	var metal := Color("#ECECEC")
	return PixelArt.make_texture(18, 14, [
		[0, 0, 18, 14, box],
		[2, 2, 14, 10, Color("#8E2418")],
		[3, 6, 11, 3, metal],   # barrel
		[12, 4, 3, 7, metal],   # body
	])

func _on_body_entered(body: Node) -> void:
	if _taken or not body.is_in_group("player"):
		return
	_taken = true
	if body.has_method("upgrade_weapon"):
		body.upgrade_weapon()
	GameManager.add_score(150)
	queue_free()
