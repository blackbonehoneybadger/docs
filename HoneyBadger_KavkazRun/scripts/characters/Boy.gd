extends BaseCharacter
## Tank. Heavy punch plus a ground-pound special that knocks back / kills every
## enemy within SPECIAL_RADIUS and can break stone blocks.

func _ready() -> void:
	character_id = "boy"
	super._ready()

func _build_texture() -> Texture2D:
	return PixelArt.make_texture(32, 48, PixelArt.boy_rects())

func get_attack_effect() -> String:
	return "normal"

func _perform_special() -> void:
	if not is_on_floor():
		# Slam downward first.
		velocity.y = MAX_FALL_SPEED
		return
	AudioManager.play_sfx("attack")
	_ground_pound()

func _ground_pound() -> void:
	for enemy in get_tree().get_nodes_in_group("enemies"):
		if enemy is Node2D and global_position.distance_to(enemy.global_position) <= SPECIAL_RADIUS:
			if enemy.has_method("knockback"):
				enemy.knockback(global_position, 320.0)
			if enemy.has_method("hit"):
				enemy.hit("normal", global_position)
	for block in get_tree().get_nodes_in_group("breakable"):
		if block is Node2D and global_position.distance_to(block.global_position) <= SPECIAL_RADIUS:
			if block.has_method("break_block"):
				block.break_block()
