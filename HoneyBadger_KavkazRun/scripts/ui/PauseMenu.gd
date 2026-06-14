extends Control
## Pause overlay toggled with the "pause" action. Processes while the tree is
## paused so its buttons stay responsive.

var _panel: Control
var _open: bool = false

func _ready() -> void:
	set_anchors_preset(Control.PRESET_FULL_RECT)
	process_mode = Node.PROCESS_MODE_ALWAYS
	if get_child_count() == 0:
		_build()
	_set_open(false)

func _build() -> void:
	var dim := ColorRect.new()
	dim.set_anchors_preset(Control.PRESET_FULL_RECT)
	dim.color = Color(0, 0, 0, 0.6)
	add_child(dim)

	_panel = VBoxContainer.new()
	_panel.position = Vector2(170, 90)
	_panel.size = Vector2(140, 120)
	_panel.add_theme_constant_override("separation", 10)
	add_child(_panel)

	var title := Label.new()
	title.text = "ПАУЗА"
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	title.add_theme_font_size_override("font_size", 22)
	title.add_theme_color_override("font_color", Color(1, 0.85, 0.2))
	_panel.add_child(title)

	_add_button("ПРОДОЛЖИТЬ", _on_resume)
	_add_button("РЕСТАРТ", _on_restart)
	_add_button("ГЛАВНОЕ МЕНЮ", _on_menu)

func _add_button(text: String, handler: Callable) -> void:
	var b := Button.new()
	b.text = text
	b.custom_minimum_size = Vector2(140, 28)
	b.add_theme_font_size_override("font_size", 14)
	b.pressed.connect(handler)
	_panel.add_child(b)

func _process(_delta: float) -> void:
	# Polled (not _unhandled_input) so the on-screen pause button — which sets the
	# action via Input.action_press — also toggles the menu, alongside ESC.
	if Input.is_action_just_pressed("pause"):
		_set_open(not _open)

func _set_open(open: bool) -> void:
	_open = open
	visible = open
	get_tree().paused = open

func _on_resume() -> void:
	_set_open(false)

func _on_restart() -> void:
	_set_open(false)
	GameManager.start_new_game()
	get_tree().change_scene_to_file(GameManager.LEVEL_SCENE_PATH)

func _on_menu() -> void:
	_set_open(false)
	get_tree().change_scene_to_file(GameManager.MAIN_MENU_PATH)
