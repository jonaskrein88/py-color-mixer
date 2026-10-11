# py-color-mixer
Python utility to create and process color palettes

A collection of color math functions to procedurally create color palettes. This is an extension of the Python script I used for my [procedural graffiti generator](https://www.artstation.com/artwork/DvVJNG). 

It is mostly build around the [OKLCH](https://oklch.com) color space to create palettes based on color harmonies but there are conversions to some other color spaces, like [OKLAB](https://bottosson.github.io/posts/oklab/) for interpolating between colors.

The palettes are built on Numpy and all operations work on whole color palettes. Even single colors are implemented as color palettes.

## usage
To make sure our colors don't compete with one another we can assign explicit roles to them. 
Example palette based on a (slightly shifted) split complement harmony.
```python
roles = [
  Role.DEEP_BASE,
  Role.MID_SUPPORT,
  Role.HERO_ACCENT,
  Role.SECOND_ACCENT,
  Role.HIGHLIGHT
]

root = OKLCHPalette.new_random(1,seed=None)  # -> palette of size 1
sc   = root.split_complement(bias=30)        # -> palette of size 2

colors = ( 
  OKLCHPalette.merge(root, root, sc, root) # -> palette of size 5
  .apply_roles(roles)
  .limit_chroma(0.2)
  .make_srgb_safe()
)

hex_codes = colors.to_hex()   # will handle the srgb conversion
```
![example](images/split_complement_02.jpg)
![example](images/split_complement_02_wheel.png)

## Analogous example
Usually I find analogous palettes difficult to use. But applying the roles sets the lightness and chroma accordingly, so that we still get a functional result.

![example](images/analogous_00.jpg)
![example](images/analogous_00_wheel.png)

## Color Vision deficency emulation
I would recommend using the [colour-science](https://colour.readthedocs.io/en/develop/) module but you can quickly check you palettes against the most common types of color vision deficiency.
- Protanopia / Protanomaly(50%)
- Deuteranopia / Deuteranomaly (50%)
- Tritanopia / Tritanomaly (50%)

The full severity transformations are taken straight from colour-science, the 50% severities are estimates.

A square harmony palette with and without protanopia emulation:

![example](images/square_00_vs_protanopia.png)

## Linear Lightness example

OKLAB and OKLCH are designed to maintain a consistent perceived brightness. This comes in very useful to create colors with a linear lightness gradient.
Example from my [Unity dithering project](https://www.artstation.com/artwork/dyA5g3):

![example](images/smooth_palette_00.jpg)

![example](images/demon_smooth_palette_00.png)
