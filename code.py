from adafruit_circuitplayground import cp
import time
import math
import random


class Holder:

    def __init__(self, value):
        self.value_arr = [value]

    def get(self):
        return self.value_arr[0]

    def set(self, value):
        self.value_arr[0] = value


class BopInput:

    def __init__(self, action_checker, action_text, passed_action=lambda: None):
        self.action_checker = action_checker
        self.action_text = action_text
        self.passed_action = passed_action


# library method that could not be imported
def hsv_to_rgb(h, s, v):
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
    # Cannot get here


last_switch_state = Holder(cp.switch)
room_light_avg = .5


# There's other types, but they were too annoying to activate/would activate randomly
bops = [BopInput(lambda: cp.light < room_light_avg / 2, "Shut it!"),
        #BopInput(lambda: cp.button_a or cp.button_b, "Press it!"),
        BopInput(lambda: cp.button_a, "Press a!"),
        BopInput(lambda: cp.button_b, "Press b!"),
        BopInput(lambda: last_switch_state.get() != cp.switch, "Switch it!", lambda: last_switch_state.set(cp.switch)),
        #BopInput(lambda: cp.tapped, "Tap it!"),
        #BopInput(lambda: cp.shake(), "Shake it!"),
        #BopInput(lambda: cp.loud_sound(100), " it!"),
        #BopInput(lambda: cp.touch_A1 or cp.touch_A2 or cp.touch_A3
        #or cp.touch_A4 or cp.touch_A5 or cp.touch_A6 or cp.touch_TX, "Touch it!")
        BopInput(lambda: math.sqrt(cp.acceleration[0] ** 2 + cp.acceleration[1] ** 2
                                   + cp.acceleration[2] ** 2) > 16, "Shake it!")
                                   ]


def signum(number):
    return 0 if number < 0 else 1 if number > 1 else number


cp.pixels.brightness = 0.1


def action(bop_index, duration, level_hue):
    bop = bops[bop_index]
    print(bop.action_text)
    start_time = time.monotonic()
    current_time = start_time
    while current_time <= start_time + duration:
        current_time = time.monotonic()
        for b in bops:
            if b.action_checker():
                b.passed_action()
                return b == bop
        for i in range(5):
            color = hsv_to_rgb(level_hue, 1, 1)
            light = 255 * (1 - signum(5 * (current_time - start_time) / duration - i))
            color = light * color[0], light * color[1], light * color[2]
            cp.pixels[i] = color
            cp.pixels[9 - i] = color
    return False


if __name__ == '__main__':

    rankedResponses = ["You're amazing", "Looking good", "Fair", "You can do better", "You failed"]
    best_score = 0
    #last_switch_state = cp.switch
    while True:
        room_light_total = 0
        room_light_samples = 0
        level = 1
        print("Do each command before the time runs out... Ready? (press any button (a or b) to start)")
        while True:
            room_light_total += cp.light
            room_light_samples += 1
            if cp.button_a or cp.button_b:
                break
        while cp.button_a or cp.button_b:
            pass
        time.sleep(0.2)
        room_light_avg = room_light_total / room_light_samples
        # print("Room light is ", room_light_avg / 5)
        while action(random.randint(0, len(bops) - 1), max(1.5, 5 - (level / 7)), ((level - 1) / 20) % 1):
            level += 1
            print("STOP!")
            time.sleep(1)
        cp.pixels.fill((0, 0, 0))
        print(rankedResponses[max(0, 4 - int(level / 7))])
        while cp.button_a or cp.button_b: # Make sure they aren't still holding down the button
            pass
        if level - 1 > best_score:
            best_score = level - 1
            print("New record: " + str(best_score) + " !!")
        elif level - 1 == best_score:
            print("You tied your record of ", best_score)
        else:
            print("You got ", str(level - 1), " and your best is ", best_score)
