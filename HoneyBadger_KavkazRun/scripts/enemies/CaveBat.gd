extends BaseEnemy
## Cave Bat: flies a horizontal sine path, swoops toward the player on approach.
## HP 1.

const SWOOP_RANGE: float = 140.0
const SWOOP_SPEED: float = 95.0
const WAVE_AMPLITUDE: float = 22.0
const WAVE_FREQ: float = 3.0

func _configure() -> void:
	hp = 1
	flying = true
	move_speed = 60.0
	edge_ray.enabled = false
	wall_ray.enabled = false

func _build_texture() -> Texture2D:
	return PixelArt.make_texture(24, 24, PixelArt.cave_bat_rects())

func _move(delta: float) -> void:
	var player := _nearest_player()
	if player and global_position.distance_to(player.global_position) < SWOOP_RANGE:
		var to_player := (player.global_position - global_position).normalized()
		velocity = to_player * SWOOP_SPEED
	else:
		velocity.x = _direction * move_speed
		velocity.y = sin(_time * WAVE_FREQ) * WAVE_AMPLITUDE
		if absf(global_position.x - _origin.x) > 150.0:
			_turn()
	sprite.flip_h = velocity.x > 0

func _nearest_player() -> Node2D:
	var players := get_tree().get_nodes_in_group("player")
	if players.is_empty():
		return null
	return players[0]
