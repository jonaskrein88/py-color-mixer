
from ColorMixer import RGBPalette, OKLCHPalette, HSVPalette, OKLABPalette
import ColorMixer as mxr

from PIL import Image, ImageDraw, ImageFont
import numpy as np
import random
import re

import xml.etree.ElementTree as ET
from itertools import cycle


TEMPLATE = "images/color_template.svg"

TARGET_NAMES = ['background', 'midtone', 'main accent', 'secondary accent', 'highlight']

TARGET_ROLES = [
	mxr.Role.DEEP_BASE,
	mxr.Role.MID_SUPPORT,
	mxr.Role.HERO_ACCENT,
	mxr.Role.SECOND_ACCENT,
	mxr.Role.HIGHLIGHT]


# little preview image with hex codes
def make_color_swatches(palette, image_width=None, image_height=800, title=None, sub_title=None):

	num_colors = len(palette)	

	column_width = 200 if not image_height else image_width/num_colors
	image_width = image_width or column_width * num_colors

	image_width = int(image_width)
	image_height = int(image_height)

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
		if palette.labels:
			label_text = palette.labels[i]
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

	return img


def pretty_preview(*palettes, image_width=None, out_file=None, show=True):

	images = []
	height = 800/len(palettes)
	for palette in palettes:
		img = make_color_swatches(palette, image_width=1200, image_height=height)
		images.append(np.asarray(img))

	stitched = np.vstack(images)

	out_image = Image.fromarray(stitched)

	if out_file:
		out_image.save(out_file)

	if show:
		out_image.show()






def recolor_svg(input_svg_path, output_svg_path, fill_colors):
    # Map normalized 6-digit lower-case hex strings to your index requirements
    COLOR_MAP = {'#ff0000': 0, '#00ff00': 1, '#0000ff': 2, '#00ffff': 3, '#ff00ff': 4, '#ffff00': 5}
    
    tree = ET.parse(input_svg_path)
    root = tree.getroot()
    
    # Configure required namespaces
    for prefix, uri in [('', "http://www.w3.org/2000/svg"), ('xlink', "http://www.w3.org/1999/xlink")]:
        ET.register_namespace(prefix, uri)

    for elem in root.iter():
        tag = elem.tag.split('}')[-1].lower()
        
        if tag in {'path', 'rect', 'circle', 'ellipse', 'line', 'polyline', 'polygon'}:
            style_str = elem.get('style', '')
            match = re.search(r'(?:^|;)\s*fill\s*:\s*([^;! \s]+)', style_str)
            raw_color = (match.group(1) if match else elem.get('fill', '')).lower()

            # Expand 3-digit short hex formats (e.g., #f00 -> #ff0000)
            if re.match(r'^#[0-9a-f]{3}$', raw_color):
                raw_color = '#' + ''.join(c * 2 for c in raw_color[1:])

            if raw_color in COLOR_MAP and COLOR_MAP[raw_color] < len(fill_colors):
                new_color = fill_colors[COLOR_MAP[raw_color]]
                elem.attrib.pop('class', None)
                elem.set('style', re.sub(r'fill\s*:\s*[^;]+', f'fill: {new_color}', style_str) if match else f"fill: {new_color};")
                elem.set('fill', new_color)
                
        elif tag in {'text', 'tspan'}:
            elem.attrib.pop('class', None)
            elem.set('style', "fill: #1A1A1A; stroke: none;")

    tree.write(output_svg_path, encoding='utf-8', xml_declaration=True)







def create_previews(file):
	def _decorator(f):
		def _wrapper(*args):
			colors = f(*args)
			pretty_preview(colors, out_file=f"{file}.png")
			recolor_svg(TEMPLATE, f"{file}_example.svg", colors.to_hex())
			mxr.plot_colors_oklch(colors, out_file=f"{file}_wheel.png")
			return colors
		return _wrapper
	return _decorator











def example_smooth_luma() -> OKLABPalette:
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

	final = final.linearize_lightness(min=0.05, max=0.9)
	final = final.limit_chroma(0.17)
	final = final.make_srgb_safe()
	rgb = final.to_srgb().clamp()
	#mxr.plot_XYY([rgb])
	#mxr.plot_perceived_brightness(rgb)
	#pretty_preview(rgb, out_file="images/smooth_palette_00.png")
	return rgb




@create_previews("images/triadic")
def create_triadic(seed=None) -> OKLCHPalette:

	root = OKLCHPalette.new_random(1,seed=seed)
	triad = root.generate_triadic()

	# try and auto asign the roles optimally based on hue
	# use base as highlight
	sorted_colors = root.join(triad).sort_for_roles()

	base 		 = sorted_colors[0]
	mid  		 = sorted_colors[0]
	heroAccent   = sorted_colors[1]
	secondAccent = sorted_colors[2]
	highlight    = sorted_colors[0]

	colors = (
		base.join(mid,secondAccent, heroAccent, highlight)
		.apply_roles(TARGET_ROLES, seed=seed)
	)
	colors.labels = TARGET_NAMES
	return colors




@create_previews("images/analogous_palette")
def create_analogous(seed=None) -> OKLABPalette:
	root = OKLCHPalette.new_random(1,seed=seed)
	colors = root.generate_analogous(5,stepsize=20).sort_for_roles()
	colors = colors.apply_roles(TARGET_ROLES, seed=seed).limit_chroma(0.2)
	colors.labels = TARGET_NAMES
	return colors




@create_previews("images/analogous_complement")
def create_analogous_complementary(seed=None) -> OKLCHPalette:
	root = OKLCHPalette.new_random(1,seed=seed)
	comp = root.complement(bias=0).generate_analogous(4,stepsize=25)
	colors = (
		OKLCHPalette.merge(comp[0],comp[1],root,comp[2], comp[3])
		.apply_roles(TARGET_ROLES, seed=seed)
		.make_srgb_safe()
	)
	colors.labels = TARGET_NAMES
	return colors



@create_previews("images/split_complement")
def create_split_complementary(seed=None) -> OKLCHPalette:

	root = OKLCHPalette.new_random(1,seed=seed)                   # -> palette of size 1
	sc   = root.generate_split_complement(bias=0, stepsize=35)    # -> palette of size 2
	colors = ( 
		OKLCHPalette.merge(root, sc[0], root, sc[1], sc[1]) # shuffle to taste -> palette of size 5
		.apply_roles(TARGET_ROLES,seed=seed)
		.make_srgb_safe()
	)
	colors.labels = TARGET_NAMES
	return colors



@create_previews("images/shades_quadrant")
def create_shades_quadrant(seed=None) -> OKLCHPalette:

	root = OKLCHPalette.new_random(1,seed=seed+123)
	shades = (
		root.shift_hue(90)
		.repeat(4)
	)

	colors = (
		OKLCHPalette.merge(shades,root)
		.apply_roles(TARGET_ROLES,seed=seed)
		.make_srgb_safe()
	)
	colors.labels = TARGET_NAMES
	return colors



@create_previews("images/complement_quadrant")
def create_complement_quadrant(seed=None) -> OKLCHPalette:

	root = OKLCHPalette.new_random(1,seed=seed)
	quadrant    = root.shift_hue(90)
	complement  = root.complement()

	colors = (
		OKLCHPalette.merge(root,root,complement,quadrant,quadrant)
		.apply_roles(TARGET_ROLES,seed=seed)
		.limit_chroma(0.2)
	)
	colors.labels = TARGET_NAMES
	return colors




@create_previews("images/shades_palette")
def create_shades(seed=None) -> OKLCHPalette:
	''' there are several way to create shades'''
	root = OKLCHPalette.new_random(1,seed=seed)
	#colors = root.generate_monochromatic_shades(5).sort_brightness()
	#colors = root.generate_hue_shifted_shades(5).sort_brightness()
	colors = (
		root.repeat(5)
		.apply_roles(TARGET_ROLES, seed=seed)
		.limit_chroma(0.2)
		.sort_brightness()
	)
	colors.labels = TARGET_NAMES
	return colors




@create_previews("images/compound")
def create_compound(seed=None) -> OKLCHPalette:
	root = OKLCHPalette.new_random(1,seed=seed)
	compound = root.generate_compound()
	colors   = (
		root.join(compound,root)
		.apply_roles(TARGET_ROLES)
		.limit_chroma(0.15)
	)
	colors.labels = TARGET_NAMES
	return colors




@create_previews("images/interpolated_lab")
def create_interpolated(seed=None) -> OKLABPalette:
	root = OKLCHPalette.new_random(1, seed=seed)
	other = root.complement(bias=40)
	colors = OKLABPalette.merge(root,other).resize(5).linearize_lightness()
	colors.labels = TARGET_NAMES
	return colors








def create_square(seed=None) -> OKLABPalette:
	root = OKLCHPalette.new_random(1,seed=seed)
	square = root.generate_square()
	colors = root.join(square).sort_for_roles()

	# appending the root again at the end to become our highlight color
	colors = colors.join(colors[0]).apply_roles(TARGET_ROLES)
	colors.labels = TARGET_NAMES
	return colors

def example_square_with_protanopia(seed=None):
	colors = create_square(seed)
	protanopia = colors.simulate_cvd(mxr.CVDType.PROTANOPIA)
	pretty_preview(colors, protanopia, out_file="images/square.png")
	recolor_svg(TEMPLATE, "images/square_example.svg", colors.to_hex())
	mxr.plot_colors_oklch(colors, out_file="images/square_wheel.png")
	recolor_svg(TEMPLATE, "images/square_protanopia_example.svg", protanopia.to_hex())
	#mxr.plot_perceived_brightness(colors)
	#mxr.plot_colors_oklch(colors,out_file="images/split_complement_00_wheel.png")
	#mxr.plot_XYY([colors])












rng = np.random.default_rng()
seed = rng.integers(1, 1234) 
print(f"Example Seed: {seed}")



# the seeds are the ones to reproduce the example images

#create_interpolated(seed)             # 1077
#create_shades(seed) 				   # 317
#create_analogous(seed)                # 774
#create_split_complementary(seed)      # 790
#create_analogous_complementary(seed)  # 322
#create_triadic(seed) 				   # 787
#create_compound(seed)                 # 1219
#create_shades_quadrant(seed)          # 126
#create_complement_quadrant(seed)      # 466
#example_square_with_protanopia(seed)  # 65


