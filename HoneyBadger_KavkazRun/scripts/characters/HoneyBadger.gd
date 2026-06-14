extends BaseCharacter
## Hero. Poison katana: enemies die in green smoke.

func _ready() -> void:
	character_id = "honey_badger"
	super._ready()

func _build_texture() -> Texture2D:
	return PixelArt.make_texture(32, 48, PixelArt.honey_badger_rects())

func get_attack_effect() -> String:
	return "poison"
