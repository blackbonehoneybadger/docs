extends Control
## Shown when the level-end flag is reached. ДАЛЕЕ / МЕНЮ.

func _ready() -> void:
	set_anchors_preset(Control.PRESET_FULL_RECT)
	if get_child_count() == 0:
		_build()

func _build() -> void:
	var bg := ColorRect.new()
	bg.set_anchors_preset(Control.PRESET_FULL_RECT)
	bg.color = Color(0.05, 0.14, 0.06)
	add_child(bg)

	var title := Label.new()
	title.text = "УРОВЕНЬ ПРОЙДЕН!"
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	title.add_theme_font_size_override("font_size", 26)
	title.add_theme_color_override("font_color", Color(1, 0.85, 0.2))
	title.size = Vector2(480, 36)
	title.position = Vector2(0, 60)
	add_child(title)

	var stats := Label.new()
	stats.text = "Счёт: %d\nМонеты: %d\nРекорд: %d" % [GameManager.score, GameManager.coins, GameManager.high_score]
	stats.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	stats.add_theme_font_size_override("font_size", 16)
	stats.add_theme_color_override("font_color", Color(1, 1, 1))
	stats.size = Vector2(480, 60)
	stats.position = Vector2(0, 110)
	add_child(stats)

	var row := HBoxContainer.new()
	row.position = Vector2(140, 196)
	row.add_theme_constant_override("separation", 16)
	add_child(row)

	var next := Button.new()
	next.text = "ДАЛЕЕ"
	next.custom_minimum_size = Vector2(90, 30)
	next.pressed.connect(_on_next)
	row.add_child(next)

	var menu := Button.new()
	menu.text = "МЕНЮ"
	menu.custom_minimum_size = Vector2(90, 30)
	menu.pressed.connect(_on_menu)
	row.add_child(menu)

func _on_next() -> void:
	# Only one level in World 1 for now — replay it with carried-over score.
	get_tree().change_scene_to_file(GameManager.LEVEL_SCENE_PATH)

func _on_menu() -> void:
	get_tree().change_scene_to_file(GameManager.MAIN_MENU_PATH)
