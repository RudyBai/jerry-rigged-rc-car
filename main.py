import serial
from inputs import get_gamepad, get_key


def keyboard():
    steering = 0
    throttle = 0
    reverse = 0
    throttle_direction = 'F'
    steering_direction = 'L'
    send = False
    while True:
        events = get_key()
        if events:
            for event in events:
                if event.ev_type == "Key":
                    if event.code == "KEY_UP":
                        if event.state == 1 and throttle != 255:
                            throttle = 255
                            throttle_direction = 'F'
                            send = True
                        elif event.state == 0:
                            throttle = 0
                            send = True
                    elif event.code == "KEY_DOWN":
                        if event.state == 1 and reverse != 255:
                            reverse = 255
                            throttle_direction = 'R'
                            send = True
                        elif event.state == 0:
                            reverse = 0
                            send = True
                    elif event.code == "KEY_LEFT":
                        if event.state == 1 and steering != 255:
                            steering = 255
                            steering_direction = 'L'
                            send = True
                        elif event.state == 0:
                            steering = 0
                            send = True
                    elif event.code == "KEY_RIGHT":
                        if event.state == 1 and steering != 255:
                            steering = 255
                            steering_direction = 'R'
                            send = True
                        elif event.state == 0:
                            steering = 0
                            send = True
                    if send:
                        arduino.write(bytes(str("%c%03d%c%03d\0" % (
                            steering_direction,
                            steering,
                            throttle_direction,
                            throttle if throttle_direction == 'F' else reverse
                        )), 'utf-8'))
                        send = False


def controller():
    steering = 0
    throttle = 0
    reverse = 0
    steering_direction = 'L'
    send = False

    while True:
        events = get_gamepad()
        for event in events:
            if event.ev_type == "Absolute":
                if event.code == "ABS_RZ":
                    throttle = event.state
                    send = True
                elif event.code == "ABS_Z":
                    reverse = event.state
                    send = True
                elif event.code == "ABS_X":
                    steering = translate(event.state, -32768, 32767, 255, -255)
                    steering_direction = 'L' if steering > 0 else 'R'
                    steering = abs(steering)
                    send = True
                if send:
                    direction = throttle > reverse
                    arduino.write(bytes(str("%c%03d%c%03d\0" % (
                        steering_direction,
                        steering,
                        'F' if direction else 'R',
                        throttle if direction else reverse
                    )), 'utf-8'))
                    print("%c%03d%c%03d\0" % (
                        steering_direction,
                        abs(steering),
                        'R' if direction else 'F',
                        throttle if direction else reverse
                    ), end='\r')
                    send = False















































def wheel():
    import pygame
    import logitechG29_wheel
    pygame.init()
    steering_wheel = logitechG29_wheel.Controller(0)
    steering, throttle, reverse = 0, 0, 0
    steering_direction = 'L'
    send = False

    done = False
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True

        steer_pos = translate(steering_wheel.get_steer(), -1, 1, -255, 255)
        if steer_pos != steering:
            steering = steer_pos
            steering_direction = 'L' if steering < 0 else 'R'
            send = True

        raw_breaking = steering_wheel.get_break()
        raw_throttle = steering_wheel.get_throttle()

        temp_reverse = translate(raw_breaking, -1, 1, 255, 0)
        temp_throttle = translate(raw_throttle, -1, 1, 255, 0)

        if temp_reverse != reverse or temp_throttle != throttle:
            reverse = temp_reverse
            throttle = temp_throttle
            send = True

        if send:
            direction = throttle < reverse
            arduino.write(bytes(str("%c%03d%c%03d\0" % (
                steering_direction,
                abs(steering),
                'R' if direction else 'F',
                reverse if direction else throttle
            )), 'utf-8'))
            print("%c%03d%c%03d\0" % (
                steering_direction,
                abs(steering),
                'R' if direction else 'F',
                reverse if direction else throttle
            ), end='\r')
            send = False

    pygame.quit()


def translate(value, left_min, left_max, right_min, right_max):
    left_span = left_max - left_min
    right_span = right_max - right_min
    value_scaled = float(value - left_min) / float(left_span)
    return int(right_min + (value_scaled * right_span))


if __name__ == "__main__":
    arduino = serial.Serial(port='COM3', baudrate=115200, timeout=.1)
    print("Choose your controller:")
    print("1. Keyboard.")
    print("2. Controller.")
    print("3. Steering Wheel + Pedals.")
    choice = input(">>> ")
    if int(choice) == 1:
        keyboard()
    elif int(choice) == 2:
        controller()
    elif int(choice) == 3:
        wheel()
    else:
        print("Invalid.")
