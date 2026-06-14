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

# --- Contra: shooting ---
const PROJECTILE_SCRIPT := "res://scripts/objects/Projectile.gd"
const PROJECTILE_SCENE := "res://scenes/objects/Projectile.tscn"
const SHOOT_CD_SINGLE: float = 0.26
const SHOOT_CD_SPREAD: float = 0.36
const SHOOT_CD_RAPID: float = 0.11
const WEAPON_MAX: int = 2  # 0 single, 1 spread, 2 rapid

# --- Battletoads: combo / smash ---
const COMBO_WINDOW: float = 0.55
const SMASH_KNOCKBACK: float = 360.0

# --- Mario 3: P-meter run / flight ---
const RUN_FILL_TIME: float = 1.1
const RUN_GROUND_DRAIN: float = 0.6
const FLY_DRAIN: float = 1.6      # seconds of flight from a full meter
const FLY_RISE: float = -90.0     # hover/climb velocity while flying

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

# Contra / Battletoads / Mario 3 state
var weapon_level: int = 0
var run_meter: float = 0.0
var _shoot_cd: float = 0.0
var _flying: bool = false
var _combo_count: int = 0
var _combo_timer: float = 0.0
var _is_smash: bool = false

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

	# Gravity, with Mario-3 style flight when the P-meter is charged.
	if not is_on_floor():
		if _flying and Input.is_action_pressed("jump") and run_meter > 0.0:
			run_meter = maxf(0.0, run_meter - delta / FLY_DRAIN)
			velocity.y = move_toward(velocity.y, FLY_RISE, 700.0 * delta)
			if run_meter <= 0.0:
				_flying = false
		else:
			_flying = false
			velocity.y = minf(velocity.y + GRAVITY * delta, MAX_FALL_SPEED)
		_coyote_timer -= delta
	else:
		_coyote_timer = COYOTE_TIME
		_flying = false

	var dir := Input.get_axis("move_left", "move_right")
	if dir != 0.0:
		velocity.x = dir * speed
		_facing = signi(int(sign(dir)))
		sprite.flip_h = _facing < 0
	else:
		velocity.x = move_toward(velocity.x, 0.0, speed * 0.25)

	if Input.is_action_just_pressed("jump"):
		_jump_buffer_timer = JUMP_BUFFER_TIME
		if not is_on_floor() and run_meter >= 1.0:
			_flying = true
	else:
		_jump_buffer_timer -= delta

	if _jump_buffer_timer > 0.0 and _coyote_timer > 0.0:
		_do_jump()

	if Input.is_action_just_pressed("attack"):
		_start_attack()
	if Input.is_action_just_pressed("special"):
		_perform_special()

	_shoot_cd = maxf(0.0, _shoot_cd - delta)
	if Input.is_action_pressed("shoot"):
		_try_shoot()

	if _combo_timer > 0.0:
		_combo_timer -= delta

	if _attack_timer > 0.0:
		_attack_timer -= delta
		if _attack_timer <= 0.0:
			attack_area.monitoring = false
			_is_smash = false
			attack_area.scale = Vector2(_facing, 1.0)

	if _invincible_timer > 0.0:
		_invincible_timer -= delta
		sprite.visible = int(_invincible_timer * 20.0) % 2 == 0
		if _invincible_timer <= 0.0:
			sprite.visible = true

	move_and_slide()
	_handle_contacts()
	_update_run_meter(delta)

	if global_position.y > DEATH_Y:
		_die()

# --- Mario 3: P-meter charges while sprinting on the ground ---
func _update_run_meter(delta: float) -> void:
	if is_on_floor():
		if absf(velocity.x) >= speed * 0.9:
			run_meter = minf(1.0, run_meter + delta / RUN_FILL_TIME)
		else:
			run_meter = maxf(0.0, run_meter - delta / RUN_GROUND_DRAIN)

func get_run_meter() -> float:
	return run_meter

# --- Contra: shooting ---
func _try_shoot() -> void:
	if _shoot_cd > 0.0:
		return
	var aim := _compute_aim()
	match weapon_level:
		1:  # spread of three
			_spawn_bullet(aim.rotated(-0.26))
			_spawn_bullet(aim)
			_spawn_bullet(aim.rotated(0.26))
			_shoot_cd = SHOOT_CD_SPREAD
		2:  # rapid single
			_spawn_bullet(aim)
			_shoot_cd = SHOOT_CD_RAPID
		_:  # default single
			_spawn_bullet(aim)
			_shoot_cd = SHOOT_CD_SINGLE
	AudioManager.play_sfx("attack")

func _compute_aim() -> Vector2:
	var horiz := Input.get_axis("move_left", "move_right")
	var up := Input.is_action_pressed("aim_up")
	var down := Input.is_action_pressed("aim_down") and not is_on_floor()
	var hx := signf(horiz)
	if up and hx != 0.0:
		return Vector2(hx, -1).normalized()
	if down and hx != 0.0:
		return Vector2(hx, 1).normalized()
	if up:
		return Vector2(0, -1)
	if down:
		return Vector2(0, 1)
	if hx != 0.0:
		return Vector2(hx, 0)
	return Vector2(_facing, 0)

func _spawn_bullet(dir: Vector2) -> void:
	var bullet: Area2D
	if ResourceLoader.exists(PROJECTILE_SCENE):
		bullet = (load(PROJECTILE_SCENE) as PackedScene).instantiate()
	else:
		bullet = Area2D.new()
		bullet.set_script(load(PROJECTILE_SCRIPT))
	if bullet.has_method("setup"):
		# Bullets deal instant "normal" damage (Contra-style); poison stays on melee.
		bullet.setup(dir, true, "normal")
	get_parent().add_child(bullet)
	bullet.global_position = global_position + dir.normalized() * 14.0 + Vector2(0, -6)

# --- Mario 3: power-up and Contra weapon upgrade ---
func power_up() -> void:
	max_health += 1
	current_health = max_health
	emit_signal("health_changed", current_health, max_health)
	AudioManager.play_sfx("coin")

func upgrade_weapon() -> void:
	weapon_level = mini(WEAPON_MAX, weapon_level + 1)
	AudioManager.play_sfx("coin")

func _do_jump() -> void:
	velocity.y = -jump_force
	_coyote_timer = 0.0
	_jump_buffer_timer = 0.0
	AudioManager.play_sfx("jump")

## Battletoads-style combo: every 3rd hit in quick succession is a big "smash"
## with a wider hitbox, heavier knockback and a camera shake.
func _start_attack() -> void:
	if _combo_timer > 0.0:
		_combo_count += 1
	else:
		_combo_count = 1
	_combo_timer = COMBO_WINDOW
	_is_smash = (_combo_count % 3 == 0)
	_attack_timer = ATTACK_TIME
	attack_area.monitoring = true
	if _is_smash:
		attack_area.scale = Vector2(_facing * 1.7, 1.7)
		AudioManager.play_sfx("stomp")
		_camera_shake(5.0)
	else:
		attack_area.scale = Vector2(_facing, 1.0)
		AudioManager.play_sfx("attack")
	_perform_attack()

func _camera_shake(amount: float) -> void:
	var cam := get_node_or_null("Camera2D")
	if cam == null:
		return
	var tween := create_tween()
	tween.tween_property(cam, "offset", Vector2(amount, -amount), 0.04)
	tween.tween_property(cam, "offset", Vector2(-amount * 0.6, amount * 0.4), 0.04)
	tween.tween_property(cam, "offset", Vector2.ZERO, 0.06)

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
		if _is_smash and node.has_method("knockback"):
			node.knockback(global_position, SMASH_KNOCKBACK)
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
