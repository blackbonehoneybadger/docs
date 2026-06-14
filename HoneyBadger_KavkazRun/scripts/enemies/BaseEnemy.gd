class_name BaseEnemy
extends CharacterBody2D
## Shared enemy logic: patrol with edge/wall detection, knockback, poison death,
## stomp death and cartoon death effects. Subclasses set stats and override
## `_move()`. Builds its own children so the .tscn only needs a root.

const GRAVITY: float = 980.0
const SCORE_ON_DEATH: int = 200
const POISON_TIME: float = 1.5
const KNOCKBACK_DECAY: float = 600.0

const L_WORLD := 1
const L_ENEMY := 3
const L_ENEMY_HITBOX := 4

@export var hp: int = 1
@export var move_speed: float = 60.0
@export var flying: bool = false

var _alive: bool = true
var _poisoned: bool = false
var _direction: int = -1
var _knockback: Vector2 = Vector2.ZERO
var _time: float = 0.0
var _origin: Vector2

@onready var sprite: Sprite2D = _ensure_sprite()
@onready var collision: CollisionShape2D = _ensure_collision()
@onready var hitbox: Area2D = _ensure_hitbox()
@onready var edge_ray: RayCast2D = _ensure_ray("EdgeRay", Vector2(12 * _direction, 28))
@onready var wall_ray: RayCast2D = _ensure_ray("WallRay", Vector2(16 * _direction, 0))

func _ready() -> void:
	add_to_group("enemies")
	_origin = global_position
	sprite.texture = _build_texture()
	_setup_collision_layers()
	_configure()

func _setup_collision_layers() -> void:
	# Body collides with the world only.
	collision_layer = 0
	collision_mask = 0
	set_collision_layer_value(L_ENEMY, true)
	set_collision_mask_value(L_WORLD, true)
	# Damaging hitbox is detectable by the player's hurt / stomp boxes.
	hitbox.collision_layer = 0
	hitbox.collision_mask = 0
	hitbox.set_collision_layer_value(L_ENEMY_HITBOX, true)
	hitbox.monitorable = true
	hitbox.monitoring = false

## Subclass hook for per-type stats.
func _configure() -> void:
	pass

func is_alive() -> bool:
	return _alive

# ------------------------------ node building --------------------------------

func _ensure_sprite() -> Sprite2D:
	var n := get_node_or_null("Sprite") as Sprite2D
	if n == null:
		n = Sprite2D.new()
		n.name = "Sprite"
		add_child(n)
	return n

func _ensure_collision() -> CollisionShape2D:
	var n := get_node_or_null("Collision") as CollisionShape2D
	if n == null:
		n = CollisionShape2D.new()
		n.name = "Collision"
		var shape := RectangleShape2D.new()
		shape.size = Vector2(20, 20)
		n.shape = shape
		add_child(n)
	return n

func _ensure_hitbox() -> Area2D:
	var n := get_node_or_null("Hitbox") as Area2D
	if n == null:
		n = Area2D.new()
		n.name = "Hitbox"
		var cs := CollisionShape2D.new()
		var shape := RectangleShape2D.new()
		shape.size = Vector2(22, 22)
		cs.shape = shape
		n.add_child(cs)
		add_child(n)
	return n

func _ensure_ray(ray_name: String, target: Vector2) -> RayCast2D:
	var n := get_node_or_null(ray_name) as RayCast2D
	if n == null:
		n = RayCast2D.new()
		n.name = ray_name
		n.target_position = target
		n.enabled = true
		add_child(n)
	return n

func _build_texture() -> Texture2D:
	return PixelArt.make_texture(24, 24, PixelArt.stone_snail_rects())

# -------------------------------- main loop ----------------------------------

func _physics_process(delta: float) -> void:
	_time += delta
	if not _alive:
		velocity = velocity.move_toward(Vector2.ZERO, KNOCKBACK_DECAY * delta)
		move_and_slide()
		return

	if _knockback.length() > 1.0:
		velocity = _knockback
		_knockback = _knockback.move_toward(Vector2.ZERO, KNOCKBACK_DECAY * delta)
		move_and_slide()
		return

	_move(delta)
	move_and_slide()

## Default ground patrol. Flying enemies override.
func _move(delta: float) -> void:
	if not is_on_floor():
		velocity.y += GRAVITY * delta
	else:
		velocity.y = 0.0
	velocity.x = _direction * move_speed
	sprite.flip_h = _direction > 0
	_update_ray_directions()
	# Turn at a ledge (no ground ahead) or against a wall.
	if (edge_ray.enabled and not edge_ray.is_colliding()) or wall_ray.is_colliding():
		_turn()

func _update_ray_directions() -> void:
	edge_ray.target_position = Vector2(12 * _direction, 28)
	wall_ray.target_position = Vector2(16 * _direction, 0)
	edge_ray.force_raycast_update()
	wall_ray.force_raycast_update()

func _turn() -> void:
	_direction = -_direction

# ------------------------------ damage / death -------------------------------

func hit(effect: String, from_pos: Vector2) -> void:
	if not _alive:
		return
	knockback(from_pos, 180.0)
	if effect == "poison":
		_apply_poison()
		return
	hp -= 1
	if hp <= 0:
		die(effect)

func stomp() -> void:
	if _alive:
		die("stomp")

func knockback(from_pos: Vector2, force: float) -> void:
	var dir := signf(global_position.x - from_pos.x)
	if dir == 0.0:
		dir = 1.0
	_knockback = Vector2(dir * force, -120.0)

func _apply_poison() -> void:
	if _poisoned:
		return
	_poisoned = true
	sprite.modulate = Color(0.5, 1.4, 0.6)
	var t := get_tree().create_timer(POISON_TIME)
	t.timeout.connect(func(): if _alive: die("poison"))

func die(effect: String) -> void:
	if not _alive:
		return
	_alive = false
	hitbox.set_deferred("monitoring", false)
	hitbox.set_deferred("monitorable", false)
	collision.set_deferred("disabled", true)
	GameManager.add_score(SCORE_ON_DEATH)
	AudioManager.play_sfx("enemy_die")
	_spawn_death_effect(effect)
	var t := get_tree().create_timer(0.45)
	t.timeout.connect(queue_free)

## Cartoon-only effects: green smoke (poison), colored confetti (confetti),
## or a simple puff. No realistic gore.
func _spawn_death_effect(effect: String) -> void:
	var particles := CPUParticles2D.new()
	particles.emitting = true
	particles.one_shot = true
	particles.explosiveness = 0.9
	particles.lifetime = 0.5
	particles.amount = 16
	particles.direction = Vector2(0, -1)
	particles.spread = 180.0
	particles.gravity = Vector2(0, 120)
	particles.initial_velocity_min = 40.0
	particles.initial_velocity_max = 90.0
	particles.scale_amount_min = 2.0
	particles.scale_amount_max = 4.0
	match effect:
		"poison":
			particles.color = Color(0.4, 1.0, 0.5, 0.9)
		"confetti":
			particles.color = Color(1, 1, 1, 1)
			var ramp := Gradient.new()
			ramp.offsets = PackedFloat32Array([0.0, 0.34, 0.67, 1.0])
			ramp.colors = PackedColorArray([
				Color(1, 0.3, 0.3), Color(0.3, 0.6, 1), Color(1, 0.9, 0.2), Color(0.5, 1, 0.5)
			])
			particles.color_ramp = ramp
		_:
			particles.color = Color(0.9, 0.9, 0.95, 0.9)
	get_parent().add_child(particles)
	particles.global_position = global_position
	sprite.visible = false
