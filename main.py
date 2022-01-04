from phys import Train
from tkinter import Tk, Label
from time import sleep

env = Train(40, 7, 2.5)


def sm_inc(e):
    if env.gear < 7:
        env.gear += 1


def sm_dec(e):
    if env.gear > 0:
        env.gear -= 1


def mq_inc(e):
    if env.movement_q < 1:
        env.movement_q += 1


def mq_dec(e):
    if env.movement_q > -1:
        env.movement_q -= 1


def main():
    try:
        env.start()

        w = Tk()
        w.geometry('300x200')

        speed_label = Label(w)
        speed_mode_label = Label(w)
        pos_label = Label(w)

        speed_label.pack()
        speed_mode_label.pack()
        pos_label.pack()

        w.bind('w', sm_inc)
        w.bind('s', sm_dec)
        w.bind('a', mq_dec)
        w.bind('d', mq_inc)

        while True:
            speed_label.config(text='Speed: %s km/h' % str(round(env.current_speed, 1)))
            speed_mode_label.config(text='Speed mode: ' + str(env.gear))
            pos_label.config(text='Kilometers ridden: ' + str(round(env.pos, 3)))
            sleep(1 / env.tps)
            w.update()
    except BaseException as e:
        env.running = False
        raise e


if __name__ == '__main__':
    main()
