extends Area2D
## Collectible coin. Spins, and on player contact adds to the coin counter.

var _collected: bool = false
var _time: float = 0.0

@onready var sprite: Sprite2D = _ensure_sprite()

func _ready() -> void:
	add_to_group("coins")
	_ensure_collision()
	sprite.texture = _build_texture()
	# Detect the player body (collision layer 2).
	collision_layer = 0
	collision_mask = 0
	set_collision_mask_value(2, true)
	monitoring = true
	body_entered.connect(_on_body_entered)

func _process(delta: float) -> void:
	_time += delta
	sprite.scale.x = 0.4 + 0.6 * absf(cos(_time * 4.0))
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
		var shape := CircleShape2D.new()
		shape.radius = 7.0
		cs.shape = shape
		add_child(cs)

func _build_texture() -> Texture2D:
	var gold := Color("#F2C400")
	var shine := Color("#FFF0A0")
	var edge := Color("#B88900")
	return PixelArt.make_texture(12, 12, [
		[3, 1, 6, 10, gold],
		[1, 3, 10, 6, gold],
		[2, 2, 8, 8, gold],
		[4, 3, 2, 5, shine],
		[3, 0, 6, 1, edge],
		[3, 11, 6, 1, edge],
	])

func _on_body_entered(body: Node) -> void:
	if _collected or not body.is_in_group("player"):
		return
	_collected = true
	GameManager.add_coin(1)
	AudioManager.play_sfx("coin")
	queue_free()
