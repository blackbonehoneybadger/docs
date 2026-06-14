extends Control
## Game over screen. Shows the final score with СНОВА / МЕНЮ.

func _ready() -> void:
	set_anchors_preset(Control.PRESET_FULL_RECT)
	if get_child_count() == 0:
		_build()
	AudioManager.stop_music()

func _build() -> void:
	var bg := ColorRect.new()
	bg.set_anchors_preset(Control.PRESET_FULL_RECT)
	bg.color = Color(0.12, 0.03, 0.03)
	add_child(bg)

	var title := Label.new()
	title.text = "GAME OVER"
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	title.add_theme_font_size_override("font_size", 34)
	title.add_theme_color_override("font_color", Color(1, 0.25, 0.25))
	title.size = Vector2(480, 40)
	title.position = Vector2(0, 64)
	add_child(title)

	var score := Label.new()
	score.text = "Счёт: %d\nРекорд: %d" % [GameManager.score, GameManager.high_score]
	score.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	score.add_theme_font_size_override("font_size", 16)
	score.add_theme_color_override("font_color", Color(1, 1, 1))
	score.size = Vector2(480, 50)
	score.position = Vector2(0, 120)
	add_child(score)

	var row := HBoxContainer.new()
	row.position = Vector2(140, 190)
	row.add_theme_constant_override("separation", 16)
	add_child(row)

	var again := Button.new()
	again.text = "СНОВА"
	again.custom_minimum_size = Vector2(90, 30)
	again.pressed.connect(_on_again)
	row.add_child(again)

	var menu := Button.new()
	menu.text = "МЕНЮ"
	menu.custom_minimum_size = Vector2(90, 30)
	menu.pressed.connect(_on_menu)
	row.add_child(menu)

func _on_again() -> void:
	GameManager.start_new_game()
	get_tree().change_scene_to_file(GameManager.LEVEL_SCENE_PATH)

func _on_menu() -> void:
	get_tree().change_scene_to_file(GameManager.MAIN_MENU_PATH)
