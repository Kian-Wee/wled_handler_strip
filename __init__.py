''' WLED effects '''

import requests
from eventmanager import Evt
from led_event_manager import LEDEffect, LEDEvent, Color, ColorVal, ColorPattern
import gevent
import random
import math
from monotonic import monotonic
from RHUI import UIField, UIFieldType
import logging

logger = logging.getLogger(__name__)

# WLED_IPS=['http://192.168.1.224', 'http://192.168.1.205']
WLED_IPS=['http://192.168.1.224']


#Query for the number of leds on a particular strip
def wled_num_of_leds(IP):
    url=str(IP)+"/json/info"
    try:
        response = requests.get(url).json()
    except:
        print("Unable to get response from: "+ url)

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

# Convert RGB hexadecimal to RGB int values
def unpack_rgb(color):
    r = 0xFF & (color >> 16)
    g = 0xFF & (color >> 8)
    b = 0xFF & color
    return r, g, b

def wledleaderProxy(args):
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

def wledled_on(strip, color=ColorVal.WHITE, pattern=ColorPattern.SOLID, offset=0):
    r,g,b = unpack_rgb(color)
    if pattern == ColorPattern.SOLID or pattern == None:
        for ip in WLED_IPS:
            try:
                print(WLED_IPS)
                print(str(ip)+'/json/state', '{"on":true,"v":true,"seg":[{"start":0, "stop":'+ str(wled_num_of_leds(ip)) +', "grp":1, "spc":0, "fx":0, "col":[[' + str(r) + ',' + str(g) +',' + str(b) + ']],"bri":255}]}')
                req = requests.post(str(ip)+'/json/state', '{"on":true,"v":true,"seg":[{"start":0, "stop":'+ str(wled_num_of_leds(ip)) +', "grp":1, "spc":0, "fx":0, "col":[[' + str(r) + ',' + str(g) +',' + str(b) + ']],"bri":255}]}')
            except:
                print("Unable to contact server", ip)
    else:
        patternlength = sum(pattern)
        wled_off=patternlength-pattern[0]
        for ip in WLED_IPS:
            try:
                req = requests.post(str(ip)+'/json/state', '{"on":true,"v":true,"seg":[{"fx":0, "col":[[' + str(r) + ',' + str(g) +',' + str(b) + ']],"bri":255, "grp":' + str(pattern[0]) + ', spc:' +  str(wled_off) + '}]}')
            except:
                print("Unable to contact server", ip)

def wledled_off(strip):
    for ip in WLED_IPS:
        try:
            req = requests.post(str(ip)+'/json/state', '{"on":false,"v":true}')
        except:
            print("Unable to contact server", ip)

#TODO
def wledchase(args):
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

    # led_off(strip)

    # for i in range(a['iterations'] * sum(a['pattern'])):
    #     led_on(strip, a['color'], a['pattern'], i)
    #     gevent.sleep(a['speedDelay']/1000.0)

    r,g,b=unpack_rgb(a['color'])
    for ip in WLED_IPS:
        try:
            req = requests.post(str(ip)+'/json/state', '{"on":true,"v":true,"seg":[{"start":0, "stop":'+ str(wled_num_of_leds(ip)) +', "grp":1, "spc":0, "fx":37, "col":[[' + str(r) + ',' + str(g) +',' + str(b) + ']],"bri":255}]}')
        except:
            print("Unable to contact server", ip)


def wledcolorloop(args):
    """Draw rainbow that fades across all pixels at once."""
    for ip in WLED_IPS:
        try:
            req = requests.post(str(ip)+'/json/state', '{"on":true,"v":true,"seg":[{"start":0, "stop":'+ str(wled_num_of_leds(ip)) +', "grp":1, "spc":0, "fx":8 ,"bri":255}]}')
        except:
            print("Unable to contact server", ip)

def wledpalette(args):
    """Draw rainbow that uniformly distributes itself across all pixels."""
    for ip in WLED_IPS:
        try:
            req = requests.post(str(ip)+'/json/state', '{"on":true,"v":true,"seg":[{"start":0, "stop":'+ str(wled_num_of_leds(ip)) +', "grp":1, "spc":0, "fx":65 ,"bri":255}]}')
        except:
            print("Unable to contact server", ip)

def wledshowColor(args):
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
        print("PATTERNING")
        pattern = ColorPattern.SOLID
    wledled_on(strip, color, pattern)

def wledclear(args):
    if 'strip' in args:
        strip = args['strip']
    else:
        return False
    wledled_off(strip)

def wledcolorWipe(args):

    if 'strip' in args:
        strip = args['strip']
    else:
        return False

    a = {
        'color': ColorVal.WHITE,
        'speedDelay': 256,
    }
    a.update(args)
    r,g,b = unpack_rgb(a['color'])
    for ip in WLED_IPS:
        try:
            req = requests.post(str(ip)+'/json/state', '{"on":true,"v":true,"seg":[{"start":0, "stop":'+ str(wled_num_of_leds(ip)) +', "grp":1, "spc":0, "fx":3, "col":[[' + str(r) + ',' + str(g) +',' + str(b) + ']],"bri":255}]}')
        except:
            print("Unable to contact server", ip)

def wledfade(args):
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

    r,g,b = unpack_rgb(a['color'])
    for ip in WLED_IPS:
        try:
            req = requests.post(str(ip)+'/json/state', '{"on":true,"v":true,"seg":[{"start":0, "stop":'+ str(wled_num_of_leds(ip)) +', "grp":1, "spc":0, "fx":12, "col":[[' + str(r) + ',' + str(g) +',' + str(b) + ']],"bri":255}]}')
        except:
            print("Unable to contact server", ip)

    # led_off(strip)

    # if 'outSteps' not in a:
    #     a['outSteps'] = a['steps']

    # # effect should never exceed 3Hz (prevent seizures)
    # a['offTime'] = min(333-((a['steps']*a['speedDelay'])+(a['outSteps']*a['speedDelay'])+a['onTime']), a['offTime'])

    # for _i in range(a['iterations']):
    #     # fade in
    #     if a['steps']:
    #         led_off(strip)
    #         gevent.idle() # never time-critical
    #         for j in range(0, a['steps'], 1):
    #             c = dim(a['color'], j/float(a['steps']))
    #             led_on(strip, c, a['pattern'])
    #             strip.show()
    #             gevent.sleep(a['speedDelay']/1000.0)

    #         led_on(strip, a['color'], a['pattern'])
    #         gevent.sleep(a['onTime']/1000.0)

    #     # fade out
    #     if a['outSteps']:
    #         led_on(strip, a['color'], a['pattern'])
    #         for j in range(a['outSteps'], 0, -1):
    #             c = dim(a['color'], j/float(a['outSteps']))
    #             led_on(strip, c, a['pattern'])
    #             strip.show()
    #             gevent.sleep(a['speedDelay']/1000.0)

    #         led_off(strip)

    #     gevent.sleep(a['offTime']/1000.0)

def wledsparkle(args):
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

    r,g,b = unpack_rgb(a['color'])
    for ip in WLED_IPS:
        try:
            req = requests.post(str(ip)+'/json/state', '{"on":true,"v":true,"seg":[{"start":0, "stop":'+ str(wled_num_of_leds(ip)) +', "grp":1, "spc":0, "fx":95, "col":[[' + str(r) + ',' + str(g) +',' + str(b) + ']],"bri":255}]}')
        except:
            print("Unable to contact server", ip)
    # gevent.idle() # never time-critical

    # # decay time = log(decay cutoff=10 / max brightness=256) / log(decay rate)
    # if a['decay']:
    #     decaySteps = int(math.ceil(math.log(0.00390625) / math.log(a['decay'])))
    # else:
    #     decaySteps = 0

    # led_off(strip)

    # for i in range(a['iterations'] + decaySteps):
    #     # fade brightness all LEDs one step
    #     for j in range(strip.numPixels()):
    #         c = strip.getPixelColor(j)
    #         strip.setPixelColor(j, dim(c, a['decay']))

    #     # pick new pixels to light up
    #     if i < a['iterations']:
    #         for px in range(strip.numPixels()):
    #             if random.random() < float(a['chance']) / strip.numPixels():
    #                 # scale effect by strip length
    #                 strip.setPixelColor(px, a['color'])

    #     strip.show()
    #     gevent.sleep(a['speedDelay']/1000.0)

def wledmeteor(args):
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

    r,g,b = unpack_rgb(a['color'])
    for ip in WLED_IPS:
        try:
            req = requests.post(str(ip)+'/json/state', '{"on":true,"v":true,"seg":[{"start":0, "stop":'+ str(wled_num_of_leds(ip)) +', "grp":1, "spc":0, "fx":76, "col":[[' + str(r) + ',' + str(g) +',' + str(b) + ']],"bri":255}]}')
        except:
            print("Unable to contact server", ip)
    # gevent.idle() # never time-critical

    # led_off(strip)

    # for i in range(strip.numPixels()*2):

    #     # fade brightness all LEDs one step
    #     for j in range(strip.numPixels()):
    #         if not a['randomDecay'] or random.random() > 0.5:
    #             c = strip.getPixelColor(j)
    #             strip.setPixelColor(j, dim(c, a['decay']))

    #     # draw meteor
    #     for j in range(a['meteorSize']):
    #         if i - j < strip.numPixels() and i - j >= 0:
    #             strip.setPixelColor(i-j, a['color'])

    #     strip.show()
    #     gevent.sleep(a['speedDelay']/1000.0)

def wledstagingTrigger(args):
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

def wledlarsonScanner(args):
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

    r,g,b = unpack_rgb(a['color'])
    for ip in WLED_IPS:
        try:
            req = requests.post(str(ip)+'/json/state', '{"on":true,"v":true,"seg":[{"start":0, "stop":'+ str(wled_num_of_leds(ip)) +', "grp":1, "spc":0, "fx":60, "col":[[' + str(r) + ',' + str(g) +',' + str(b) + ']],"bri":255}]}')
        except:
            print("Unable to contact server", ip)

    # a['speedDelay'] = a['speedDelay']/float(strip.numPixels()) # scale effect by strip length

    # gevent.idle() # never time-critical

    # led_off(strip)

    # for _k in range(a['iterations']):
    #     for i in range(strip.numPixels()-a['eyeSize']-1):
    #         strip.setPixelColor(i-1, ColorVal.NONE)

    #         strip.setPixelColor(i, dim(a['color'], 0.25))
    #         for j in range(a['eyeSize']):
    #             strip.setPixelColor(i+j+1, a['color'])
    #         strip.setPixelColor(i+a['eyeSize']+1, dim(a['color'], 0.25))
    #         strip.show()
    #         gevent.sleep(a['speedDelay']/1000.0)

    #     gevent.sleep(a['returnDelay']/1000.0)

    #     for i in range(strip.numPixels()-a['eyeSize']-2, -1, -1):
    #         if i < strip.numPixels()-a['eyeSize']-2:
    #             strip.setPixelColor(i+a['eyeSize']+2, ColorVal.NONE)

    #         strip.setPixelColor(i, dim(a['color'], 0.25))
    #         for j in range(a['eyeSize']):
    #             strip.setPixelColor(i+j+1, a['color'])
    #         strip.setPixelColor(i+a['eyeSize']+1, dim(a['color'], 0.25))
    #         strip.show()
    #         gevent.sleep(a['speedDelay']/1000.0)

    #     gevent.sleep(a['returnDelay']/1000.0)

def wleddim(color, decay):
    r = (color & 0x00ff0000) >> 16
    g = (color & 0x0000ff00) >> 8
    b = (color & 0x000000ff)

    r = 0 if r <= 1 else int(r*decay)
    g = 0 if g <= 1 else int(g*decay)
    b = 0 if b <= 1 else int(b*decay)

    return Color(int(r), int(g), int(b))

def wleddiscover():
    return [
    # color
    LEDEffect("Color/Pattern[WLED] (Args)", wledshowColor, {
        'manual': False,
        'exclude': [Evt.ALL]
        }, {
        'time': 4
        },
    ),
    LEDEffect("Solid[WLED]", wledshowColor, {
        'include': [Evt.SHUTDOWN],
        'recommended': [Evt.RACE_START, Evt.RACE_STOP]
        }, {
        'pattern': ColorPattern.SOLID,
        'time': 4
        },
    ),
    LEDEffect("Pattern 1-1[WLED]", wledshowColor, {
        'include': [Evt.SHUTDOWN],
        }, {
        'pattern': ColorPattern.ALTERNATING,
        'time': 4
        },
    ),
    LEDEffect("Pattern 1-2[WLED]", wledshowColor, {
        'include': [Evt.SHUTDOWN],
        }, {
        'pattern': ColorPattern.ONE_OF_THREE,
        'time': 4
        },
    ),
    LEDEffect("Pattern 2-1[WLED]", wledshowColor, {
        'include': [Evt.SHUTDOWN],
        'recommended': [Evt.RACE_STAGE]
        }, {
        'pattern': ColorPattern.TWO_OUT_OF_THREE,
        'time': 4
        },
    ),
    LEDEffect("Staging Pulse 2-1[WLED]", wledstagingTrigger, {
        'manual': False,
        'include': [Evt.RACE_STAGE],
        'exclude': [Evt.ALL],
        'recommended': [Evt.RACE_STAGE]
        }, {
        'effect_fn': wledfade,
        'pattern': ColorPattern.TWO_OUT_OF_THREE,
        'ontime': 0,
        'steps': 0,
        'outSteps': 10,
        'time': 2
        },
    ),
    LEDEffect("Pattern 4-4[WLED]", wledshowColor, {
        'include': [Evt.SHUTDOWN],
        'recommended': [Evt.RACE_FINISH]
        }, {
        'pattern': ColorPattern.FOUR_ON_FOUR_OFF,
        'time': 4
        },
    ),

    # chase
    LEDEffect("Chase Pattern 1-2[WLED]", wledchase, {}, {
        'pattern': ColorPattern.ONE_OF_THREE,
        'speedDelay': 50,
        'iterations': 5
        },
    ),
    LEDEffect("Chase Pattern 2-1[WLED]", wledchase, {}, {
        'pattern': ColorPattern.TWO_OUT_OF_THREE,
        'speedDelay': 50,
        'iterations': 5,
        },
    ),
    LEDEffect("Chase Pattern 4-4[WLED]", wledchase, {}, {
        'pattern': ColorPattern.FOUR_ON_FOUR_OFF,
        'speedDelay': 50,
        'iterations': 5,
        },
    ),

    # rainbow
    LEDEffect("Rainbow[WLED]", wledcolorloop, {
        'include': [Evt.SHUTDOWN, LEDEvent.IDLE_DONE, LEDEvent.IDLE_READY, LEDEvent.IDLE_RACING],
        }, {
        'time': 4
        },
    ),
    LEDEffect("Rainbow Cycle[WLED]", wledpalette, {
        'include': [LEDEvent.IDLE_DONE, LEDEvent.IDLE_READY, LEDEvent.IDLE_RACING]
        },
        {},
    ),

    # wipe
    LEDEffect("Wipe[WLED]", wledcolorWipe, {}, {
        'speedDelay': 3,
        'time': 2
        },
    ),

    # fade
    LEDEffect("Fade In[WLED]", wledfade, {}, {
        'pattern': ColorPattern.SOLID,
        'steps': 50,
        'outSteps': 0,
        'speedDelay': 10,
        'onTime': 0,
        'offTime': 0,
        'iterations': 1,
        'time': 4
        },
    ),
    LEDEffect("Pulse 3x[WLED]", wledfade, {}, {
        'pattern': ColorPattern.SOLID,
        'steps': 10,
        'outSteps': 10,
        'speedDelay': 1,
        'onTime': 10,
        'offTime': 10,
        'iterations': 3,
        'time': 3
        },
    ),
    LEDEffect("Fade Out[WLED]", wledfade, {}, {
        'pattern': ColorPattern.SOLID,
        'steps': 10,
        'outSteps': 128,
        'speedDelay': 1,
        'onTime': 0,
        'offTime': 0,
        'iterations': 1,
        'time': 4
        },
    ),

    # blink
    LEDEffect("Blink 3x[WLED]", wledfade, {}, {
        'pattern': ColorPattern.SOLID,
        'steps': 1,
        'speedDelay': 1,
        'onTime': 100,
        'offTime': 100,
        'iterations': 3,
        'time': 3
        },
    ),

    # sparkle
    LEDEffect("Sparkle[WLED]", wledsparkle, {}, {
        'chance': 1.0,
        'decay': 0.95,
        'speedDelay': 10,
        'iterations': 50,
        'time': 0
        },
    ),

    # meteor
    LEDEffect("Meteor Fall[WLED]", wledmeteor, {}, {
        'meteorSize': 10,
        'decay': 0.75,
        'randomDecay': True,
        'speedDelay': 1,
        'time': 0
        },
    ),

    # larson scanner
    LEDEffect("Scanner[WLED]", wledlarsonScanner, {}, {
        'eyeSize': 4,
        'speedDelay': 256,
        'returnDelay': 50,
        'iterations': 3,
        'time': 0
        },
    ),

    # leader color proxies
    LEDEffect("Solid / Leader[WLED]", wledleaderProxy, {
        'include': [Evt.RACE_LAP_RECORDED, LEDEvent.IDLE_RACING, LEDEvent.IDLE_DONE],
        'exclude': [Evt.ALL],
        'recommended': [Evt.RACE_LAP_RECORDED]
        }, {
        'effect_fn': wledshowColor,
        'pattern': ColorPattern.SOLID,
        'time': 4
        },
    ),
    LEDEffect("Pattern 1-1 / Leader[WLED]", wledleaderProxy, {
        'include': [Evt.RACE_LAP_RECORDED, LEDEvent.IDLE_RACING, LEDEvent.IDLE_DONE],
        'exclude': [Evt.ALL],
        'recommended': [Evt.RACE_LAP_RECORDED]
        }, {
        'effect_fn': wledshowColor,
        'pattern': ColorPattern.ALTERNATING,
        'time': 4
        },
    ),
    LEDEffect("Pattern 1-2 / Leader[WLED]", wledleaderProxy, {
        'include': [Evt.RACE_LAP_RECORDED, LEDEvent.IDLE_RACING, LEDEvent.IDLE_DONE],
        'exclude': [Evt.ALL],
        'recommended': [Evt.RACE_LAP_RECORDED]
        }, {
        'effect_fn': wledshowColor,
        'pattern': ColorPattern.ONE_OF_THREE,
        'time': 4
        },
    ),
    LEDEffect("Pattern 2-1 / Leader[WLED]", wledleaderProxy, {
        'include': [Evt.RACE_LAP_RECORDED, LEDEvent.IDLE_RACING, LEDEvent.IDLE_DONE],
        'exclude': [Evt.ALL],
        'recommended': [Evt.RACE_LAP_RECORDED]
        }, {
        'effect_fn': wledshowColor,
        'pattern': ColorPattern.TWO_OUT_OF_THREE,
        'time': 4
        },
    ),
    LEDEffect("Pattern 4-4 / Leader[WLED]", wledleaderProxy, {
        'include': [Evt.RACE_LAP_RECORDED, LEDEvent.IDLE_RACING, LEDEvent.IDLE_DONE],
        'exclude': [Evt.ALL],
        'recommended': [Evt.RACE_LAP_RECORDED]
        }, {
        'effect_fn': wledshowColor,
        'pattern': ColorPattern.FOUR_ON_FOUR_OFF,
        'time': 4
        },
    ),

    # clear - permanently assigned to LEDEventManager.clear()
    LEDEffect("Turn Off[WLED]", wledclear, {
        'manual': False,
        'include': [Evt.SHUTDOWN, LEDEvent.IDLE_DONE, LEDEvent.IDLE_READY, LEDEvent.IDLE_RACING],
        'recommended': [Evt.ALL]
        }, {
            'time': 8
        },
    )
    ]

def wledregister_handlers(args):
    for led_effect in wleddiscover():
        args['register_fn'](led_effect)

class wled_manager():

    def __init__(self, rhapi):
        self._rhapi = rhapi
        self._rhapi.events.on(Evt.LED_INITIALIZE, wledregister_handlers)

        self._rhapi.ui.register_panel('wled', 'WLED', 'settings')
        self._rhapi.fields.register_option(UIField('wled_ip', "Enter WLED IP seperated by space    (ie http://192.168.1.2))", UIFieldType.TEXT), 'wled')
        self._rhapi.ui.register_quickbutton('wled', 'wled_save', "Save WLED Addresses", self.saveip)
        logger.debug("Finish initalizing plugin module WLED")

    # Needs args else database will be empty ?
    def saveip(self,args):
        global WLED_IPS
        WLED_IPS = str(self._rhapi.db.option('wled_ip', None)).split()
        print("Updated WLED IP: " + str(WLED_IPS))

def initialize(rhapi):
    wled=wled_manager(rhapi)
