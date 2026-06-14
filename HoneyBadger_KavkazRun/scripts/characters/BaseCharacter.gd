class_name BaseCharacter
extends CharacterBody2D
## Shared platformer character. Subclasses set `character_id` and override
## `_perform_attack()` / `_perform_special()`. Builds its own child nodes in
## `_ready()` so the .tscn only needs a root CharacterBody2D with this script.

signal health_changed(current: int, max_health: int)
signal player_died

const GRAVITY: float = 980.0
const MAX_FALL_SPEED: float = 900.0
const COYOTE_TIME: float = 0.12
const JUMP_BUFFER_TIME: float = 0.10
const INVINCIBLE_TIME: float = 1.5
const STOMP_BOUNCE: float = -260.0
const DEATH_Y: float = 900.0
const ATTACK_TIME: float = 0.18
const SPECIAL_RADIUS: float = 96.0

# Collision layer bits (1-based to match set_collision_*_value):
const L_WORLD := 1
const L_PLAYER := 2
const L_ENEMY := 3
const L_ENEMY_HITBOX := 4
const L_PICKUP := 5

@export var character_id: String = "honey_badger"

var speed: float = 180.0
var jump_force: float = 360.0
var max_health: int = 3
var current_health: int = 3

var _coyote_timer: float = 0.0
var _jump_buffer_timer: float = 0.0
var _invincible_timer: float = 0.0
var _attack_timer: float = 0.0
var _is_dead: bool = false
var _facing: int = 1
var _start_position: Vector2

@onready var sprite: Sprite2D = _ensure_sprite()
@onready var body_collision: CollisionShape2D = _ensure_body_collision()
@onready var attack_area: Area2D = _ensure_attack_area()
@onready var hurtbox: Area2D = _ensure_hurtbox()
@onready var stomp_box: Area2D = _ensure_stomp_box()

func _ready() -> void:
	add_to_group("player")
	_load_stats()
	current_health = max_health
	_start_position = global_position
	_apply_sprite_texture()
	_setup_collision_layers()
	attack_area.monitoring = false
	emit_signal("health_changed", current_health, max_health)

func _setup_collision_layers() -> void:
	# Body collides only with the world, so it passes through enemies.
	collision_layer = 0
	collision_mask = 0
	set_collision_layer_value(L_PLAYER, true)
	set_collision_mask_value(L_WORLD, true)
	# Hurt / stomp boxes look for enemy hitboxes.
	for box in [hurtbox, stomp_box]:
		box.collision_layer = 0
		box.collision_mask = 0
		box.set_collision_mask_value(L_ENEMY_HITBOX, true)
		box.monitoring = true
		box.monitorable = false
	# Attack area looks for enemy bodies.
	attack_area.collision_layer = 0
	attack_area.collision_mask = 0
	attack_area.set_collision_mask_value(L_ENEMY, true)
	attack_area.monitorable = false

func _load_stats() -> void:
	speed = float(CharacterConfig.get_stat(character_id, "speed", speed))
	jump_force = float(CharacterConfig.get_stat(character_id, "jump_force", jump_force))
	max_health = int(CharacterConfig.get_stat(character_id, "health", max_health))

# ----- node construction (defensive: reuse existing children if present) -----

func _ensure_sprite() -> Sprite2D:
	var n := get_node_or_null("Sprite") as Sprite2D
	if n == null:
		n = Sprite2D.new()
		n.name = "Sprite"
		add_child(n)
	return n

func _ensure_body_collision() -> CollisionShape2D:
	var n := get_node_or_null("Collision") as CollisionShape2D
	if n == null:
		n = CollisionShape2D.new()
		n.name = "Collision"
		var shape := RectangleShape2D.new()
		shape.size = Vector2(22, 40)
		n.shape = shape
		n.position = Vector2(0, -4)
		add_child(n)
	return n

func _ensure_attack_area() -> Area2D:
	var n := get_node_or_null("AttackArea") as Area2D
	if n == null:
		n = Area2D.new()
		n.name = "AttackArea"
		var cs := CollisionShape2D.new()
		var shape := RectangleShape2D.new()
		shape.size = Vector2(34, 34)
		cs.shape = shape
		cs.position = Vector2(22, -4)
		n.add_child(cs)
		add_child(n)
	return n

func _ensure_hurtbox() -> Area2D:
	var n := get_node_or_null("Hurtbox") as Area2D
	if n == null:
		n = Area2D.new()
		n.name = "Hurtbox"
		var cs := CollisionShape2D.new()
		var shape := RectangleShape2D.new()
		shape.size = Vector2(20, 38)
		cs.shape = shape
		cs.position = Vector2(0, -4)
		n.add_child(cs)
		add_child(n)
	return n

func _ensure_stomp_box() -> Area2D:
	var n := get_node_or_null("StompBox") as Area2D
	if n == null:
		n = Area2D.new()
		n.name = "StompBox"
		var cs := CollisionShape2D.new()
		var shape := RectangleShape2D.new()
		shape.size = Vector2(18, 10)
		cs.shape = shape
		cs.position = Vector2(0, 16)
		n.add_child(cs)
		add_child(n)
	return n

func _apply_sprite_texture() -> void:
	sprite.texture = _build_texture()
	sprite.position = Vector2(0, -8)

## Override in subclasses for distinct looks.
func _build_texture() -> Texture2D:
	return PixelArt.make_texture(32, 48, PixelArt.honey_badger_rects())

# ----------------------------- main loop -------------------------------------

func _physics_process(delta: float) -> void:
	if _is_dead:
		return

	if not is_on_floor():
		velocity.y = minf(velocity.y + GRAVITY * delta, MAX_FALL_SPEED)
		_coyote_timer -= delta
	else:
		_coyote_timer = COYOTE_TIME

	var dir := Input.get_axis("move_left", "move_right")
	if dir != 0.0:
		velocity.x = dir * speed
		_facing = signi(int(sign(dir)))
		sprite.flip_h = _facing < 0
		attack_area.scale.x = _facing
	else:
		velocity.x = move_toward(velocity.x, 0.0, speed * 0.25)

	if Input.is_action_just_pressed("jump"):
		_jump_buffer_timer = JUMP_BUFFER_TIME
	else:
		_jump_buffer_timer -= delta

	if _jump_buffer_timer > 0.0 and _coyote_timer > 0.0:
		_do_jump()

	if Input.is_action_just_pressed("attack"):
		_start_attack()
	if Input.is_action_just_pressed("special"):
		_perform_special()

	if _attack_timer > 0.0:
		_attack_timer -= delta
		if _attack_timer <= 0.0:
			attack_area.monitoring = false

	if _invincible_timer > 0.0:
		_invincible_timer -= delta
		sprite.visible = int(_invincible_timer * 20.0) % 2 == 0
		if _invincible_timer <= 0.0:
			sprite.visible = true

	move_and_slide()
	_handle_contacts()

	if global_position.y > DEATH_Y:
		_die()

func _do_jump() -> void:
	velocity.y = -jump_force
	_coyote_timer = 0.0
	_jump_buffer_timer = 0.0
	AudioManager.play_sfx("jump")

func _start_attack() -> void:
	_attack_timer = ATTACK_TIME
	attack_area.monitoring = true
	AudioManager.play_sfx("attack")
	_perform_attack()

## Default attack: hit every enemy in the attack area with this character's effect.
func _perform_attack() -> void:
	for body in attack_area.get_overlapping_bodies():
		_hit_enemy(body)
	# A short deferred sweep so enemies that overlap this frame still register.
	await get_tree().create_timer(0.02).timeout
	if is_instance_valid(self):
		for body in attack_area.get_overlapping_bodies():
			_hit_enemy(body)

## Boy overrides; default special mirrors attack.
func _perform_special() -> void:
	_start_attack()

func _hit_enemy(node: Node) -> void:
	if node and node.is_in_group("enemies") and node.has_method("hit"):
		node.hit(get_attack_effect(), global_position)

## Subclasses override to pick poison / normal / confetti.
func get_attack_effect() -> String:
	return "normal"

## Resolve stomp vs. damage each frame via area overlaps (enemies don't block
## movement; their damaging child is an Area2D named "Hitbox").
func _handle_contacts() -> void:
	if _is_dead:
		return
	var stomped: Dictionary = {}
	if velocity.y > 0:
		for area in stomp_box.get_overlapping_areas():
			var stomp_target := area.get_parent()
			if stomp_target and stomp_target.is_in_group("enemies") and _enemy_alive(stomp_target):
				if stomp_target.has_method("stomp"):
					stomp_target.stomp()
				velocity.y = STOMP_BOUNCE
				_jump_buffer_timer = 0.0
				AudioManager.play_sfx("stomp")
				stomped[stomp_target] = true
	if _invincible_timer <= 0.0:
		for area in hurtbox.get_overlapping_areas():
			var hurt_source := area.get_parent()
			if hurt_source and hurt_source.is_in_group("enemies") and _enemy_alive(hurt_source) and not stomped.has(hurt_source):
				take_damage(1, hurt_source.global_position)
				break

func _enemy_alive(e: Node) -> bool:
	if e.has_method("is_alive"):
		return e.is_alive()
	return true

# ----------------------------- damage / death --------------------------------

func take_damage(amount: int, from_pos: Vector2) -> void:
	if _is_dead or _invincible_timer > 0.0:
		return
	current_health -= amount
	emit_signal("health_changed", current_health, max_health)
	if current_health <= 0:
		_die()
		return
	_invincible_timer = INVINCIBLE_TIME
	var knock := signf(global_position.x - from_pos.x)
	if knock == 0.0:
		knock = 1.0
	velocity.x = knock * 160.0
	velocity.y = -180.0
	AudioManager.play_sfx("player_hurt")

func _die() -> void:
	if _is_dead:
		return
	_is_dead = true
	AudioManager.play_sfx("player_die")
	emit_signal("player_died")

func reset_for_respawn(pos: Vector2) -> void:
	_is_dead = false
	global_position = pos
	velocity = Vector2.ZERO
	current_health = max_health
	_invincible_timer = INVINCIBLE_TIME
	sprite.visible = true
	emit_signal("health_changed", current_health, max_health)
