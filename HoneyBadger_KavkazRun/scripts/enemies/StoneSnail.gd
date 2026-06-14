extends BaseEnemy
## Stone Snail: slow ground patrol. HP 2. First hit retreats into its shell
## (invincible 2s), second hit kills it.

const SHELL_TIME: float = 2.0

var _in_shell: bool = false

func _configure() -> void:
	hp = 2
	move_speed = 40.0

func _build_texture() -> Texture2D:
	return PixelArt.make_texture(24, 24, PixelArt.stone_snail_rects())

func hit(effect: String, from_pos: Vector2) -> void:
	if not _alive or _in_shell:
		return
	knockback(from_pos, 140.0)
	if effect == "poison":
		_apply_poison()
		return
	hp -= 1
	if hp <= 0:
		die(effect)
	else:
		_enter_shell()

func _enter_shell() -> void:
	_in_shell = true
	sprite.modulate = Color(0.7, 0.7, 0.8)
	var t := get_tree().create_timer(SHELL_TIME)
	t.timeout.connect(func():
		_in_shell = false
		if _alive:
			sprite.modulate = Color(1, 1, 1)
	)
