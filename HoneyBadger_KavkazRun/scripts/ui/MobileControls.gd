extends Control
## On-screen controls: a drag joystick on the left 40% (move_left/move_right)
## and three round action buttons on the right (jump / attack / special).
## Uses TouchScreenButton for multitouch buttons and tracks pointers manually
## for the joystick. Mouse events work too, for desktop testing.

const DEADZONE_PX := 12.0
const JOY_RADIUS := 60.0

var _joy_base: TextureRect
var _joy_knob: TextureRect
var _joy_center: Vector2
var _joy_pointer: int = -1   # -1 none, -2 mouse, >=0 touch index
var _move_state: int = 0     # -1 left, 0 none, 1 right
var _aim_state: int = 0      # -1 up, 0 none, 1 down

func _ready() -> void:
	set_anchors_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	if get_child_count() == 0:
		_build()

func _build() -> void:
	_joy_center = Vector2(96, 200)

	_joy_base = TextureRect.new()
	_joy_base.texture = _circle_texture(60, Color(1, 1, 1, 0.18))
	_joy_base.size = Vector2(120, 120)
	_joy_base.position = _joy_center - Vector2(60, 60)
	_joy_base.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_joy_base)

	_joy_knob = TextureRect.new()
	_joy_knob.texture = _circle_texture(26, Color(1, 1, 1, 0.45))
	_joy_knob.size = Vector2(52, 52)
	_joy_knob.position = _joy_center - Vector2(26, 26)
	_joy_knob.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_joy_knob)

	_make_action_button(Vector2(410, 215), Color(0.2, 0.8, 0.3), "jump", "A")
	_make_action_button(Vector2(356, 188), Color(0.85, 0.2, 0.2), "attack", "B")
	_make_action_button(Vector2(446, 178), Color(0.25, 0.45, 0.9), "special", "S")
	_make_action_button(Vector2(398, 150), Color(0.7, 0.4, 0.9), "shoot", "F")
	_make_pause_button(Vector2(462, 16))

func _make_action_button(pos: Vector2, color: Color, action: String, glyph: String) -> void:
	var btn := TouchScreenButton.new()
	btn.texture_normal = _circle_texture(24, color)
	btn.action = action
	btn.passby_press = true
	btn.position = pos - Vector2(24, 24)
	add_child(btn)

	var label := Label.new()
	label.text = glyph
	label.add_theme_font_size_override("font_size", 18)
	label.add_theme_color_override("font_color", Color(1, 1, 1))
	label.size = Vector2(48, 48)
	label.position = pos - Vector2(24, 24)
	label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(label)

func _make_pause_button(pos: Vector2) -> void:
	var btn := TouchScreenButton.new()
	btn.texture_normal = _circle_texture(14, Color(0.9, 0.9, 0.9, 0.5))
	btn.action = "pause"
	btn.position = pos - Vector2(14, 14)
	add_child(btn)
	var bars := Label.new()
	bars.text = "II"
	bars.add_theme_font_size_override("font_size", 14)
	bars.add_theme_color_override("font_color", Color(0.1, 0.1, 0.1))
	bars.position = pos - Vector2(14, 14)
	bars.size = Vector2(28, 28)
	bars.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	bars.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	bars.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(bars)

func _input(event: InputEvent) -> void:
	if event is InputEventScreenTouch:
		if event.pressed and _joy_pointer == -1 and _in_left_zone(event.position):
			_joy_pointer = event.index
			_joy_center = event.position
			_update_knob(event.position)
		elif not event.pressed and _joy_pointer == event.index:
			_release_joystick()
	elif event is InputEventScreenDrag and _joy_pointer == event.index:
		_update_knob(event.position)
	elif event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_LEFT:
		if event.pressed and _joy_pointer == -1 and _in_left_zone(event.position):
			_joy_pointer = -2
			_joy_center = event.position
			_update_knob(event.position)
		elif not event.pressed and _joy_pointer == -2:
			_release_joystick()
	elif event is InputEventMouseMotion and _joy_pointer == -2:
		_update_knob(event.position)

func _in_left_zone(pos: Vector2) -> bool:
	return pos.x < get_viewport_rect().size.x * 0.4

func _update_knob(pos: Vector2) -> void:
	var offset := pos - _joy_center
	if offset.length() > JOY_RADIUS:
		offset = offset.normalized() * JOY_RADIUS
	if _joy_knob:
		_joy_knob.position = _joy_center + offset - Vector2(26, 26)
	if _joy_base:
		_joy_base.position = _joy_center - Vector2(60, 60)
	_set_move(offset.x)
	_set_aim(offset.y)

func _set_move(dx: float) -> void:
	var new_state := 0
	if dx < -DEADZONE_PX:
		new_state = -1
	elif dx > DEADZONE_PX:
		new_state = 1
	if new_state == _move_state:
		return
	# Release the old direction, press the new one.
	Input.action_release("move_left")
	Input.action_release("move_right")
	if new_state == -1:
		Input.action_press("move_left")
	elif new_state == 1:
		Input.action_press("move_right")
	_move_state = new_state

func _set_aim(dy: float) -> void:
	var new_state := 0
	if dy < -DEADZONE_PX * 1.6:
		new_state = -1
	elif dy > DEADZONE_PX * 1.6:
		new_state = 1
	if new_state == _aim_state:
		return
	Input.action_release("aim_up")
	Input.action_release("aim_down")
	if new_state == -1:
		Input.action_press("aim_up")
	elif new_state == 1:
		Input.action_press("aim_down")
	_aim_state = new_state

func _release_joystick() -> void:
	_joy_pointer = -1
	_set_move(0.0)
	_set_aim(0.0)
	Input.action_release("move_left")
	Input.action_release("move_right")
	Input.action_release("aim_up")
	Input.action_release("aim_down")
	_joy_center = Vector2(96, 200)
	if _joy_knob:
		_joy_knob.position = _joy_center - Vector2(26, 26)
	if _joy_base:
		_joy_base.position = _joy_center - Vector2(60, 60)

func _circle_texture(radius: int, color: Color) -> Texture2D:
	var d := radius * 2
	var img := Image.create(d, d, false, Image.FORMAT_RGBA8)
	img.fill(Color(0, 0, 0, 0))
	var c := Vector2(radius, radius)
	for y in d:
		for x in d:
			if Vector2(x, y).distance_to(c) <= float(radius) - 0.5:
				img.set_pixel(x, y, color)
	return ImageTexture.create_from_image(img)
