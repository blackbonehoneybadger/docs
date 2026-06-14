extends Node
## Loads character definitions from JSON with a built-in fallback.
## Autoloaded as "CharacterConfig".

const CONFIG_PATH: String = "res://assets/characters/shared/characters_config.json"

var _data: Dictionary = {}

func _ready() -> void:
	_load()

func _load() -> void:
	if FileAccess.file_exists(CONFIG_PATH):
		var file := FileAccess.open(CONFIG_PATH, FileAccess.READ)
		if file != null:
			var text := file.get_as_text()
			file.close()
			var parsed: Variant = JSON.parse_string(text)
			if parsed is Dictionary and parsed.has("characters"):
				_data = parsed
				return
	push_warning("CharacterConfig: using built-in fallback data.")
	_data = _fallback_data()

func get_all_ids() -> Array:
	var ids: Array = []
	for c in _data.get("characters", []):
		ids.append(c.get("id", ""))
	return ids

func get_character(id: String) -> Dictionary:
	for c in _data.get("characters", []):
		if c.get("id", "") == id:
			return c
	return {}

func get_stat(id: String, stat: String, default_value: Variant = 0) -> Variant:
	var c := get_character(id)
	return c.get(stat, default_value)

func _fallback_data() -> Dictionary:
	return {
		"characters": [
			{
				"id": "honey_badger",
				"name": "HONEY BADGER",
				"role": "Герой",
				"speed": 180,
				"jump_force": 360,
				"health": 3,
				"attack_type": "poison_katana",
				"description": "Бесстрашный медоед с ядовитой катаной."
			},
			{
				"id": "boy",
				"name": "BOY",
				"role": "Танк",
				"speed": 130,
				"jump_force": 280,
				"health": 5,
				"attack_type": "heavy_punch",
				"description": "Силач. Ломает камень, отбрасывает врагов."
			},
			{
				"id": "mr_kroo",
				"name": "MR. KROO",
				"role": "Ловкач",
				"speed": 220,
				"jump_force": 430,
				"health": 2,
				"attack_type": "scissors",
				"description": "Быстрый и прыгучий. Враги в конфетти."
			}
		]
	}
