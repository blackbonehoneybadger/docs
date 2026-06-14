extends Control
## Title screen with a pulsing logo and PLAY / CHARACTERS / EXIT.

const MENU_MUSIC := "res://assets/audio/music/main_menu.ogg"

var _title: Label
var _time: float = 0.0

func _ready() -> void:
	set_anchors_preset(Control.PRESET_FULL_RECT)
	if get_child_count() == 0:
		_build()
	else:
		_title = get_node_or_null("Title")
		_wire_existing()
	AudioManager.play_music(MENU_MUSIC, true)

func _process(delta: float) -> void:
	if _title == null:
		return
	_time += delta
	var s := 1.0 + 0.06 * sin(_time * 3.0)
	_title.scale = Vector2(s, s)

func _build() -> void:
	var bg := TextureRect.new()
	bg.set_anchors_preset(Control.PRESET_FULL_RECT)
	bg.texture = _gradient_bg()
	bg.stretch_mode = TextureRect.STRETCH_SCALE
	add_child(bg)

	_title = Label.new()
	_title.name = "Title"
	_title.text = "HONEY BADGER"
	_title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_title.add_theme_font_size_override("font_size", 36)
	_title.add_theme_color_override("font_color", Color(1.0, 0.8, 0.0))
	_title.add_theme_color_override("font_outline_color", Color(0.1, 0.2, 0.1))
	_title.add_theme_constant_override("outline_size", 6)
	_title.size = Vector2(480, 50)
	_title.position = Vector2(0, 44)
	_title.pivot_offset = Vector2(240, 25)
	add_child(_title)

	var subtitle := Label.new()
	subtitle.text = "КАВКАЗСКИЙ ЗАБЕГ"
	subtitle.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	subtitle.add_theme_font_size_override("font_size", 18)
	subtitle.add_theme_color_override("font_color", Color(0.85, 0.95, 0.8))
	subtitle.size = Vector2(480, 24)
	subtitle.position = Vector2(0, 96)
	add_child(subtitle)

	var vbox := VBoxContainer.new()
	vbox.position = Vector2(160, 150)
	vbox.size = Vector2(160, 110)
	vbox.add_theme_constant_override("separation", 10)
	add_child(vbox)

	_add_button(vbox, "ИГРАТЬ", _on_play)
	_add_button(vbox, "ПЕРСОНАЖИ", _on_characters)
	_add_button(vbox, "ВЫХОД", _on_exit)

func _wire_existing() -> void:
	var play := get_node_or_null("VBox/BtnPlay")
	var chars := get_node_or_null("VBox/BtnCharacters")
	var quit := get_node_or_null("VBox/BtnExit")
	if play: play.pressed.connect(_on_play)
	if chars: chars.pressed.connect(_on_characters)
	if quit: quit.pressed.connect(_on_exit)

func _add_button(parent: Node, text: String, handler: Callable) -> void:
	var b := Button.new()
	b.text = text
	b.custom_minimum_size = Vector2(160, 30)
	b.add_theme_font_size_override("font_size", 16)
	b.pressed.connect(handler)
	parent.add_child(b)

func _gradient_bg() -> Texture2D:
	var grad := Gradient.new()
	grad.set_color(0, Color(0.04, 0.16, 0.07))
	grad.set_color(1, Color(0.02, 0.06, 0.03))
	var tex := GradientTexture2D.new()
	tex.gradient = grad
	tex.fill = GradientTexture2D.FILL_LINEAR
	tex.fill_from = Vector2(0, 0)
	tex.fill_to = Vector2(0, 1)
	tex.width = 480
	tex.height = 270
	return tex

func _on_play() -> void:
	get_tree().change_scene_to_file(GameManager.CHARACTER_SELECT_PATH)

func _on_characters() -> void:
	get_tree().change_scene_to_file(GameManager.CHARACTER_SELECT_PATH)

func _on_exit() -> void:
	get_tree().quit()
