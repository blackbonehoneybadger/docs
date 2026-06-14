extends BaseEnemy
## Forest Spirit: floats on a sine path, chases the player within 200px. HP 1.

const CHASE_RANGE: float = 200.0
const CHASE_SPEED: float = 70.0
const FLOAT_AMPLITUDE: float = 28.0
const FLOAT_FREQ: float = 2.0

func _configure() -> void:
	hp = 1
	flying = true
	move_speed = 50.0
	edge_ray.enabled = false
	wall_ray.enabled = false

func _build_texture() -> Texture2D:
	return PixelArt.make_texture(24, 24, PixelArt.forest_spirit_rects())

func _move(delta: float) -> void:
	var player := _nearest_player()
	if player and global_position.distance_to(player.global_position) < CHASE_RANGE:
		var to_player := (player.global_position - global_position).normalized()
		velocity = to_player * CHASE_SPEED
	else:
		velocity.x = _direction * move_speed
		velocity.y = cos(_time * FLOAT_FREQ) * FLOAT_AMPLITUDE
		if absf(global_position.x - _origin.x) > 120.0:
			_turn()
	sprite.flip_h = velocity.x > 0

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
