# lights.py - part 2 from Tony Dicola - Adafruit
# 2016-1204 PePo new, copied/adopted from
# part 2: 
#   https://gist.github.com/tdicola/4d1788a415aaeb32c7f4dddbed1c3327
# part 1:
#   https://gist.github.com/tdicola/55c7ba333933bccaa75526a07b266bf2
# ------------------
import machine
import neopixel
import utime
import ujson

# standard configuration that never changes
# NodeMCU: neopixels attached to pin D7 (GPIO13)
PIXEL_PIN = machine.Pin(13, machine.Pin.OUT)
# number of neopixels
#PIXEL_COUNT = 64  # 8x8 pixels
PIXEL_COUNT = 24  # 24-pixels ring
#PIXEL_COUNT = 8  # 8-pixels ring
#PIXEL_COUNT = 8  # stick 1*8

# dynamic configuration than can be changed
# lateron replaced by reading the data from config.json
# config = {
#     'colors': [(0,0,255), (16,0,128), (32,0,64), (64,0,32), (128,0,16), (255,0,0)],
#     'period_ms': 500,
#     'mirror_colors': True,
#     'animation': 'foo'
# }

# ramp of alternate colors...
# 2016-1204 part 2 and 3: controlled by a webpage!
#colors = [(0,255,0), (16,128,0), (32,64,0), (64,32,0), (128,16,0), (255,0,0)]
# ramp of colors Blue, Green and Red
#colors = [(0,0,255), (0,255,0), (255,0,0)]

# mirror the colors to make a ramp up and ramp down with no repeated colors.
def mirror(values):
    # Add the input values in reverse order to the end of the array
    # However slice off the very first and very last item (the [1:1] syntax)
    # to prevent the first and last values from repeating.
    # for example an input of:
    # [1, 2, 3]
    # returns:
    # [1, 2, 3, 2]
    # instead of returning:
    # [1, 2, 3, 3, 2, 1]
    # which would duplicate 3 and 1 as you loop through the elements
    values.extend(list(reversed(values))[1:-1])
    return values

# Linear interpolation helper:
def _lerp(x, x0, x1, y0, y1):
    return y0 + (x - x0) * ((y1 - y0)/(x1 - x0))

# Animation functions
# blank the neopixels
def blank(config, np, pixel_count):
    np.fill((0,0,0))
    np.write()

# solid animation
def solid(config, np, pixel_count):
    colors = config['colors']
    elapsed = utime.ticks_ms() // config['period_ms']
    current = elapsed % len(colors)
    np.fill(colors[current])
    np.write()

# chasing animation
def chase(config, np, pixel_count):
    colors = config['colors']
    elapsed = utime.ticks_ms() // config['period_ms']
    for i in range(pixel_count):
        current = (elapsed+i) % len(colors)
        np[i] = colors[current]
    np.write()

# smooth animation
def smooth(config, np, pixel_count):
    # Smooth pulse of all pixels at the same color.  Interpolates inbetween colors
    # for smoother animation.
    colors = config['colors']
    period_ms = config['period_ms']
    ticks = utime.ticks_ms()
    step = ticks // period_ms
    offset = ticks % period_ms
    color0 = colors[step % len(colors)]
    color1 = colors[(step+1) % len(colors)]
    color = (int(_lerp(offset, 0, period_ms, color0[0], color1[0])),
             int(_lerp(offset, 0, period_ms, color0[1], color1[1])),
             int(_lerp(offset, 0, period_ms, color0[2], color1[2])))
    np.fill(color)
    np.write()

# extra helper function to blank pixels to be called on the repl-interface
def off():
    np.fill((0,0,0))
    np.write()

# Setup code #
# Load configuration from config JSON file.
# using Python context manager
with open('config.json', 'r') as infile:
    config = ujson.load(infile)

# config: mirror_colors
if (config['mirror_colors']):
    config['colors'] = mirror(config['colors'])

# config: pixels - initialize the neopixels and turn them off
numberOfPixels = config['pixels']
print(numberOfPixels)
np = neopixel.NeoPixel(PIXEL_PIN, numberOfPixels)
#np = neopixel.NeoPixel(PIXEL_PIN, PIXEL_COUNT)

np.fill((0,0,0))
np.write()

# determine the animation function to call
#if config['animation'] == 'solid':
#    animation = solid
#elif config['animation'] == 'chase':
#    animation = chase
#else:
#    animation = blank
animation = globals().get(config['animation'], blank)

# Main loop
while True:
    #animation(config, np, PIXEL_COUNT)
    animation(config, np, numberOfPixels)
    utime.sleep(0.01)
