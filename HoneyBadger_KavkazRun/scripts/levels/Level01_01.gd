extends Node2D
## World 1 — Adygea, stage 1. Owns level construction, the player, the camera,
## the HUD / mobile controls / pause overlay, respawn and win/lose flow.

const WORLD_MUSIC := "res://assets/audio/music/world_01.ogg"
const RESPAWN_DELAY := 1.0

const PLAYER_SCRIPTS := {
	"honey_badger": "res://scripts/characters/HoneyBadger.gd",
	"boy": "res://scripts/characters/Boy.gd",
	"mr_kroo": "res://scripts/characters/MrKroo.gd",
}

var _generator := LevelGenerator.new()
var _player: BaseCharacter
var _spawn: Vector2
var _hud: Control
var _completed: bool = false

func _ready() -> void:
	add_to_group("level")
	_spawn = _generator.build(self)
	_spawn_player()
	_add_camera()
	_add_ui()
	AudioManager.play_music(WORLD_MUSIC, true)

func _spawn_player() -> void:
	var id: String = GameManager.selected_character
	var script_path: String = PLAYER_SCRIPTS.get(id, PLAYER_SCRIPTS["honey_badger"])
	# Prefer the character scene; fall back to building a body from the script.
	var scene_path := GameManager.get_character_scene_path()
	var inst: Node
	if ResourceLoader.exists(scene_path):
		inst = (load(scene_path) as PackedScene).instantiate()
	else:
		inst = CharacterBody2D.new()
		inst.set_script(load(script_path))
	_player = inst as BaseCharacter
	var start: Vector2 = GameManager.checkpoint_position if GameManager.has_checkpoint else _spawn
	_player.global_position = start
	add_child(_player)
	_player.player_died.connect(_on_player_died)

func _add_camera() -> void:
	var cam := Camera2D.new()
	cam.name = "Camera2D"
	cam.position_smoothing_enabled = true
	cam.position_smoothing_speed = 6.0
	cam.limit_left = 0
	cam.limit_top = -200
	cam.limit_right = int(LevelGenerator.LEVEL_WIDTH)
	cam.limit_bottom = int(LevelGenerator.LEVEL_HEIGHT)
	_player.add_child(cam)
	cam.make_current()

func _add_ui() -> void:
	var layer := CanvasLayer.new()
	layer.name = "UILayer"
	add_child(layer)

	_hud = _make_ui_control("res://scripts/ui/HUD.gd", "HUD")
	layer.add_child(_hud)
	if _hud.has_method("bind_player"):
		_hud.call("bind_player", _player)

	var mobile := _make_ui_control("res://scripts/ui/MobileControls.gd", "MobileControls")
	layer.add_child(mobile)

	var pause := _make_ui_control("res://scripts/ui/PauseMenu.gd", "PauseMenu")
	pause.process_mode = Node.PROCESS_MODE_ALWAYS
	layer.add_child(pause)

func _make_ui_control(script_path: String, node_name: String) -> Control:
	var c := Control.new()
	c.name = node_name
	c.set_anchors_preset(Control.PRESET_FULL_RECT)
	c.set_script(load(script_path))
	return c

# ------------------------------ flow control ---------------------------------

func _on_player_died() -> void:
	if _completed:
		return
	var still_alive := GameManager.lose_life()
	if still_alive:
		await get_tree().create_timer(RESPAWN_DELAY).timeout
		if is_instance_valid(_player):
			var pos: Vector2 = GameManager.checkpoint_position if GameManager.has_checkpoint else _spawn
			_player.reset_for_respawn(pos)
	else:
		await get_tree().create_timer(RESPAWN_DELAY).timeout
		get_tree().change_scene_to_file("res://scenes/ui/GameOver.tscn")

func complete_level() -> void:
	if _completed:
		return
	_completed = true
	GameManager.level_complete()
	if is_instance_valid(_player):
		_player.set_physics_process(false)
	await get_tree().create_timer(0.8).timeout
	get_tree().change_scene_to_file("res://scenes/ui/LevelComplete.tscn")
