from threading import Thread
from time import sleep


class Train:
    def __init__(self, max_speed, max_gear, sps, road_max, road_min=0, tps=10):
        self.current_speed = 0  # Current speed in km/h
        self.max_speed = max_speed  # Maximum speed in km/h
        self.gear = 0
        self.max_gear = max_gear
        self.pos = 0    # Train position in meters
        self.spt = sps / tps  # Speed per tick. Increment or decrement of speed per tick
        self.tps = tps
        self.tick_thread = Thread(target=self.tick_thread_method, args=())
        self.running = False
        self.movement_q = 0
        self.road_min = 0
        self.road_max = road_max
        self.road_end_func = None

    def __str__(self):
        return f'<Train gear={self.gear} movement_q={self.movement_q}' \
               f' current_speed={self.current_speed} pos={self.pos}>'

    def tick(self):
        target_speed = self.max_speed / self.max_gear * self.gear * self.movement_q

        if abs(self.current_speed - target_speed) > self.spt:
            if self.current_speed < target_speed:
                self.current_speed += self.spt
            elif self.current_speed > target_speed:
                self.current_speed -= self.spt
        else:
            self.current_speed = target_speed

        self.pos += self.current_speed / 3.6 / self.tps

        if self.pos < self.road_min:
            self.pos = self.road_min
        elif self.pos > self.road_max:
            self.pos = self.road_max

            if self.road_end_func is not None:
                self.road_end_func()

    def tick_thread_method(self):
        while self.running:
            self.tick()
            sleep(0.1)

    def start(self):
        self.running = True
        self.tick_thread.start()

    def panda3d_start(self):
        self.running = True

        from direct.stdpy import thread

        thread.start_new_thread(function=self.tick_thread_method, args='')

    def bind_road_end(self, func):
        self.road_end_func = func 
