extends Control
## Three character cards with stat bars; pick one, then В БОЙ.

const STAT_MAX := {"speed": 240.0, "jump_force": 450.0, "health": 6.0}

var _selected_id: String = ""
var _cards: Dictionary = {}

func _ready() -> void:
	set_anchors_preset(Control.PRESET_FULL_RECT)
	_selected_id = GameManager.selected_character
	if get_child_count() == 0:
		_build()

func _build() -> void:
	var bg := ColorRect.new()
	bg.set_anchors_preset(Control.PRESET_FULL_RECT)
	bg.color = Color(0.05, 0.12, 0.08)
	add_child(bg)

	var header := Label.new()
	header.text = "ВЫБОР ПЕРСОНАЖА"
	header.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	header.add_theme_font_size_override("font_size", 20)
	header.add_theme_color_override("font_color", Color(1, 0.85, 0.2))
	header.size = Vector2(480, 24)
	header.position = Vector2(0, 8)
	add_child(header)

	var ids := CharacterConfig.get_all_ids()
	var card_w := 148.0
	var gap := 8.0
	var total := ids.size() * card_w + (ids.size() - 1) * gap
	var start_x := (480.0 - total) * 0.5
	for i in ids.size():
		var id: String = ids[i]
		var card := _build_card(id)
		card.position = Vector2(start_x + i * (card_w + gap), 40)
		add_child(card)
		_cards[id] = card

	var fight := Button.new()
	fight.text = "В БОЙ"
	fight.add_theme_font_size_override("font_size", 16)
	fight.size = Vector2(120, 28)
	fight.position = Vector2(250, 234)
	fight.pressed.connect(_on_fight)
	add_child(fight)

	var back := Button.new()
	back.text = "НАЗАД"
	back.add_theme_font_size_override("font_size", 16)
	back.size = Vector2(100, 28)
	back.position = Vector2(120, 234)
	back.pressed.connect(_on_back)
	add_child(back)

	_refresh_highlight()

func _build_card(id: String) -> Panel:
	var data := CharacterConfig.get_character(id)
	var card := Panel.new()
	card.name = "Card_" + id
	card.custom_minimum_size = Vector2(148, 188)
	card.size = Vector2(148, 188)

	var v := VBoxContainer.new()
	v.position = Vector2(8, 6)
	v.size = Vector2(132, 176)
	v.add_theme_constant_override("separation", 3)
	card.add_child(v)

	var name_label := Label.new()
	name_label.text = str(data.get("name", id))
	name_label.add_theme_font_size_override("font_size", 14)
	name_label.add_theme_color_override("font_color", Color(1, 0.9, 0.4))
	v.add_child(name_label)

	var role := Label.new()
	role.text = str(data.get("role", ""))
	role.add_theme_font_size_override("font_size", 11)
	role.add_theme_color_override("font_color", Color(0.8, 0.85, 0.8))
	v.add_child(role)

	var portrait := TextureRect.new()
	portrait.texture = _portrait_for(id)
	portrait.custom_minimum_size = Vector2(48, 72)
	portrait.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	v.add_child(portrait)

	v.add_child(_stat_row("СКОР", float(data.get("speed", 0)), STAT_MAX["speed"]))
	v.add_child(_stat_row("ПРЫЖ", float(data.get("jump_force", 0)), STAT_MAX["jump_force"]))
	v.add_child(_stat_row("HP", float(data.get("health", 0)), STAT_MAX["health"]))

	var pick := Button.new()
	pick.text = "ВЫБРАТЬ"
	pick.add_theme_font_size_override("font_size", 12)
	pick.pressed.connect(_on_pick.bind(id))
	v.add_child(pick)

	return card

func _stat_row(label: String, value: float, max_value: float) -> HBoxContainer:
	var row := HBoxContainer.new()
	var l := Label.new()
	l.text = label
	l.custom_minimum_size = Vector2(36, 0)
	l.add_theme_font_size_override("font_size", 10)
	row.add_child(l)
	var blocks := int(round(clampf(value / max_value, 0.0, 1.0) * 8.0))
	var bar := Label.new()
	bar.text = "█".repeat(blocks) + "░".repeat(8 - blocks)
	bar.add_theme_font_size_override("font_size", 10)
	bar.add_theme_color_override("font_color", Color(0.4, 0.9, 0.5))
	row.add_child(bar)
	return row

func _portrait_for(id: String) -> Texture2D:
	match id:
		"boy":
			return PixelArt.make_texture(32, 48, PixelArt.boy_rects())
		"mr_kroo":
			return PixelArt.make_texture(32, 48, PixelArt.mr_kroo_rects())
		_:
			return PixelArt.make_texture(32, 48, PixelArt.honey_badger_rects())

func _on_pick(id: String) -> void:
	_selected_id = id
	GameManager.selected_character = id
	AudioManager.play_sfx("coin")
	_refresh_highlight()

func _refresh_highlight() -> void:
	for id in _cards.keys():
		var card: Panel = _cards[id]
		var sb := StyleBoxFlat.new()
		sb.bg_color = Color(0.1, 0.18, 0.12)
		if id == _selected_id:
			sb.border_color = Color(1, 0.84, 0.0)
			sb.set_border_width_all(3)
		else:
			sb.border_color = Color(0.3, 0.35, 0.3)
			sb.set_border_width_all(1)
		card.add_theme_stylebox_override("panel", sb)

func _on_fight() -> void:
	GameManager.selected_character = _selected_id
	GameManager.start_new_game()
	get_tree().change_scene_to_file(GameManager.LEVEL_SCENE_PATH)

func _on_back() -> void:
	get_tree().change_scene_to_file(GameManager.MAIN_MENU_PATH)
