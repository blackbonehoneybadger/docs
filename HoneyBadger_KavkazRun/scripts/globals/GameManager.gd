extends Node
## Global game state: selected character, lives, coins, score, high score.
## Autoloaded as "GameManager".

signal lives_changed(lives: int)
signal coins_changed(coins: int)
signal score_changed(score: int)

const STARTING_LIVES: int = 3
const COINS_PER_EXTRA_LIFE: int = 100
const SAVE_PATH: String = "user://honey_badger_save.cfg"

const LEVEL_SCENE_PATH: String = "res://scenes/levels/world_01_adygea/Level_01_01.tscn"
const MAIN_MENU_PATH: String = "res://scenes/ui/MainMenu.tscn"
const CHARACTER_SELECT_PATH: String = "res://scenes/ui/CharacterSelect.tscn"

var selected_character: String = "honey_badger"
var lives: int = STARTING_LIVES
var coins: int = 0
var score: int = 0
var high_score: int = 0

# Checkpoint position within the active level (Vector2.ZERO = level start).
var checkpoint_position: Vector2 = Vector2.ZERO
var has_checkpoint: bool = false

func _ready() -> void:
	_ensure_input_actions()
	_load_high_score()

## Belt-and-suspenders: guarantee the input actions exist even if the
## project.godot input map fails to load for any reason.
func _ensure_input_actions() -> void:
	var defaults := {
		"move_left": [KEY_A, KEY_LEFT],
		"move_right": [KEY_D, KEY_RIGHT],
		"jump": [KEY_SPACE, KEY_W],
		"aim_up": [KEY_UP, KEY_I],
		"aim_down": [KEY_DOWN, KEY_K],
		"attack": [KEY_Z, KEY_J],
		"special": [KEY_X, KEY_U],
		"shoot": [KEY_C, KEY_L],
		"pause": [KEY_ESCAPE],
	}
	for action_name in defaults.keys():
		if not InputMap.has_action(action_name):
			InputMap.add_action(action_name)
		for keycode in defaults[action_name]:
			var already := false
			for ev in InputMap.action_get_events(action_name):
				if ev is InputEventKey and ev.physical_keycode == keycode:
					already = true
					break
			if not already:
				var key_event := InputEventKey.new()
				key_event.physical_keycode = keycode
				InputMap.action_add_event(action_name, key_event)

func get_character_scene_path() -> String:
	return "res://scenes/characters/%s.tscn" % _character_scene_name(selected_character)

func _character_scene_name(id: String) -> String:
	match id:
		"honey_badger":
			return "HoneyBadger"
		"boy":
			return "Boy"
		"mr_kroo":
			return "MrKroo"
		_:
			return "HoneyBadger"

func start_new_game() -> void:
	lives = STARTING_LIVES
	coins = 0
	score = 0
	checkpoint_position = Vector2.ZERO
	has_checkpoint = false
	emit_signal("lives_changed", lives)
	emit_signal("coins_changed", coins)
	emit_signal("score_changed", score)

func add_coin(amount: int = 1) -> void:
	coins += amount
	add_score(50 * amount)
	while coins >= COINS_PER_EXTRA_LIFE:
		coins -= COINS_PER_EXTRA_LIFE
		lives += 1
		emit_signal("lives_changed", lives)
	emit_signal("coins_changed", coins)

func add_score(amount: int) -> void:
	score += amount
	if score > high_score:
		high_score = score
	emit_signal("score_changed", score)

## Returns true if the player still has lives left, false on game over.
func lose_life() -> bool:
	lives -= 1
	emit_signal("lives_changed", lives)
	if lives <= 0:
		_save_high_score()
		return false
	return true

func set_checkpoint(pos: Vector2) -> void:
	checkpoint_position = pos
	has_checkpoint = true

func level_complete() -> void:
	add_score(1000)
	_save_high_score()

func _load_high_score() -> void:
	var cfg := ConfigFile.new()
	if cfg.load(SAVE_PATH) == OK:
		high_score = int(cfg.get_value("progress", "high_score", 0))

func _save_high_score() -> void:
	var cfg := ConfigFile.new()
	cfg.set_value("progress", "high_score", high_score)
	cfg.save(SAVE_PATH)
