


from ColorMixer import RGBPalette, OKLCHPalette, HSVPalette, OKLABPalette
import ColorMixer as mxr
import numpy as np

from PIL import Image, ImageDraw, ImageFont






# little preview image with hex codes
# TODO add label
def pretty_preview(palette, out_file=None, show=True):

	num_colors = len(palette)
	column_width = 200
	image_height = 800
	image_width = column_width * num_colors

	img = Image.new("RGB", (image_width, image_height), "#FFFFFF")
	draw = ImageDraw.Draw(img)


	try:
	    font_hex = ImageFont.truetype("arialbd.ttf", 24)
	except IOError:
	    font_hex = ImageFont.load_default()
	    font_name = ImageFont.load_default()

	hexes = palette.to_srgb().to_hex()
	lumas = palette.luma()

	for i, colorHex in enumerate(hexes):

	    x_start = i * column_width
	    x_end = x_start + column_width
	    
	    draw.rectangle([x_start, 0, x_end, image_height], fill=colorHex)
	    
	    hex_text = colorHex.replace("#", "").upper()
	    hex_text_x = x_start + (column_width - draw.textlength(hex_text, font=font_hex)) / 2

	    text_color = '#dddddd' if lumas[i]<0.5 else '#444444'

	    draw.text((hex_text_x, image_height - 70), hex_text, fill=text_color, font=font_hex)

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

	final = final.make_safe_chroma()
	rgb = final.to_srgb().clamp()
	mxr.plot_XYY([rgb])
	pretty_preview(rgb,"images/smooth_palette_00.jpg")




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






def example_triadic():

	'''
	create a small triadic harmony,
	with two brighter variants
	'''
	root = OKLCHPalette.new_random(1)

	triad = root.triadic()
	c4 = triad[0].whiten(0.75) 
	c5 = triad[1].whiten(0.9) 

	colors = triad.join(c4,c5)
	pretty_preview(colors, "images/triadic_00.jpg")
	#mxr.plot_XYY([colors])






def example_split_complementary():
	''' create a small color based on a split complementary harmony '''

	root = OKLCHPalette.new_random(1)
	split = root.split_complement(bias=10)
	a = split[0]
	b = split[1].exposure(1.125)
	c = b.whiten(0.75)
	d = root.whiten(0.7)

	final = root.join(a,b,c,d)
	final = final.make_srgb_safe()
	pretty_preview(final, "images/split_complement_00.jpg")
	#mxr.plot_XYY([colors])








#example_smooth_luma_00()
#example_smooth_luma_01()
#example_split_complementary()
example_triadic()






