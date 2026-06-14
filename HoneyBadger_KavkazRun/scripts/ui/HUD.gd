extends Control
## Heads-up display: HP hearts, lives, coins (top-left) and score (top-right).

var _hearts: Label
var _lives: Label
var _coins: Label
var _score: Label
var _max_health: int = 3
var _current_health: int = 3

func _ready() -> void:
	set_anchors_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	if get_child_count() == 0:
		_build()
	GameManager.lives_changed.connect(_on_lives_changed)
	GameManager.coins_changed.connect(_on_coins_changed)
	GameManager.score_changed.connect(_on_score_changed)
	_on_lives_changed(GameManager.lives)
	_on_coins_changed(GameManager.coins)
	_on_score_changed(GameManager.score)

func _build() -> void:
	_hearts = _make_label(Vector2(8, 6), 16, Color(1, 0.3, 0.3))
	add_child(_hearts)
	_lives = _make_label(Vector2(8, 26), 14, Color(1, 1, 1))
	add_child(_lives)
	_coins = _make_label(Vector2(8, 44), 14, Color(1, 0.85, 0.2))
	add_child(_coins)

	_score = _make_label(Vector2(330, 6), 14, Color(1, 1, 1))
	_score.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	_score.size = Vector2(142, 20)
	add_child(_score)

func _make_label(pos: Vector2, font_size: int, color: Color) -> Label:
	var l := Label.new()
	l.position = pos
	l.add_theme_font_size_override("font_size", font_size)
	l.add_theme_color_override("font_color", color)
	l.add_theme_color_override("font_outline_color", Color(0, 0, 0))
	l.add_theme_constant_override("outline_size", 4)
	return l

## Called by the level after the player is spawned.
func bind_player(player: Node) -> void:
	if player and player.has_signal("health_changed"):
		player.connect("health_changed", _on_health_changed)
		var mh: Variant = player.get("max_health")
		var ch: Variant = player.get("current_health")
		if mh != null:
			_max_health = int(mh)
		if ch != null:
			_current_health = int(ch)
		_update_hearts()

func _on_health_changed(current: int, max_health: int) -> void:
	_current_health = current
	_max_health = max_health
	_update_hearts()

func _update_hearts() -> void:
	if _hearts == null:
		return
	var s := ""
	for i in _max_health:
		s += "♥" if i < _current_health else "♡"
	_hearts.text = s

func _on_lives_changed(lives: int) -> void:
	if _lives:
		_lives.text = "Жизни: x%d" % lives

func _on_coins_changed(coins: int) -> void:
	if _coins:
		_coins.text = "Монеты: %d" % coins

func _on_score_changed(score: int) -> void:
	if _score:
		_score.text = "Очки: %d" % score
