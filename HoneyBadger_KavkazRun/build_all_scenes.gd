@tool
extends EditorScript
## One-shot generator. In the Godot editor open this file and run it
## (File ▸ Run, or the Run button in the script editor) to create every .tscn
## scene, placeholder sprite PNG and procedural sound the project references.
##
## Safe to re-run; it overwrites the generated files.

const SAMPLE_RATE := 22050

func _run() -> void:
	_generate_sprites()
	_generate_sounds()
	_generate_music()
	_generate_scenes()
	print("[build_all_scenes] Done. All scenes, sprites and sounds generated.")

# =============================== SCENES ======================================

func _generate_scenes() -> void:
	# UI scenes (root Control + script).
	_save_scene("res://scenes/ui/MainMenu.tscn", _control("MainMenu", "res://scripts/ui/MainMenu.gd"))
	_save_scene("res://scenes/ui/CharacterSelect.tscn", _control("CharacterSelect", "res://scripts/ui/CharacterSelect.gd"))
	_save_scene("res://scenes/ui/HUD.tscn", _control("HUD", "res://scripts/ui/HUD.gd"))
	_save_scene("res://scenes/ui/PauseMenu.tscn", _control("PauseMenu", "res://scripts/ui/PauseMenu.gd"))
	_save_scene("res://scenes/ui/GameOver.tscn", _control("GameOver", "res://scripts/ui/GameOver.gd"))
	_save_scene("res://scenes/ui/LevelComplete.tscn", _control("LevelComplete", "res://scripts/ui/LevelComplete.gd"))
	_save_scene("res://scenes/ui/MobileControls.tscn", _control("MobileControls", "res://scripts/ui/MobileControls.gd"))

	# Characters (root CharacterBody2D + script).
	_save_scene("res://scenes/characters/HoneyBadger.tscn", _body2d("HoneyBadger", "res://scripts/characters/HoneyBadger.gd"))
	_save_scene("res://scenes/characters/Boy.tscn", _body2d("Boy", "res://scripts/characters/Boy.gd"))
	_save_scene("res://scenes/characters/MrKroo.tscn", _body2d("MrKroo", "res://scripts/characters/MrKroo.gd"))

	# Enemies (root CharacterBody2D + script).
	_save_scene("res://scenes/enemies/ForestSpirit.tscn", _body2d("ForestSpirit", "res://scripts/enemies/ForestSpirit.gd"))
	_save_scene("res://scenes/enemies/StoneSnail.tscn", _body2d("StoneSnail", "res://scripts/enemies/StoneSnail.gd"))
	_save_scene("res://scenes/enemies/CaveBat.tscn", _body2d("CaveBat", "res://scripts/enemies/CaveBat.gd"))
	_save_scene("res://scenes/enemies/Turret.tscn", _body2d("Turret", "res://scripts/enemies/Turret.gd"))

	# Objects (root Area2D / StaticBody2D + script).
	_save_scene("res://scenes/objects/Coin.tscn", _area2d("Coin", "res://scripts/objects/Coin.gd"))
	_save_scene("res://scenes/objects/Checkpoint.tscn", _area2d("Checkpoint", "res://scripts/objects/Checkpoint.gd"))
	_save_scene("res://scenes/objects/LevelEnd.tscn", _area2d("LevelEnd", "res://scripts/objects/LevelEnd.gd"))
	_save_scene("res://scenes/objects/Projectile.tscn", _area2d("Projectile", "res://scripts/objects/Projectile.gd"))
	_save_scene("res://scenes/objects/WeaponPickup.tscn", _area2d("WeaponPickup", "res://scripts/objects/WeaponPickup.gd"))
	_save_scene("res://scenes/objects/PowerUpItem.tscn", _area2d("PowerUpItem", "res://scripts/objects/PowerUpItem.gd"))
	var qblock := StaticBody2D.new()
	qblock.name = "QuestionBlock"
	qblock.set_script(load("res://scripts/objects/QuestionBlock.gd"))
	_save_scene("res://scenes/objects/QuestionBlock.tscn", qblock)

	# Level (root Node2D + script).
	var level := Node2D.new()
	level.name = "Level_01_01"
	level.set_script(load("res://scripts/levels/Level01_01.gd"))
	_save_scene("res://scenes/levels/world_01_adygea/Level_01_01.tscn", level)

func _control(node_name: String, script_path: String) -> Control:
	var c := Control.new()
	c.name = node_name
	c.set_anchors_preset(Control.PRESET_FULL_RECT)
	c.set_script(load(script_path))
	return c

func _body2d(node_name: String, script_path: String) -> CharacterBody2D:
	var b := CharacterBody2D.new()
	b.name = node_name
	b.set_script(load(script_path))
	return b

func _area2d(node_name: String, script_path: String) -> Area2D:
	var a := Area2D.new()
	a.name = node_name
	a.set_script(load(script_path))
	return a

func _save_scene(path: String, root: Node) -> void:
	var packed := PackedScene.new()
	var err := packed.pack(root)
	if err != OK:
		push_error("Failed to pack %s (err %d)" % [path, err])
		return
	var save_err := ResourceSaver.save(packed, path)
	if save_err != OK:
		push_error("Failed to save %s (err %d)" % [path, save_err])
	else:
		print("  scene  ", path)
	root.free()

# =============================== SPRITES =====================================

func _generate_sprites() -> void:
	_save_png(PixelArt.make_image(32, 48, PixelArt.honey_badger_rects()),
		"res://assets/characters/honey_badger/honey_badger.png")
	_save_png(PixelArt.make_image(32, 48, PixelArt.boy_rects()),
		"res://assets/characters/boy/boy.png")
	_save_png(PixelArt.make_image(32, 48, PixelArt.mr_kroo_rects()),
		"res://assets/characters/mr_kroo/mr_kroo.png")
	# Portraits.
	_save_png(PixelArt.make_image(32, 48, PixelArt.honey_badger_rects()),
		"res://assets/ui/portraits/honey_badger.png")
	_save_png(PixelArt.make_image(32, 48, PixelArt.boy_rects()),
		"res://assets/ui/portraits/boy.png")
	_save_png(PixelArt.make_image(32, 48, PixelArt.mr_kroo_rects()),
		"res://assets/ui/portraits/mr_kroo.png")
	# Enemy reference sprites.
	_save_png(PixelArt.make_image(24, 24, PixelArt.forest_spirit_rects()),
		"res://assets/tilesets/world_01/forest_spirit.png")
	_save_png(PixelArt.make_image(24, 24, PixelArt.stone_snail_rects()),
		"res://assets/tilesets/world_01/stone_snail.png")
	_save_png(PixelArt.make_image(24, 24, PixelArt.cave_bat_rects()),
		"res://assets/tilesets/world_01/cave_bat.png")

func _save_png(img: Image, path: String) -> void:
	var err := img.save_png(path)
	if err == OK:
		print("  sprite ", path)
	else:
		push_error("Failed to save png %s (err %d)" % [path, err])

# =============================== SOUNDS ======================================

func _generate_sounds() -> void:
	_save_wav(_tone(880.0, 0.10, 0.6, "sine", true), "res://assets/audio/sfx/jump.wav")
	_save_wav(_mix_tone([220.0, 440.0], 0.15, 0.5, "square"), "res://assets/audio/sfx/attack.wav")
	_save_wav(_tone(1320.0, 0.08, 0.5, "sine", true), "res://assets/audio/sfx/coin.wav")
	_save_wav(_sweep(600.0, 200.0, 0.20, 0.5, "square"), "res://assets/audio/sfx/enemy_die.wav")
	_save_wav(_tone(150.0, 0.10, 0.6, "square", true), "res://assets/audio/sfx/player_hurt.wav")
	_save_wav(_melody([440.0, 330.0, 262.0, 196.0], 0.125, 0.5, "square"), "res://assets/audio/sfx/player_die.wav")
	_save_wav(_tone(110.0, 0.10, 0.7, "square", true), "res://assets/audio/sfx/stomp.wav")

func _generate_music() -> void:
	# 8-bit, 4/4, ~120 BPM. Saved as .wav; AudioManager loops them at runtime.
	var menu_notes := [262.0, 330.0, 392.0, 330.0, 294.0, 349.0, 440.0, 349.0]
	_save_wav(_melody(menu_notes, 0.25, 0.35, "square"), "res://assets/audio/music/main_menu.wav")
	var world_notes := [392.0, 392.0, 440.0, 392.0, 523.0, 494.0, 440.0, 392.0,
		349.0, 392.0, 440.0, 392.0, 330.0, 294.0, 262.0, 294.0]
	_save_wav(_melody(world_notes, 0.22, 0.35, "square"), "res://assets/audio/music/world_01.wav")

func _save_wav(stream: AudioStreamWAV, path: String) -> void:
	var err := stream.save_to_wav(path)
	if err == OK:
		print("  sound  ", path)
	else:
		push_error("Failed to save wav %s (err %d)" % [path, err])

# ---- synthesis helpers (16-bit mono PCM) ----

func _make_wav(samples: PackedFloat32Array) -> AudioStreamWAV:
	var bytes := PackedByteArray()
	bytes.resize(samples.size() * 2)
	for i in samples.size():
		var v := int(clampf(samples[i], -1.0, 1.0) * 32767.0)
		bytes.encode_s16(i * 2, v)
	var wav := AudioStreamWAV.new()
	wav.format = AudioStreamWAV.FORMAT_16_BITS
	wav.mix_rate = SAMPLE_RATE
	wav.stereo = false
	wav.data = bytes
	return wav

func _osc(phase: float, kind: String) -> float:
	match kind:
		"square":
			return 1.0 if sin(phase) >= 0.0 else -1.0
		_:
			return sin(phase)

func _tone(freq: float, dur: float, vol: float, kind: String, decay: bool) -> AudioStreamWAV:
	var n := int(dur * SAMPLE_RATE)
	var samples := PackedFloat32Array()
	samples.resize(n)
	for i in n:
		var t := float(i) / SAMPLE_RATE
		var env := 1.0
		if decay:
			env = 1.0 - float(i) / n
		samples[i] = _osc(TAU * freq * t, kind) * vol * env
	return _make_wav(samples)

func _mix_tone(freqs: Array, dur: float, vol: float, kind: String) -> AudioStreamWAV:
	var n := int(dur * SAMPLE_RATE)
	var samples := PackedFloat32Array()
	samples.resize(n)
	for i in n:
		var t := float(i) / SAMPLE_RATE
		var env := 1.0 - float(i) / n
		var s := 0.0
		for f in freqs:
			s += _osc(TAU * float(f) * t, kind)
		samples[i] = (s / freqs.size()) * vol * env
	return _make_wav(samples)

func _sweep(f0: float, f1: float, dur: float, vol: float, kind: String) -> AudioStreamWAV:
	var n := int(dur * SAMPLE_RATE)
	var samples := PackedFloat32Array()
	samples.resize(n)
	var phase := 0.0
	for i in n:
		var k := float(i) / n
		var freq := lerpf(f0, f1, k)
		phase += TAU * freq / SAMPLE_RATE
		samples[i] = _osc(phase, kind) * vol * (1.0 - k)
	return _make_wav(samples)

func _melody(notes: Array, note_dur: float, vol: float, kind: String) -> AudioStreamWAV:
	var samples := PackedFloat32Array()
	var per := int(note_dur * SAMPLE_RATE)
	for note in notes:
		for i in per:
			var t := float(i) / SAMPLE_RATE
			var env := minf(1.0, (1.0 - float(i) / per) * 4.0)
			samples.append(_osc(TAU * float(note) * t, kind) * vol * env)
	return _make_wav(samples)
