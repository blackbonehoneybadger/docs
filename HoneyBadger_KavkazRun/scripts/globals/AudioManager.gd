extends Node
## Centralized music and SFX playback.
## Autoloaded as "AudioManager".
## SFX are looked up by short name; missing files are tolerated silently.

const SFX_DIR: String = "res://assets/audio/sfx/"
const MUSIC_DIR: String = "res://assets/audio/music/"
const SFX_VOICE_COUNT: int = 8

var _music_player: AudioStreamPlayer
var _sfx_players: Array[AudioStreamPlayer] = []
var _sfx_cache: Dictionary = {}
var _current_music_path: String = ""

var music_volume_db: float = -6.0
var sfx_volume_db: float = -3.0

func _ready() -> void:
	_music_player = AudioStreamPlayer.new()
	_music_player.bus = "Master"
	_music_player.volume_db = music_volume_db
	add_child(_music_player)
	_music_player.finished.connect(_on_music_finished)

	for i in SFX_VOICE_COUNT:
		var p := AudioStreamPlayer.new()
		p.bus = "Master"
		p.volume_db = sfx_volume_db
		add_child(p)
		_sfx_players.append(p)

func play_music(path: String, loop: bool = true) -> void:
	if path == _current_music_path and _music_player.playing:
		return
	var stream := _load_stream(path)
	if stream == null:
		return
	if loop:
		_apply_loop(stream)
	_current_music_path = path
	_music_player.stream = stream
	_music_player.volume_db = music_volume_db
	_music_player.play()

func stop_music() -> void:
	_music_player.stop()
	_current_music_path = ""

## Accepts either a short name ("jump") or a full res:// path.
func play_sfx(name_or_path: String) -> void:
	var path := name_or_path
	if not name_or_path.begins_with("res://"):
		path = SFX_DIR + name_or_path
		if not path.ends_with(".wav"):
			path += ".wav"
	var stream: AudioStream = _sfx_cache.get(path, null)
	if stream == null:
		stream = _load_stream(path)
		if stream == null:
			return
		_sfx_cache[path] = stream
	var player := _free_sfx_player()
	player.stream = stream
	player.volume_db = sfx_volume_db
	player.play()

func set_music_volume(linear: float) -> void:
	music_volume_db = linear_to_db(clampf(linear, 0.0001, 1.0))
	_music_player.volume_db = music_volume_db

func set_sfx_volume(linear: float) -> void:
	sfx_volume_db = linear_to_db(clampf(linear, 0.0001, 1.0))
	for p in _sfx_players:
		p.volume_db = sfx_volume_db

func _free_sfx_player() -> AudioStreamPlayer:
	for p in _sfx_players:
		if not p.playing:
			return p
	return _sfx_players[0]

func _load_stream(path: String) -> AudioStream:
	var resolved := path
	if not ResourceLoader.exists(resolved):
		# Tolerate .ogg references when only a generated .wav exists (or vice versa).
		if resolved.ends_with(".ogg"):
			resolved = resolved.trim_suffix(".ogg") + ".wav"
		elif resolved.ends_with(".wav"):
			resolved = resolved.trim_suffix(".wav") + ".ogg"
	if not ResourceLoader.exists(resolved):
		return null
	var res: Resource = load(resolved)
	if res is AudioStream:
		return res
	return null

func _apply_loop(stream: AudioStream) -> void:
	if stream is AudioStreamWAV:
		stream.loop_mode = AudioStreamWAV.LOOP_FORWARD
		stream.loop_begin = 0
		stream.loop_end = stream.data.size() / 2
	elif stream is AudioStreamOggVorbis:
		stream.loop = true

func _on_music_finished() -> void:
	# WAV loop handles itself; this catches non-looping streams we want repeated.
	if _current_music_path != "" and _music_player.stream is AudioStreamOggVorbis:
		_music_player.play()
