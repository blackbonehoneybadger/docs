extends Area2D
## Contra-style bullet. Travels in a straight line, damages the opposing side,
## despawns on walls or after its lifetime. Built from script so it needs no
## external scene.

const SPEED: float = 320.0
const LIFETIME: float = 1.3

var _dir: Vector2 = Vector2.RIGHT
var _from_player: bool = true
var _effect: String = "normal"
var _life: float = LIFETIME

@onready var sprite: Sprite2D = _ensure_sprite()

func setup(dir: Vector2, from_player: bool, effect: String = "normal") -> void:
	_dir = dir.normalized() if dir.length() > 0.0 else Vector2.RIGHT
	_from_player = from_player
	_effect = effect

func _ready() -> void:
	add_to_group("projectiles")
	_ensure_collision()
	sprite.texture = _build_texture()
	rotation = _dir.angle()
	collision_layer = 0
	collision_mask = 0
	set_collision_mask_value(1, true)  # world
	if _from_player:
		set_collision_mask_value(3, true)  # enemy bodies
	else:
		set_collision_mask_value(2, true)  # player body
	monitoring = true
	body_entered.connect(_on_body_entered)

func _physics_process(delta: float) -> void:
	global_position += _dir * SPEED * delta
	_life -= delta
	if _life <= 0.0:
		queue_free()

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
		shape.radius = 4.0
		cs.shape = shape
		add_child(cs)

func _build_texture() -> Texture2D:
	var core := Color("#FFE38A") if _from_player else Color("#FF6464")
	var glow := Color("#FFB020") if _from_player else Color("#C03030")
	return PixelArt.make_texture(10, 6, [
		[0, 1, 10, 4, glow],
		[2, 1, 6, 4, core],
		[3, 0, 4, 6, core],
	])

func _on_body_entered(body: Node) -> void:
	if _from_player:
		if body.is_in_group("enemies"):
			if body.has_method("hit"):
				body.hit(_effect, global_position)
			queue_free()
			return
	else:
		if body.is_in_group("player"):
			if body.has_method("take_damage"):
				body.take_damage(1, global_position)
			queue_free()
			return
	# Anything else solid (world geometry) stops the bullet.
	if not body.is_in_group("player") and not body.is_in_group("enemies"):
		queue_free()
