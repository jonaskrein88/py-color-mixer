


from ColorMixer import RGBPalette, OKLCHPalette, HSVPalette, OKLABPalette
import ColorMixer as mxr
import numpy as np

from PIL import Image, ImageDraw, ImageFont

import random




# little preview image with hex codes
def pretty_preview(palette, out_file=None, show=True, color_labels=None, title=None, sub_title=None):

	num_colors = len(palette)
	column_width = 200
	image_height = 800
	image_width = column_width * num_colors

	img = Image.new("RGB", (image_width, image_height), "#FFFFFF")
	draw = ImageDraw.Draw(img)

	try:
		font_hex = ImageFont.truetype("arialbd.ttf", 24)
		font_label = ImageFont.truetype("arial.ttf", 16)
		font_title = ImageFont.truetype("arialbd.ttf", 32)
	except IOError:
		font_hex = ImageFont.load_default()
		font_label = ImageFont.load_default()
		font_title = ImageFont.load_default()
		print("using fallback fonts")

	hexes = palette.to_srgb().to_hex()
	lumas = palette.luma_physical()

	for i, colorHex in enumerate(hexes):

		x_start = i * column_width
		x_end = x_start + column_width

		draw.rectangle([x_start, 0, x_end, image_height], fill=colorHex)

		# write hex
		hex_text = colorHex#.replace("#", "").upper()
		hex_text_x = x_start + (column_width - draw.textlength(hex_text, font=font_hex)) / 2

		text_color = '#eeeeee' if lumas[i]<0.5 else '#444444'
		draw.text((hex_text_x, image_height - 90), hex_text, fill=text_color, font=font_hex)

		# write label if present
		if color_labels:

			label_text = color_labels[i]
			label_text_x = x_start + (column_width - draw.textlength(label_text, font=font_label)) / 2
			draw.text((label_text_x, image_height - 60), label_text, fill=text_color, font=font_label)

	if title:
		title_color = '#ffffff'
		title_x = image_width/2 - draw.textlength(title, font=font_title) / 2
		draw.text((title_x, 30), title, fill=title_color, font=font_title)

	if sub_title:
		title_color = '#ffffff'
		title_x = image_width/2 - draw.textlength(sub_title, font=font_hex) / 2
		draw.text((title_x, 72), sub_title, fill=title_color, font=font_hex)

	if out_file:
		img.save(out_file)

	if show:
		img.show()













def example_smooth_luma_00():
	'''
	generates a color palette and remaps the luma so it has a smooth brightness gradient
	'''

	# as a starting point we just take red, green and blue and rotate them in OKCLCH
	lch    = RGBPalette.from_hex('ff0000', '00ff00', '0000ff').to_oklch()
	colors = lch.shift_hue(-120).resize(7)

	lightness = np.linspace(0.1, 0.9, 7)
	hue       = colors.get_hue()
	chroma    = colors.get_chroma()

	final = mxr.OKLCHPalette.from_channels(lightness, chroma, hue)

	final = final.make_srgb_safe()
	rgb = final.to_srgb().clamp()
	mxr.plot_XYY([rgb])
	pretty_preview(rgb,"images/smooth_palette_00.jpg", title="Test Smooth Luma")




def example_smooth_luma_01():
	'''
	generates a random palette with smooth lightness
	'''
	lightness = np.linspace(0.1, 0.9, 7)
	random_hues = np.random.uniform(0.0, 360.0, 7)
	colors = mxr.OKLCHPalette.from_channels(lightness, lightness, random_hues)
	colors = colors.make_srgb_safe()
	pretty_preview(colors,"images/smooth_palette_01.jpg")
	#mxr.plot_XYY([colors])









def example_triadic(seed=None):

	'''
	create a small triadic harmony,
	with two additional variants
	'''
	root = OKLCHPalette.new_random(1,seed=seed)
	triad = root.triadic()

	# try and asign the roles optimally based on hue
	sorted_colors = root.join(triad).sort_for_roles()

	base 		 = sorted_colors[0].apply_role(mxr.Role.DEEP_BASE)
	mid  		 = sorted_colors[0].apply_role(mxr.Role.MID_SUPPORT)
	heroAccent   = sorted_colors[1].apply_role(mxr.Role.HERO_ACCENT)
	secondAccent = sorted_colors[2].apply_role(mxr.Role.SECOND_ACCENT)
	highlight    = sorted_colors[0].apply_role(mxr.Role.HIGHLIGHT)

	colors = base.join(mid,secondAccent, heroAccent, highlight)
	labels = ['background', 'midtone', 'secondary accent', 'main accent', 'highlight']

	pretty_preview(colors, "images/triadic_00.jpg", color_labels=labels)
	mxr.plot_colors_oklch(colors, out_file="images/triadic_00_wheel.png")




# hardcoded seed for testing
def example_split_complementary_00(seed=None):
	root = OKLCHPalette.new_random(1,seed=42)

	comp = root.complement(bias=0).analogous(2,35)


	base 		 = root.apply_role(mxr.Role.DEEP_BASE)
	mid  		 = root.apply_role(mxr.Role.MID_SUPPORT)
	heroAccent   = comp[0].apply_role(mxr.Role.HERO_ACCENT)
	secondAccent = comp[1].apply_role(mxr.Role.SECOND_ACCENT)
	highlight    = root.apply_role(mxr.Role.HIGHLIGHT)

	colors = base.join(mid,secondAccent, heroAccent, highlight)
	labels = ['background', 'midtone', 'secondary accent', 'main accent', 'highlight']

	pretty_preview(colors, "images/split_complement_02.jpg", color_labels=labels)
	mxr.plot_colors_oklch(colors, out_file="images/split_complement_02_wheel.png")
	#mxr.plot_perceived_brightness(colors)



def example_split_complementary_01(seed=None):

	root = OKLCHPalette.new_random(1,seed=seed)

	split = root.split_complement(bias=0)
	base 		 = root.apply_role(mxr.Role.DEEP_BASE)
	mid  		 = root.apply_role(mxr.Role.MID_SUPPORT)
	heroAccent   = split[1].apply_role(mxr.Role.HERO_ACCENT)
	secondAccent = split[0].apply_role(mxr.Role.SECOND_ACCENT)
	highlight    = root.apply_role(mxr.Role.HIGHLIGHT)

	colors = base.join(mid,secondAccent, heroAccent, highlight)
	colors = colors.limit_chroma(0.2)
	colors = colors.linearize_lightness()
	colors = colors.make_srgb_safe()
	pretty_preview(colors, "images/split_complement_00.jpg")
	mxr.plot_colors_oklch(colors,out_file="images/split_complement_00_wheel.png")
	#mxr.plot_XYY([colors])



def example_square():

	root = OKLCHPalette.new_random(1)
	square = root.square()
	c5 = square[0].fade(0.5) 

	colors = root.join(square,c5)
	#colors = colors.make_srgb_safe()
	pretty_preview(colors, "images/square_00.jpg")
	mxr.plot_colors_oklch(colors, out_file="images/square_00_wheel.png")




def example_analogous(seed=None):
	root = OKLCHPalette.new_random(1,seed=seed)
	colors = root.analogous(5).sort_for_roles()
	roles = [
		mxr.Role.DEEP_BASE,
		mxr.Role.MID_SUPPORT,
		mxr.Role.HERO_ACCENT,
		mxr.Role.SECOND_ACCENT,
		mxr.Role.HIGHLIGHT]
	colors = colors.apply_roles(roles)
	labels = ['background', 'midtone', 'secondary accent', 'main accent', 'highlight']
	pretty_preview(colors, "images/analogous_00.jpg", color_labels=labels)
	mxr.plot_colors_oklch(colors, out_file="images/analogous_00_wheel.png")


def example_compound(seed=None):

	root = OKLCHPalette.new_random(1,seed=None)
	compound = root.compound().adjust_chroma(0.75)
	c5     = root.fade(0.5)
	colors = root.join(compound,c5)
	colors = colors.sort_brightness()
	#colors = colors.make_srgb_safe()
	pretty_preview(colors, "images/compound_00.jpg")
	mxr.plot_colors_oklch(colors, out_file="images/compound_00_wheel.png")





rng = np.random.default_rng()
seed = rng.integers(1, 9999) 
print(f"Example Seed: {seed}")

#example_smooth_luma_00()
#example_smooth_luma_01()
#example_split_complementary_00(seed)
#example_split_complementary_01(seed)
#example_triadic()
#example_square()
example_analogous(seed)
#example_compound(seed)







