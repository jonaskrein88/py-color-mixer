
import matplotlib
import matplotlib.pyplot as plt
import math
import numpy as np




# utility class with conversion function.
# TODO rename and/or move into palette parent class
class Color:

    def rgb_to_hsv(rgb):
        r, g, b = rgb
        maxc = max(r, g, b)
        minc = min(r, g, b)
        v = maxc
        if minc == maxc:
            return 0.0, 0.0, v
        s = (maxc - minc) / maxc
        rc = (maxc - r) / (maxc - minc)
        gc = (maxc - g) / (maxc - minc)
        bc = (maxc - b) / (maxc - minc)
        if r == maxc:
            h = bc - gc
        elif g == maxc:
            h = 2.0 + rc - bc
        else:
            h = 4.0 + gc - rc
        h = (h / 6.0) % 1.0
        return h, s, v

    def hsv_to_rgb(hsv):
        h, s, v = hsv
        if s == 0.0:
            return v, v, v
        i = int(h * 6.0)  # XXX assume int() truncates!
        f = (h * 6.0) - i
        p = v * (1.0 - s)
        q = v * (1.0 - s * f)
        t = v * (1.0 - s * (1.0 - f))
        i = i % 6
        if i == 0:
            return v, t, p
        if i == 1:
            return q, v, p
        if i == 2:
            return p, v, t
        if i == 3:
            return p, q, v
        if i == 4:
            return t, p, v
        if i == 5:
            return v, p, q

    @staticmethod
    def rgb_to_oklab(rgb):
        r, g, b = rgb
        l = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
        m = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
        s = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b
        l = l**(1 / 3)
        m = m**(1 / 3)
        s = s**(1 / 3)
        return (0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s,
                1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s,
                0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s)

    @staticmethod
    def oklab_to_rgb(lab):
        l, a, b = lab
        l_ = l + 0.3963377774 * a + 0.2158037573 * b
        m_ = l - 0.1055613458 * a - 0.0638541728 * b
        s_ = l - 0.0894841775 * a - 1.2914855480 * b

        l = l_ * l_ * l_
        m = m_ * m_ * m_
        s = s_ * s_ * s_

        return (+4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
                -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
                -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s)

    @classmethod
    def rgb_to_oklch(cls, rgb):
        return cls.oklab_to_oklch(cls.rgb_to_oklab(rgb))

    @classmethod
    def oklch_to_rgb(cls, lch):
        return cls.oklab_to_rgb(cls.oklch_to_oklab(lch))

    @staticmethod
    def oklab_to_oklch(lab):
        l, a, b = lab
        c = math.sqrt(a**2 + b**2)
        h = float('nan') if (abs(a) < 0.0002 and abs(b) < 0.0002) else ((
            (math.atan2(b, a) * 180) / math.pi % 360) + 360) % 360
        return (l, c, h)

    @staticmethod
    def oklch_to_oklab(lch):
        a = 0 if math.isnan(
            lch[2]) else lch[1] * math.cos(lch[2] * math.pi / 180)
        b = 0 if math.isnan(
            lch[2]) else lch[1] * math.sin(lch[2] * math.pi / 180)
        return (lch[0], a, b)

    @staticmethod
    def clampRGB(rgb):
        return (min(1, max(0, rgb[0])), min(1, max(0, rgb[1])),
                min(1, max(0, rgb[2])))


    @classmethod
    def rgb_to_hex(cls, rgb):
        rgb = cls.clampRGB(rgb)
        r = round(rgb[0] * 255)
        g = round(rgb[1] * 255)
        b = round(rgb[2] * 255)
        return "#{:02x}{:02x}{:02x}".format(r, g, b)

    @staticmethod
    def hex_to_rgb(h):
        h = h.lstrip('#')
        return tuple(float(int(h[i:i + 2], 16)) / 255.0 for i in (0, 2, 4))

    @staticmethod
    def srgb_to_linear_rgb(srgb):
        r, g, b = srgb

        def f(x):
            if (x >= 0.04045): return ((x + 0.055) / (1 + 0.055))**2.4
            else: return x / 12.92

        return (f(r), f(g), f(b))

    @staticmethod
    def linear_rgb_to_srgb(rgb):
        r, g, b = rgb

        def f(x):
            if (x >= 0.0031308): return 1.055 * (x**(1.0 / 2.4)) - 0.055
            else: return 12.92 * x

        return (f(r), f(g), f(b))

    @staticmethod
    def rgb_to_luma(rgb):
        r, g, b = rgb
        l = (0.2126 * r) + (0.7152 * g) + (0.0722 * b)
        return l

    @staticmethod
    def clamp(rgb):
        r, g, b = rgb
        return (min(1, max(0, r)), min(1, max(0, g)), min(1, max(0, b)))

    @staticmethod
    def rgb_to_xyY(rgb):
        '''
        expects linear 0-1 rgb
        '''
        r, g, b = rgb
        rgb_to_xyz_matrix = np.array([[0.4124, 0.3576, 0.1805],
                                       [0.2126, 0.7152, 0.0722],
                                       [0.0193, 0.1192, 0.9505]])

        rgb_vector = np.array([r, g, b])

        # convert to XYZ tristimulus values
        xyz_vector = np.dot(rgb_to_xyz_matrix, rgb_vector)
        x, y, z = xyz_vector[0], xyz_vector[1], xyz_vector[2]

        # handle black
        sum_xyz = x + y + z
        if sum_xyz == 0:
            return (0.0, 0.0)

        # XYZ to xy 
        x_chrom = x / sum_xyz
        y_chrom = y / sum_xyz
        return (x_chrom, y_chrom, y)

    @classmethod
    def rgb_to_xy(cls, rgb):
        (x, y, _) = cls.rgb_to_xyY(rgb)
        return (x, y)

    @staticmethod
    def lerp_float(a,b,t):
        return b*t + a *(1.0-t)







class ColorPalette:

    def __init__(self, npArray, name=None):

        # handle rank
        # single channel shape (x,)
        # three channel  shape (x,3)
        # TODO single rank is not really idiomatic for most colors
        if len(npArray.shape) == 1:
            self.colors = np.stack((npArray, npArray, npArray)).T
        else:
            self.colors = npArray

        self.name = name


    def __repr__(self):
        s = f"{self.__class__.__name__} Size:{self.colors.shape}"
        for c in self.colors:
            s += str(c)
        return s

    def __getitem__(self, index):
        '''there is no concept of single colors so we return a color palette containing only one color'''
        color_tuple = self.colors[index]
        return self._as_self(np.array([color_tuple]))

    def __iter__(self):
        return iter(self.colors)

    def __len__(self):
        return self.colors.shape[0]

    @classmethod
    def from_color(cls,color):
        ''' this abstract methods relies on the individual conversion functions '''
        raise NotImplementedError

    @classmethod
    def _as_self(cls, colors):
        ''' wraps the color array in the current class '''
        return cls(colors)

    def luma(self):
        rgb = self.to_rgb()
        return [Color.rgb_to_luma(x) for x in rgb.colors]

    @classmethod
    def from_channels(cls, a, b=None, c=None, name=None):
        abc = np.stack((a, b, c)).T
        return cls(abc, name=name)

    @classmethod
    def from_channel(cls, channel):
        ''' needs to be implemented by the color models individually '''
        raise NotImplementedError

    def channel_mix(self, other, index):
        ''' copies channel of color a and pastes it at the same index in color b'''
        colors = np.copy(self.colors)
        colors[:,index] = other.get_channel(index)
        return self._as_self(colors)

    def clamp(self):
        current_class = type(self)
        return current_class(self.map(Color.clamp))

    def get_channel(self, index=0):
        ''' return an array of only the indexed channel values '''
        return self.colors[:, index]

    def join(self, *others):
        ''' convert other palettes to this ones color mode and combine to new one ''' 
        colors = np.copy(self.colors)
        for other in others:
            other = self.from_color(other)
            colors = np.concatenate((colors, other.colors));
        return self._as_self(colors)


    def sort(self, fn):
        raise NotImplementedError
        # TODO


    @classmethod
    def interpolate(cls, a, b, t: float):
        ''' 
        Convert colors to this color mode and return linear interpolated color 
        Best use OKLAB for this
        '''
        a = cls.from_color(a)
        b = cls.from_color(b)
        result = a.colors + t * (b.colors - a.colors)
        return cls._as_self(result)


    def resize(self, num_new_colors: int):
        '''

        extends or shrinks the color palette to the input size
        with new colors interpolated between the first and last.

        Will interpolate the channels individually in the current color space,
        so the choice of color space matters.

        To keep the original colors in addition to new ones, the new size needs to be:
        original_size + num_inbetweens * (original_size-1)

        '''

        original_colors = self.colors
        xp = np.arange(len(original_colors))
        x = np.linspace(0, len(original_colors) - 1, num_new_colors)
        interpolated_channels = [
            np.interp(x, xp, original_colors[:, i])
            for i in range(original_colors.shape[1])
        ]

        # np.vstack() combines the 1D arrays into a 2D array.
        interpolated_colors = np.vstack(interpolated_channels).T

        # cast to palette of source type
        current_class = type(self)
        return current_class(interpolated_colors)

    def map(self, fn):
        '''
        utility function to map a function over the colors.
        Returns just the color data - needs to be wrapped in a Class
        '''
        return np.array([fn(x) for x in self.colors])







class SRGBPalette(ColorPalette):

    @classmethod
    def from_hex(cls, *hexes):
        rgb = [Color.hex_to_rgb(x) for x in hexes]
        return cls(np.array(rgb))

    @classmethod
    def from_color(color):
        ''' new sRGB from an unknown Color Class '''
        return color.to_rgb().to_srgb()

    @classmethod
    def from_channel(cls, channel):
        ''' Monochrome sRGB '''
        colors = np.stack((channel, channel, channel)).T
        return SRGBPalette(colors)

    def to_rgb(self):
        return RGBPalette(self.map(Color.srgb_to_linear_rgb))

    def to_hex(self):
        return [Color.rgb_to_hex(x) for x in self.colors]

    def to_xy(self):
        return self.to_rgb().to_xy()

    def to_srgb(self):
        return self


    @staticmethod
    def from_oklch(oklch):
        return oklch.to_srgb()





class RGBPalette(ColorPalette):


    def __add__(self, other):
        if isinstance(other, ColorPalette):
            return RGBPalette(np.add(self.colors, other.colors))
        return RGBPalette(self.colors + other)

    def __mul__(self, value):
        return RGBPalette(self.colors * value)

    @classmethod
    def from_hex(cls, *hexes):
        return SRGBPalette.from_hex(*hexes).to_rgb()

    @classmethod
    def from_color(cls,color):
        ''' new Linear RGB from an unknown Color Class ''' 
        return color.to_rgb()

    @classmethod
    def from_channel(cls, channel):
        ''' Monochrome Linear RGB '''
        colors = np.stack((channel, channel, channel)).T
        return RGBPalette(colors)

    #@staticmethod
    #def from_oklch(oklch):
    #    return oklch.to_rgb()

    def gamma(self, value):
        return RGBPalette(self.map(lambda x: pow(x, value)))

    def to_oklch(self):
        return OKLCHPalette(self.map(Color.rgb_to_oklch))

    def to_oklab(self):
        return OKLABPalette(self.map(Color.rgb_to_oklab))

    def to_hsv(self):
        return HSVPalette(self.map(Color.rgb_to_hsv))

    def to_srgb(self):
        return SRGBPalette(self.map(Color.linear_rgb_to_srgb))

    def to_luma(self):
        return RGBPalette(self.map(Color.rgb_to_luma))

    def to_rgb(self):
        return self

    def to_hex(self):
        return self.to_srgb().to_hex()

    def to_xyY(self):
        return np.array([Color.rgb_to_xyY(x) for x in self.colors])

    def to_xy(self):
        return [Color.rgb_to_xy(x) for x in self.colors]

    def invert(self):
        colors = self.map(lambda x: (1.0-x[0], 1.0-x[1], 1.0-x[2]))
        return RGBPalette(colors)









class OKLCHPalette(ColorPalette):

    @classmethod
    def from_color(cls,color):
        ''' new OKLCH from an unknown Color Class ''' 
        return color.to_oklch()

    @classmethod
    def new_random(cls, num_colors, min_luma=0, max_luma=1, min_chroma=0, max_chroma=1):
        rng = np.random.default_rng()
        hue       = rng.uniform(0.0, 360.0, num_colors)
        lightness = rng.uniform(min_luma,   max_luma,   num_colors)
        chroma    = rng.uniform(min_chroma, max_chroma, num_colors)
        return OKLCHPalette.from_channels(lightness, chroma, hue)


    def to_oklch(self):
        return self

    def to_oklab(self):
        return OKLABPalette(self.map(Color.oklch_to_oklab))

    def to_rgb(self):
        return RGBPalette(self.map(Color.oklch_to_rgb))

    def to_srgb(self):
        return self.to_rgb().to_srgb()

    def to_hex(self):
        return self.to_srgb().to_hex()

    def get_luma(self):
        return self.get_channel(0)

    def get_chroma(self):
        return self.get_channel(1)

    def get_hue(self):
        return self.get_channel(2)

    def get_hue_normalized(self):
        return self.get_channel(2)/360.0


    # doesn't guarantee valid srgb results, so kinda pointless
    '''
    def make_safe_chroma(self):    
        lightness = self.get_luma()
        max_safe_chroma = np.where(
            lightness <= 0.65,
            lightness * 0.28,           # Dark segment clamp
            (1.0 - lightness) * 0.52    # Bright segment clamp
        )
        hue = self.get_hue()
        return OKLCHPalette.from_channels(lightness, max_safe_chroma, hue)
    '''


    def make_srgb_safe(self):    
        '''
        keeps lightness and hue 
        tries reducing chroma until it fits perfectly inside sRGB.
        '''
        def is_srgb_legal(rgb):
            '''checks if an sRGB color is in range 0-1'''
            if rgb[0] < -0.001 or rgb[0] > 1.001: return False
            if rgb[1] < -0.001 or rgb[1] > 1.001: return False
            if rgb[2] < -0.001 or rgb[2] > 1.001: return False
            return True

        def fn(lch):
            # check if the current chroma is already safe
            rgb = Color.linear_rgb_to_srgb(Color.oklch_to_rgb(lch))

            if is_srgb_legal(rgb):
                return lch
                
            (l,c,h) = lch
            low_c = 0.0
            high_c = c
            best_c = 0.0
            best_rgb = np.array([0.0, 0.0, 0.0])
            
            # 16 iterations of trial and error
            for _ in range(16):
                mid_c = (low_c + high_c) / 2.0
                test_rgb = Color.linear_rgb_to_srgb(Color.oklch_to_rgb((l, mid_c, h)))
                
                if is_srgb_legal(test_rgb):
                    best_c = mid_c
                    best_rgb = test_rgb
                    low_c = mid_c  # increase to see if we can get more vividness
                else:
                    high_c = mid_c # otherwise reduce
                    
            return (l, best_c, h)
        return OKLCHPalette(self.map(fn))




    def shift_hue(self,offset):
        def fn(lch):
            h = (lch[2] + offset) % 360
            return (lch[0], lch[1], h)
        return OKLCHPalette(self.map(fn))

    def exposure(self, x):
        ''' multiply luma by x '''
        colors = self.map(lambda c : (c[0]*x,c[1],c[2]))
        return OKLCHPalette(colors)

    def adjust_chroma(self, x):
        ''' multiply chroma by x '''
        colors = self.map(lambda c : (c[0],c[1]*x,c[2]))
        return OKLCHPalette(colors)

    def adjust_saturation(self, x):
        ''' just an alias for adjust_chroma '''
        return self.adjust_chroma(x)

    def whiten(self, t:float):
        ''' fades to white: increases luma, reduces saturation, leaves hue as is '''
        def fn(lch):
            luma   = Color.lerp_float(lch[0],1.0,t)
            chroma = Color.lerp_float(lch[1],0.0,t)
            return(luma,chroma,lch[2])
        return OKLCHPalette(self.map(fn))




    # the harmonic functions
    # undecided if the functions should return the input color
    def complement(self):
        return self.shift_hue(-180)


    def triadic(self, keep_input=True):
        a =  self.shift_hue(120)
        b =  self.shift_hue(-120)
        if keep_input: return self.join(a.join(b))
        return a.join(b)

    def square(self):
        ''' aka tetradic '''
        a =  self.shift_hue(90)
        b =  self.shift_hue(180)
        c =  self.shift_hue(270)
        return self.join(a,b,c)

    def analogous(self, num=5, stepsize=20):
        self = self.shift_hue(float(num)/2.0*-stepsize)
        out = self
        for i in range(1,num):
            x = self.shift_hue(i*stepsize)
            out = out.join(x)
        return out

    def split_complement(self,spread=40, bias=0):
        ''' shorthand for complement + 2 analogous with optional shift'''
        compl = self.complement().shift_hue(bias)
        return compl.analogous(2,spread)


    # not sure id ever need this
    #def shift_chroma(self,offset):
    #    fn = lambda color: (color[0], min(1,max(0,color[1])) + offset, color[2])
    #    return OKLCHPalette(self.map(fn))


    def split(self, angle=20):
        x = [self.__split(x,angle) for x in self.colors]
        return OKLCHPalette(np.array(x).reshape((-1,3)))










class OKLABPalette(ColorPalette):

    @classmethod
    def from_color(cls,color):
        ''' new OKLAB from an unknown Color Class ''' 
        return color.to_oklch().to_oklab()

    def to_oklab(self):
        return self

    def to_oklch(self):
        return OKLCHPalette(self.map(Color.oklab_to_oklch))

    def to_rgb(self):
        return RGBPalette(self.map(Color.oklab_to_rgb))

    def to_hex(self):
        return self.to_rgb().to_hex()

    def to_srgb(self):
        return self.to_rgb().to_srgb()





class HSVPalette(ColorPalette):

    @classmethod
    def from_color(cls,color):
        ''' new HSV from an unknown Color Class ''' 
        return color.to_rgb().to_hsv()


    def to_rgb(self):
        return RGBPalette(self.map(Color.hsv_to_rgb))

    def to_srgb(self):
        return self.to_rgb().to_srgb()

    def to_hex(self):
        return self.to_srgb().to_hex()








def plot_XYY(palettes):
    '''
    Plots the colors in a CIE X and CIE Y diagram
    and perceived brightness in it's own graph.
    With sRGB primaries as reference

    '''
    fig = plt.figure()

    ax = fig.add_subplot(121)
    ax_luma = fig.add_subplot(122)


    srgb_primaries = [(0.640, 0.330), (0.300, 0.600), (0.150, 0.060)]
    rgb_colors = [(1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)]
    srgb_triangle = matplotlib.patches.Polygon(srgb_primaries,
                                               facecolor='none',
                                               edgecolor='grey',
                                               linestyle=':',
                                               zorder=1)

    sx, sy = zip(*srgb_primaries)

    ax.add_patch(srgb_triangle)
    #ax.scatter(sx,sy,c=rgb_colors) # add the color dots at the triangle
    #ax.set_xlim(0, 0.8)
    #ax.set_ylim(0, 0.9)
    ax.set_xlabel('CIE x')
    ax.set_ylabel('CIE y')
    ax.set_title('Chromaticity')
    ax.grid(True)
    #ax.set_aspect('equal') 

    for palette in palettes:
        palette = palette.to_rgb()
        x, y = zip(*palette.to_xy())
        #p, = ax.plot(x, y, linewidth=1.0)
        #p.set_linestyle(':')
        ax.scatter(x, y, c=palette.to_srgb().clamp().colors)

        # the luma plot
        x = np.arange(0.0, 1.0, 1.0 / len(palette))
        #y = palette.to_xyY()[:, 2]
        y = palette.to_oklab().colors[:,0]
        ax_luma.scatter(x, y, c=palette.to_srgb().clamp().colors)
        p, = ax_luma.plot(x, y, linewidth=1.0)
        p.set_linestyle(':')
        #ax_luma.set_title('Y Stimulus')
        ax_luma.set_title('Perceived Brightness')


    plt.show()



# TODO make nice
def showPalettes(*palettes):

    fig = plt.figure()
    size = 20
    ax = fig.add_subplot(111)
    for y, p in enumerate(palettes):
        if p.name != None:
            matplotlib.pyplot.text(p.colors.shape[0] * size, 300 - y * size,
                                   p.name)

        p = p.to_hex()
        for x, c in enumerate(p):
            pos = (x * size, 300 - y * size)
            rect = matplotlib.patches.Rectangle(pos, size, size, color=c)
            ax.add_patch(rect)

    plt.xlim([-0, 400])
    plt.ylim([-0, 400])
    plt.show()


