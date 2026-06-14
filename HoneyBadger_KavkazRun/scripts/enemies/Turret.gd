extends BaseEnemy
## Contra-style gun turret. Stationary, HP 2, fires aimed bullets at the player
## when in range. Vulnerable to melee, stomp and the player's own bullets.

const FIRE_INTERVAL: float = 1.5
const RANGE: float = 280.0
const PROJECTILE_SCRIPT := "res://scripts/objects/Projectile.gd"
const PROJECTILE_SCENE := "res://scenes/objects/Projectile.tscn"

var _fire_t: float = 0.8

func _configure() -> void:
	hp = 2
	move_speed = 0.0
	flying = false
	edge_ray.enabled = false
	wall_ray.enabled = false

func _build_texture() -> Texture2D:
	var base := Color("#5A6066")
	var barrel := Color("#2E3238")
	var eye := Color("#FF5050")
	return PixelArt.make_texture(24, 24, [
		[3, 12, 18, 10, base],     # housing
		[7, 6, 10, 8, base],       # turret head
		[14, 8, 9, 4, barrel],     # barrel
		[9, 8, 3, 3, eye],
	])

func _move(delta: float) -> void:
	if not is_on_floor():
		velocity.y += GRAVITY * delta
	else:
		velocity.y = 0.0
	velocity.x = 0.0
	_fire_t -= delta
	var player := _nearest_player()
	if player == null:
		return
	if global_position.distance_to(player.global_position) <= RANGE and _fire_t <= 0.0:
		_fire_t = FIRE_INTERVAL
		_fire_at(player.global_position)
		sprite.flip_h = player.global_position.x > global_position.x

func _fire_at(target: Vector2) -> void:
	var dir := (target - global_position).normalized()
	var bullet: Area2D
	if ResourceLoader.exists(PROJECTILE_SCENE):
		bullet = (load(PROJECTILE_SCENE) as PackedScene).instantiate()
	else:
		bullet = Area2D.new()
		bullet.set_script(load(PROJECTILE_SCRIPT))
	if bullet.has_method("setup"):
		bullet.setup(dir, false, "normal")
	get_parent().add_child(bullet)
	bullet.global_position = global_position + dir * 14.0

func _nearest_player() -> Node2D:
	var nearest: Node2D = null
	var best := INF
	for p in get_tree().get_nodes_in_group("player"):
		if p is Node2D:
			var d := global_position.distance_to(p.global_position)
			if d < best:
				best = d
				nearest = p
	return nearest
