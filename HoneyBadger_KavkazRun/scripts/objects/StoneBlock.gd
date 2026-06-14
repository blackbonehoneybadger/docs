extends StaticBody2D
## A breakable stone block. Boy's ground-pound special can shatter it.

@onready var sprite: Sprite2D = _ensure_sprite()

func _ready() -> void:
	add_to_group("breakable")
	_ensure_collision()
	sprite.texture = PixelArt.make_texture(48, 48, [
		[0, 0, 48, 48, Color("#7A7A82")],
		[2, 2, 44, 44, Color("#8E8E96")],
		[0, 0, 48, 4, Color("#A0A0A8")],
		[20, 0, 4, 48, Color("#6A6A72")],
		[0, 22, 48, 4, Color("#6A6A72")],
	])
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
		shape.size = Vector2(48, 48)
		cs.shape = shape
		cs.position = Vector2(24, 24)
		add_child(cs)

func break_block() -> void:
	var particles := CPUParticles2D.new()
	particles.emitting = true
	particles.one_shot = true
	particles.explosiveness = 0.9
	particles.amount = 12
	particles.lifetime = 0.5
	particles.gravity = Vector2(0, 300)
	particles.initial_velocity_min = 60.0
	particles.initial_velocity_max = 120.0
	particles.color = Color("#8E8E96")
	get_parent().add_child(particles)
	particles.global_position = global_position + Vector2(24, 24)
	AudioManager.play_sfx("stomp")
	queue_free()
