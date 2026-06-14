extends Area2D
## Mario-3 style power-up. On contact raises the player's max HP by 1 and heals.

var _taken: bool = false
var _time: float = 0.0

@onready var sprite: Sprite2D = _ensure_sprite()

func _ready() -> void:
	add_to_group("powerup")
	_ensure_collision()
	sprite.texture = _build_texture()
	collision_layer = 0
	collision_mask = 0
	set_collision_mask_value(2, true)  # player body
	monitoring = true
	body_entered.connect(_on_body_entered)

func _process(delta: float) -> void:
	_time += delta
	sprite.position.y = sin(_time * 3.5) * 2.0

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
		shape.size = Vector2(16, 16)
		cs.shape = shape
		add_child(cs)

func _build_texture() -> Texture2D:
	# Honey jar — heals and toughens the badger.
	var jar := Color("#E8A02A")
	var lid := Color("#7A4A1E")
	var shine := Color("#FFE9A8")
	return PixelArt.make_texture(16, 16, [
		[2, 4, 12, 11, jar],
		[2, 2, 12, 3, lid],
		[4, 6, 3, 6, shine],
		[6, 8, 6, 4, Color("#C97E18")],
	])

func _on_body_entered(body: Node) -> void:
	if _taken or not body.is_in_group("player"):
		return
	_taken = true
	if body.has_method("power_up"):
		body.power_up()
	GameManager.add_score(200)
	queue_free()
