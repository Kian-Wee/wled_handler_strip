''' WLED effects '''

import requests
from eventmanager import Evt
from led_event_manager import LEDEffect, LEDEvent, Color, ColorVal, ColorPattern
import gevent
from RHUI import UIField, UIFieldType
import logging

logger = logging.getLogger(__name__)

JSON_IP = 'http://192.168.1.224/json/state'
WLED_IPS=['http://192.168.1.156']


#Query for the number of leds on a particular strip
def wled_num_of_leds(IP):
    url=str(IP)+"/json/info"
    response = requests.get(url)
    return int(response["leds"]["count"])

def wled_equiv_color(color):
    if color == ColorVal.NONE:
        return '{"on":true,"v":true,"seg":[{"col":[[0, 0, 0]],"bri":255}]}'
    elif color == ColorVal.BLUE:
        return '{"on":true,"v":true,"seg":[{"col":[[0, 31, 255]],"bri":255}]}'
    elif color == ColorVal.CYAN:
        return '{"on":true,"v":true,"seg":[{"col":[[0, 255, 255]],"bri":255}]}'
    elif color == ColorVal.DARK_ORANGE:
        return '{"on":true,"v":true,"seg":[{"col":[[255, 63, 0]],"bri":255}]}'
    elif color == ColorVal.DARK_YELLOW:
        return '{"on":true,"v":true,"seg":[{"col":[[250, 210, 0]],"bri":255}]}'
    elif color == ColorVal.GREEN:
        return '{"on":true,"v":true,"seg":[{"col":[[0,255,0]],"bri":255}]}'
    elif color == ColorVal.LIGHT_GREEN:
        return '{"on":true,"v":true,"seg":[{"col":[[127,255,0]],"bri":255}]}'
    elif color == ColorVal.ORANGE:
        return '{"on":true,"v":true,"seg":[{"col":[[255,128,0]],"bri":255}]}'
    elif color == ColorVal.MINT:
        return '{"on":true,"v":true,"seg":[{"col":[[63,255,63]],"bri":255}]}'
    elif color == ColorVal.PINK:
        return '{"on":true,"v":true,"seg":[{"col":[[255,0,127]],"bri":255}]}'
    elif color == ColorVal.PURPLE:
        return '{"on":true,"v":true,"seg":[{"col":[[127,0,255]],"bri":255}]}'
    elif color == ColorVal.RED:
        return '{"on":true,"v":true,"seg":[{"col":[[255,0,0]],"bri":255}]}'
    elif color == ColorVal.SKY:
        return '{"on":true,"v":true,"seg":[{"col":[[0,191,255]],"bri":255}]}'
    elif color == ColorVal.WHITE:
        return '{"on":true,"v":true,"seg":[{"col":[[255, 255, 225]],"bri":255}]}'
    elif color == ColorVal.YELLOW:
        return '{"on":true,"v":true,"seg":[{"col":[[255, 255, 0]],"bri":255}]}'
    else:
        return '{"on":false,"v":true,"seg":[{"col":[[255, 255, 225]],"bri":255}]}'

def unpack_rgb(color):
    r = 0xFF & (color >> 16)
    g = 0xFF & (color >> 8)
    b = 0xFF & color
    return r, g, b

def leaderProxy(args):
    if 'effect_fn' in args:
        if 'results' in args and args['results']:
            result = args['results']
        elif 'RACE' in args and hasattr(args['RACE'], 'results'):
            result = args['RACE'].results
        else:
            return False

        if result and 'meta' in result and 'primary_leaderboard' in result['meta']: 
            leaderboard = result[result['meta']['primary_leaderboard']]
        else:
            return False

        if len(leaderboard):
            leader = leaderboard[0]
            if leader['starts']:
                if 'node_index' not in args or args['node_index'] != leader['node']:
                    args['color'] = args['manager'].getDisplayColor(leader['node'], from_result=True)
                args['effect_fn'](args)
                return True
    return False

def led_on(strip, color=ColorVal.WHITE, pattern=ColorPattern.SOLID, offset=0):
    r,g,b = unpack_rgb(color)
    if pattern == ColorPattern.SOLID:
        for ip in WLED_IPS:
            try:
                r = requests.post(str(ip)+'/json/state', '{"on":true,"v":true,"seg":[{"start":0, "stop":' + wled_num_of_leds(ip) + '"fx":0, "col":[[' + str(r) + ',' + str(g) +',' + str(b) + ']],"bri":255}]}')
            except:
                print("Unable to contact server")
    else:
        patternlength = sum(pattern)
        wled_off=patternlength-pattern[0]
        for ip in WLED_IPS:
            try:
                r = requests.post(str(ip)+'/json/state', '{"on":true,"v":true,"seg":[{"fx":0, "col":[[' + str(r) + ',' + str(g) +',' + str(b) + ']],"bri":255, "grp":' + str(pattern[0]) + ', spc:' +  str(wled_off) + '}]}')
            except:
                print("Unable to contact server")

def led_off():
    for ip in WLED_IPS:
        try:
            r = requests.post(str(ip)+'/json/state', '{"on":false,"v":true}')
        except:
            print("Unable to contact server")

def chase(args):
    """Movie theater light style chaser animation."""
    if 'strip' in args:
        strip = args['strip']
    else:
        return False

    a = {
        'color': ColorVal.WHITE,
        'pattern': ColorPattern.ONE_OF_THREE,
        'speedDelay': 50,
        'iterations': 5,
    }
    a.update(args)

    led_off(strip)

    for i in range(a['iterations'] * sum(a['pattern'])):
        led_on(strip, a['color'], a['pattern'], i)
        gevent.sleep(a['speedDelay']/1000.0)

    r,g,b=unpack_rgb(a['color'])
    print("PATTERN")
    print(a['pattern'])
    for ip in WLED_IPS:
        try:
            r = requests.post(str(ip)+'/json/state', '{"on":true,"v":true,"seg":[{"fx":37, "col":[[' + str(r) + ',' + str(g) +',' + str(b) + ']],"bri":255, "grp":' + str(pattern[0]) + ', spc:' +  str(wled_off) + '}]}')
        except:
            print("Unable to contact server")

def color_wheel(pos):
    """Generate rainbow colors across 0-255 positions."""
    if pos < 85:
        return Color(pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return Color(255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return Color(0, pos * 3, 255 - pos * 3)

def rainbow(args):
    """Draw rainbow that fades across all pixels at once."""
    if 'strip' in args:
        strip = args['strip']
    else:
        return False

    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color_wheel(int(i * 256 / strip.numPixels()) & 255))
    strip.show()

def rainbowCycle(args):
    """Draw rainbow that uniformly distributes itself across all pixels."""
    if 'strip' in args:
        strip = args['strip']
    else:
        return False

    if args and 'wait_ms' in args:
        wait_ms = args['wait_ms']
    else:
        wait_ms = 2

    while True:
        for j in range(256):
            for i in range(strip.numPixels()):
                strip.setPixelColor(i, color_wheel((int(i * 256 / strip.numPixels()) + j) & 255))
            strip.show()
            gevent.sleep(wait_ms/1000.0)

def showColor(args):
    if 'strip' in args:
        strip = args['strip']
    else:
        return False

    if 'color' in args:
        color = args['color']
    else:
        color = ColorVal.WHITE

    if 'pattern' in args:
        pattern = args['pattern']
    else:
        pattern = ColorPattern.SOLID

    led_on(strip, color, pattern)

def clear():
    led_off()

# Effects adapted from work by Hans Luijten https://www.tweaking4all.com/hardware/arduino/adruino-led-strip-effects/

def colorWipe(args):
    gevent.idle() # never time-critical

    if 'strip' in args:
        strip = args['strip']
    else:
        return False

    a = {
        'color': ColorVal.WHITE,
        'speedDelay': 256,
    }
    a.update(args)

    a['speedDelay'] = a['speedDelay']/float(strip.numPixels()) # scale effect by strip length

    for i in range(strip.numPixels()):
        strip.setPixelColor(i, a['color'])
        strip.show()
        gevent.sleep(a['speedDelay']/1000.0)

def fade(args):
    if 'strip' in args:
        strip = args['strip']
    else:
        return False

    a = {
        'color': ColorVal.WHITE,
        'pattern': ColorPattern.SOLID,
        'steps': 25,
        'speedDelay': 10,
        'onTime': 250,
        'offTime': 250,
        'iterations': 1
    }
    a.update(args)

    led_off(strip)

    if 'outSteps' not in a:
        a['outSteps'] = a['steps']

    # effect should never exceed 3Hz (prevent seizures)
    a['offTime'] = min(333-((a['steps']*a['speedDelay'])+(a['outSteps']*a['speedDelay'])+a['onTime']), a['offTime'])

    for _i in range(a['iterations']):
        # fade in
        if a['steps']:
            led_off(strip)
            gevent.idle() # never time-critical
            for j in range(0, a['steps'], 1):
                c = dim(a['color'], j/float(a['steps']))
                led_on(strip, c, a['pattern'])
                strip.show()
                gevent.sleep(a['speedDelay']/1000.0)

            led_on(strip, a['color'], a['pattern'])
            gevent.sleep(a['onTime']/1000.0)

        # fade out
        if a['outSteps']:
            led_on(strip, a['color'], a['pattern'])
            for j in range(a['outSteps'], 0, -1):
                c = dim(a['color'], j/float(a['outSteps']))
                led_on(strip, c, a['pattern'])
                strip.show()
                gevent.sleep(a['speedDelay']/1000.0)

            led_off(strip)

        gevent.sleep(a['offTime']/1000.0)

def sparkle(args):
    if 'strip' in args:
        strip = args['strip']
    else:
        return False

    a = {
        'color': ColorVal.WHITE,
        'chance': 1.0,
        'decay': 0.95,
        'speedDelay': 100,
        'iterations': 100
    }
    a.update(args)

    gevent.idle() # never time-critical

    # decay time = log(decay cutoff=10 / max brightness=256) / log(decay rate)
    if a['decay']:
        decaySteps = int(math.ceil(math.log(0.00390625) / math.log(a['decay'])))
    else:
        decaySteps = 0

    led_off(strip)

    for i in range(a['iterations'] + decaySteps):
        # fade brightness all LEDs one step
        for j in range(strip.numPixels()):
            c = strip.getPixelColor(j)
            strip.setPixelColor(j, dim(c, a['decay']))

        # pick new pixels to light up
        if i < a['iterations']:
            for px in range(strip.numPixels()):
                if random.random() < float(a['chance']) / strip.numPixels():
                    # scale effect by strip length
                    strip.setPixelColor(px, a['color'])

        strip.show()
        gevent.sleep(a['speedDelay']/1000.0)

def meteor(args):
    if 'strip' in args:
        strip = args['strip']
    else:
        return False

    a = {
        'color': ColorVal.WHITE,
        'meteorSize': 10,
        'decay': 0.75,
        'randomDecay': True,
        'speedDelay': 1
    }
    a.update(args)

    gevent.idle() # never time-critical

    led_off(strip)

    for i in range(strip.numPixels()*2):

        # fade brightness all LEDs one step
        for j in range(strip.numPixels()):
            if not a['randomDecay'] or random.random() > 0.5:
                c = strip.getPixelColor(j)
                strip.setPixelColor(j, dim(c, a['decay']))

        # draw meteor
        for j in range(a['meteorSize']):
            if i - j < strip.numPixels() and i - j >= 0:
                strip.setPixelColor(i-j, a['color'])

        strip.show()
        gevent.sleep(a['speedDelay']/1000.0)

def stagingTrigger(args):
    stage_time = args['pi_staging_at_s']
    start_time = args['pi_starts_at_s']
    triggers = args['staging_tones']

    if triggers < 1:
        args['effect_fn'](args)
    else:
        idx = 0
        while idx < triggers:
            diff = stage_time - monotonic()
            diff_to_s = diff % 1
            if diff:
                gevent.sleep(diff_to_s)
                idx += 1
                args['effect_fn'](args)
            else:
                break

def larsonScanner(args):
    if 'strip' in args:
        strip = args['strip']
    else:
        return False

    a = {
        'color': ColorVal.WHITE,
        'eyeSize': 4,
        'speedDelay': 256,
        'returnDelay': 50,
        'iterations': 3
    }
    a.update(args)

    a['speedDelay'] = a['speedDelay']/float(strip.numPixels()) # scale effect by strip length

    gevent.idle() # never time-critical

    led_off(strip)

    for _k in range(a['iterations']):
        for i in range(strip.numPixels()-a['eyeSize']-1):
            strip.setPixelColor(i-1, ColorVal.NONE)

            strip.setPixelColor(i, dim(a['color'], 0.25))
            for j in range(a['eyeSize']):
                strip.setPixelColor(i+j+1, a['color'])
            strip.setPixelColor(i+a['eyeSize']+1, dim(a['color'], 0.25))
            strip.show()
            gevent.sleep(a['speedDelay']/1000.0)

        gevent.sleep(a['returnDelay']/1000.0)

        for i in range(strip.numPixels()-a['eyeSize']-2, -1, -1):
            if i < strip.numPixels()-a['eyeSize']-2:
                strip.setPixelColor(i+a['eyeSize']+2, ColorVal.NONE)

            strip.setPixelColor(i, dim(a['color'], 0.25))
            for j in range(a['eyeSize']):
                strip.setPixelColor(i+j+1, a['color'])
            strip.setPixelColor(i+a['eyeSize']+1, dim(a['color'], 0.25))
            strip.show()
            gevent.sleep(a['speedDelay']/1000.0)

        gevent.sleep(a['returnDelay']/1000.0)

def dim(color, decay):
    r = (color & 0x00ff0000) >> 16
    g = (color & 0x0000ff00) >> 8
    b = (color & 0x000000ff)

    r = 0 if r <= 1 else int(r*decay)
    g = 0 if g <= 1 else int(g*decay)
    b = 0 if b <= 1 else int(b*decay)

    return Color(int(r), int(g), int(b))

def discover():
    return [
    # color
    LEDEffect("Color/Pattern (Args)", showColor, {
        'manual': False,
        'exclude': [Evt.ALL]
        }, {
        'time': 4
        },
        name="stripColor",
    ),
    LEDEffect("Solid", showColor, {
        'include': [Evt.SHUTDOWN],
        'recommended': [Evt.RACE_START, Evt.RACE_STOP]
        }, {
        'pattern': ColorPattern.SOLID,
        'time': 4
        },
        name="stripColorSolid",
    ),
    LEDEffect("Pattern 1-1", showColor, {
        'include': [Evt.SHUTDOWN],
        }, {
        'pattern': ColorPattern.ALTERNATING,
        'time': 4
        },
        name="stripColor1_1",
    ),
    LEDEffect("Pattern 1-2", showColor, {
        'include': [Evt.SHUTDOWN],
        }, {
        'pattern': ColorPattern.ONE_OF_THREE,
        'time': 4
        },
        name="stripColor1_2",
    ),
    LEDEffect("Pattern 2-1", showColor, {
        'include': [Evt.SHUTDOWN],
        'recommended': [Evt.RACE_STAGE]
        }, {
        'pattern': ColorPattern.TWO_OUT_OF_THREE,
        'time': 4
        },
        name="stripColor2_1",
    ),
    LEDEffect("Staging Pulse 2-1", stagingTrigger, {
        'manual': False,
        'include': [Evt.RACE_STAGE],
        'exclude': [Evt.ALL],
        'recommended': [Evt.RACE_STAGE]
        }, {
        'effect_fn': fade,
        'pattern': ColorPattern.TWO_OUT_OF_THREE,
        'ontime': 0,
        'steps': 0,
        'outSteps': 10,
        'time': 2
        },
        name="stripStaging",
    ),
    LEDEffect("Pattern 4-4", showColor, {
        'include': [Evt.SHUTDOWN],
        'recommended': [Evt.RACE_FINISH]
        }, {
        'pattern': ColorPattern.FOUR_ON_FOUR_OFF,
        'time': 4
        },
        name="stripColor4_4",
    ),

    # chase
    LEDEffect("Chase Pattern 1-2", chase, {}, {
        'pattern': ColorPattern.ONE_OF_THREE,
        'speedDelay': 50,
        'iterations': 5
        },
        name="stripChase1_2",
    ),
    LEDEffect("Chase Pattern 2-1", chase, {}, {
        'pattern': ColorPattern.TWO_OUT_OF_THREE,
        'speedDelay': 50,
        'iterations': 5,
        },
        name="stripChase2_1",
    ),
    LEDEffect("Chase Pattern 4-4", chase, {}, {
        'pattern': ColorPattern.FOUR_ON_FOUR_OFF,
        'speedDelay': 50,
        'iterations': 5,
        },
        name="stripChase4_4",
    ),

    # rainbow
    LEDEffect("Rainbow", rainbow, {
        'include': [Evt.SHUTDOWN, LEDEvent.IDLE_DONE, LEDEvent.IDLE_READY, LEDEvent.IDLE_RACING],
        }, {
        'time': 4
        },
        name="rainbow",
    ),
    LEDEffect("Rainbow Cycle", rainbowCycle, {
        'include': [LEDEvent.IDLE_DONE, LEDEvent.IDLE_READY, LEDEvent.IDLE_RACING]
        },
        {},
        name="rainbowCycle",
    ),

    # wipe
    LEDEffect("Wipe", colorWipe, {}, {
        'speedDelay': 3,
        'time': 2
        },
        name="stripWipe",
    ),

    # fade
    LEDEffect("Fade In", fade, {}, {
        'pattern': ColorPattern.SOLID,
        'steps': 50,
        'outSteps': 0,
        'speedDelay': 10,
        'onTime': 0,
        'offTime': 0,
        'iterations': 1,
        'time': 4
        },
        name="stripFadeIn",
    ),
    LEDEffect("Pulse 3x", fade, {}, {
        'pattern': ColorPattern.SOLID,
        'steps': 10,
        'outSteps': 10,
        'speedDelay': 1,
        'onTime': 10,
        'offTime': 10,
        'iterations': 3,
        'time': 3
        },
        name="stripPulse",
    ),
    LEDEffect("Fade Out", fade, {}, {
        'pattern': ColorPattern.SOLID,
        'steps': 10,
        'outSteps': 128,
        'speedDelay': 1,
        'onTime': 0,
        'offTime': 0,
        'iterations': 1,
        'time': 4
        },
        name="stripFadeOut",
    ),

    # blink
    LEDEffect("Blink 3x", fade, {}, {
        'pattern': ColorPattern.SOLID,
        'steps': 1,
        'speedDelay': 1,
        'onTime': 100,
        'offTime': 100,
        'iterations': 3,
        'time': 3
        },
        name="stripBlink",
    ),

    # sparkle
    LEDEffect("Sparkle", sparkle, {}, {
        'chance': 1.0,
        'decay': 0.95,
        'speedDelay': 10,
        'iterations': 50,
        'time': 0
        },
        name="stripSparkle",
    ),

    # meteor
    LEDEffect("Meteor Fall", meteor, {}, {
        'meteorSize': 10,
        'decay': 0.75,
        'randomDecay': True,
        'speedDelay': 1,
        'time': 0
        },
        name="stripMeteor",
    ),

    # larson scanner
    LEDEffect("Scanner", larsonScanner, {}, {
        'eyeSize': 4,
        'speedDelay': 256,
        'returnDelay': 50,
        'iterations': 3,
        'time': 0
        },
        name="stripScanner",
    ),

    # leader color proxies
    LEDEffect("Solid / Leader", leaderProxy, {
        'include': [Evt.RACE_LAP_RECORDED, LEDEvent.IDLE_RACING, LEDEvent.IDLE_DONE],
        'exclude': [Evt.ALL],
        'recommended': [Evt.RACE_LAP_RECORDED]
        }, {
        'effect_fn': showColor,
        'pattern': ColorPattern.SOLID,
        'time': 4
        },
        name="stripColorSolidLeader",
    ),
    LEDEffect("Pattern 1-1 / Leader", leaderProxy, {
        'include': [Evt.RACE_LAP_RECORDED, LEDEvent.IDLE_RACING, LEDEvent.IDLE_DONE],
        'exclude': [Evt.ALL],
        'recommended': [Evt.RACE_LAP_RECORDED]
        }, {
        'effect_fn': showColor,
        'pattern': ColorPattern.ALTERNATING,
        'time': 4
        },
        name="stripColor1_1Leader",
    ),
    LEDEffect("Pattern 1-2 / Leader", leaderProxy, {
        'include': [Evt.RACE_LAP_RECORDED, LEDEvent.IDLE_RACING, LEDEvent.IDLE_DONE],
        'exclude': [Evt.ALL],
        'recommended': [Evt.RACE_LAP_RECORDED]
        }, {
        'effect_fn': showColor,
        'pattern': ColorPattern.ONE_OF_THREE,
        'time': 4
        },
        name="stripColor1_2Leader",
    ),
    LEDEffect("Pattern 2-1 / Leader", leaderProxy, {
        'include': [Evt.RACE_LAP_RECORDED, LEDEvent.IDLE_RACING, LEDEvent.IDLE_DONE],
        'exclude': [Evt.ALL],
        'recommended': [Evt.RACE_LAP_RECORDED]
        }, {
        'effect_fn': showColor,
        'pattern': ColorPattern.TWO_OUT_OF_THREE,
        'time': 4
        },
        name="stripColor2_1Leader",
    ),
    LEDEffect("Pattern 4-4 / Leader", leaderProxy, {
        'include': [Evt.RACE_LAP_RECORDED, LEDEvent.IDLE_RACING, LEDEvent.IDLE_DONE],
        'exclude': [Evt.ALL],
        'recommended': [Evt.RACE_LAP_RECORDED]
        }, {
        'effect_fn': showColor,
        'pattern': ColorPattern.FOUR_ON_FOUR_OFF,
        'time': 4
        },
        name="stripColor4_4Leader",
    ),

    # clear - permanently assigned to LEDEventManager.clear()
    LEDEffect("Turn Off", clear, {
        'manual': False,
        'include': [Evt.SHUTDOWN, LEDEvent.IDLE_DONE, LEDEvent.IDLE_READY, LEDEvent.IDLE_RACING],
        'recommended': [Evt.ALL]
        }, {
            'time': 8
        },
        name="clear",
    )
    ]

def register_handlers(args):
    for led_effect in discover():
        args['register_fn'](led_effect)

class wled_manager():

    def __init__(self, rhapi):
        self._rhapi = rhapi
        self._rhapi.events.on(Evt.LED_INITIALIZE, register_handlers)
        # # rhapi.fields.register_pilot_attribute(UIField(MAC_ADDR_OPT_NAME, "Fusion MAC Address", UIFieldType.TEXT))
        # # rhapi.ui.register_panel('vrx_tbs', 'VRX Control: TBS', 'settings')
        # # rhapi.fields.register_option(UIField('tbs_comms_port', "Manual Port Override", UIFieldType.TEXT), 'vrx_tbs')
        # # rhapi.ui.register_quickbutton('vrx_tbs', 'run_autodetect', "Run Port Assignment", controller.discoverPort, args={'manual':True})

        self._rhapi.ui.register_panel('wled', 'WLED', 'settings')
        self._rhapi.fields.register_option(UIField('wled_ip', "Enter WLED IP seperated by space    (ie http://192.168.1.2))", UIFieldType.TEXT), 'wled')
        self._rhapi.ui.register_quickbutton('wled', 'wled_save', "Save WLED Addresses", self.saveip())
        logger.debug("Finish initalizing plugin module WLED")

    def saveip(self):
        print(self._rhapi.db.option)
        print(self._rhapi.db.option('tbs_comms_port', None))
        print(self._rhapi.db.option("wled_ip"))
        # for plugin_setting in rhapi.fields.options:
        #     if plugin_setting.name == "wled_ip":
        #         # print(plugin_setting.field)
        #         # print(plugin_setting.field.value)
        #         pass
        # # ports = rhapi.db.option('wled_ip', None)
        # # print(ports)
        WLED_IPS = string.split()

def initialize(rhapi):
    print("HIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII")
    wled=wled_manager(rhapi)
