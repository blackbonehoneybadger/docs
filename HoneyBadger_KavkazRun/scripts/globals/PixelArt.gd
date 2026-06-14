class_name PixelArt
extends RefCounted
## Builds small pixel-art ImageTextures from a list of colored rectangles.
## Used so characters, enemies and objects always have a visual even with no
## external sprite files. Each "rect" is [x, y, w, h, Color].

static func make_texture(width: int, height: int, rects: Array) -> ImageTexture:
	var img := Image.create(width, height, false, Image.FORMAT_RGBA8)
	img.fill(Color(0, 0, 0, 0))
	for r in rects:
		_fill_rect(img, r[0], r[1], r[2], r[3], r[4])
	return ImageTexture.create_from_image(img)

static func make_image(width: int, height: int, rects: Array) -> Image:
	var img := Image.create(width, height, false, Image.FORMAT_RGBA8)
	img.fill(Color(0, 0, 0, 0))
	for r in rects:
		_fill_rect(img, r[0], r[1], r[2], r[3], r[4])
	return img

static func _fill_rect(img: Image, x: int, y: int, w: int, h: int, color: Color) -> void:
	for iy in range(y, y + h):
		if iy < 0 or iy >= img.get_height():
			continue
		for ix in range(x, x + w):
			if ix < 0 or ix >= img.get_width():
				continue
			img.set_pixel(ix, iy, color)

# ---- Per-character placeholder rect specs (origin top-left of a 32x48 frame) --

static func honey_badger_rects() -> Array:
	var body := Color("#2E5A2E")
	var head := Color("#D8C29A")
	var hat := Color("#5B3A1E")
	var beard := Color("#3A2410")
	var white := Color(1, 1, 1)
	return [
		[4, 12, 24, 36, body],     # body
		[6, 2, 20, 18, head],      # head
		[5, 0, 22, 8, hat],        # hat
		[8, 16, 16, 10, beard],    # beard
		[10, 8, 2, 2, white],      # eye L
		[20, 8, 2, 2, white],      # eye R
	]

static func boy_rects() -> Array:
	var body := Color("#3A3A4A")
	var head := Color("#D8C29A")
	var yellow := Color("#F2C400")
	return [
		[0, 12, 32, 36, body],     # wide body
		[2, 2, 28, 22, head],      # wide head
		[6, 26, 3, 3, yellow],     # "B"
		[12, 26, 3, 3, yellow],    # "O"
		[18, 26, 3, 3, yellow],    # "Y"
		[9, 9, 3, 3, Color(0.1,0.1,0.1)],
		[21, 9, 3, 3, Color(0.1,0.1,0.1)],
	]

static func mr_kroo_rects() -> Array:
	var body := Color("#6A6A72")
	var head := Color("#D8C29A")
	var cap := Color("#1E2A5B")
	var white := Color(1, 1, 1)
	return [
		[6, 8, 20, 40, body],      # narrow tall body
		[7, 0, 18, 18, head],      # narrow head
		[6, 0, 20, 6, cap],        # cap
		[10, 8, 4, 4, white],      # round glasses L
		[18, 8, 4, 4, white],      # round glasses R
		[11, 9, 2, 2, Color(0.1,0.1,0.1)],
		[19, 9, 2, 2, Color(0.1,0.1,0.1)],
	]

static func forest_spirit_rects() -> Array:
	var glow := Color("#7CFFB2")
	var core := Color("#2FA46A")
	var white := Color(1, 1, 1)
	return [
		[4, 4, 16, 16, glow],
		[7, 7, 10, 10, core],
		[9, 9, 2, 2, white],
		[13, 9, 2, 2, white],
	]

static func stone_snail_rects() -> Array:
	var shell := Color("#8A8A95")
	var shell2 := Color("#6A6A75")
	var body := Color("#C9B07A")
	return [
		[2, 14, 24, 8, body],      # foot
		[8, 4, 16, 16, shell],     # shell
		[12, 8, 8, 8, shell2],     # shell swirl
		[0, 8, 4, 4, body],        # eye stalk
	]

static func cave_bat_rects() -> Array:
	var wing := Color("#4A3A5A")
	var body := Color("#2A2030")
	var red := Color("#FF5555")
	return [
		[0, 8, 8, 6, wing],        # left wing
		[16, 8, 8, 6, wing],       # right wing
		[8, 6, 8, 10, body],       # body
		[9, 8, 2, 2, red],
		[13, 8, 2, 2, red],
	]
