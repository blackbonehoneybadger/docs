extends BaseCharacter
## Agile. Scissors attack: enemies burst into colored confetti.

func _ready() -> void:
	character_id = "mr_kroo"
	super._ready()

func _build_texture() -> Texture2D:
	return PixelArt.make_texture(32, 48, PixelArt.mr_kroo_rects())

func get_attack_effect() -> String:
	return "confetti"
