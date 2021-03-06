from ursina import *
from ursina.prefabs.health_bar import HealthBar
from phys import Train
from direct.stdpy import thread
from random import randint
import sys  # sys.stderr

premium = False


def main():
    app = Ursina()
    
    prepare_window()
    System()

    app.run()


def prepare_window():
    window.title = 'Train emulator'
    window.exit_button.visible = False

    camera.position = Vec3(0, 0, 0)
    camera.rotation_y = 90


class Difficulty:
    EASY = None
    MEDIUM = None
    HARD = None
    
    def __init__(self, obstacle_time_range, score):
        self.obstacle_time_range = obstacle_time_range
        self.score = score


Difficulty.EASY = Difficulty((5000, 20000), 1)
Difficulty.MEDIUM = Difficulty((3000, 10000), 2)
Difficulty.HARD = Difficulty((3000, 5000), 3)


class System(Entity):
    def __init__(self):
        Entity.__init__(self)

        Text.size = 0.1

        self.textures_loaded = 0
        self.info = Text('Press space to start...', origin=(0, 0), size=0.1)
        self.textures_to_load = [
            'gravel',
            'rails',
            'wall',
            'round',
            'arrow',
            'wall2',
            'gauge',
            'needle',
            'nitro'
        ]
        self.texture_folder = 'textures_jpg'
        self.world = World(200, difficulty=None)
        self.train = Train(40, 7, 2.5, 50, 2, 15, self.world.road_length - 1)
        # self.train.pos = 190
        self.difficulty_screen = False
        
        self.gear_text = None
        self.speed_text = None
        self.round = None
        self.arrow_up = None
        self.arrow_down = None
        self.brake_gauge = None
        self.brake_gauge_needle = None
        self.nitro = None

        self.train.bind_road_end(self.win)

    def input(self, key):
        if key == 'escape':
            window.exit_button.on_click()
        elif key == 'space':
            if not self.textures_loaded:
                self.choose_difficulty()
            else:
                self.train.is_brake_active = True
        elif key == 'space up':
            self.train.is_brake_active = False
        elif key == 'a':
            if self.train.movement_q > -1:
                self.train.movement_q -= 1
        elif key == 'd':
            if self.train.movement_q < 1:
                self.train.movement_q += 1
        elif key == 'w':
            if self.train.gear < 7:
                self.train.gear += 1
        elif key == 's':
            if self.train.gear > 0:
                self.train.gear -= 1
        elif key == 'c':
            self.train.nitro()
            self.nitro.enabled = False
        
        elif key == 'e' and self.difficulty_screen:
            self.world.difficulty = Difficulty.EASY
            self.end_difficulty_screen()
            
        elif key == 'm' and self.difficulty_screen:
            self.world.difficulty = Difficulty.MEDIUM
            self.end_difficulty_screen()

        elif key == 'h' and self.difficulty_screen:
            self.world.difficulty = Difficulty.HARD
            self.end_difficulty_screen()
            
        elif key == 'e' and not self.difficulty_screen and premium:
            self.train.gear = 7
            self.train.movement_q = 1

    def choose_difficulty(self):
        self.difficulty_screen = True
        self.info.text = \
                         'Choose difficulty: \n' \
                         '(E)asy,\n(M)edium,\n(H)ard'
    def end_difficulty_screen(self):
        self.difficulty_screen = False
        thread.start_new_thread(function=self.load_textures, args='')
    
    def load_textures(self):
        self.info.text = 'Loading...'
        bar = HealthBar(max_value=len(self.textures_to_load), value=0, position=(-0.5, -0.35, -2), scale_x=1,
                        animation_duration=0, bar_color=color.gray)
        bar.lines.color = color.turquoise

        for i in self.textures_to_load:
            load_texture(i, self.texture_folder)
            bar.value += 1

        self.textures_loaded = True
        self.info.enabled = False
        bar.enabled = False

        self.prepare_ui()
        self.world.create_entities()
        self.train.panda3d_start()

    def update_ui_pos(self):
        round_pos = (0.4 * window.aspect_ratio, -0.35)
        brake_gauge_pos = (-0.25 * window.aspect_ratio)

        if self.gear_text is not None:
            self.gear_text.position = (-0.5 * window.aspect_ratio, -0.35)
        if self.round is not None:
            self.round.position = round_pos
        if self.arrow_up is not None:
            self.arrow_up.position =(round_pos[0] + 0.1, round_pos[1] + 0.1)
        if self.arrow_down is not None:
            self.arrow_down.position = (round_pos[0] - 0.1, round_pos[1] + 0.1)
        if self.brake_gauge is not None:
            self.brake_gauge.position = brake_gauge_pos
        if self.brake_gauge_needle is not None:
            self.brake_gauge_needle.position = brake_gauge_pos
        
    def prepare_ui(self):
        self.gear_text = Text('', size=0.07)
        self.speed_text = Text('', position=(0, -0.35), size=0.05)
        self.round = Entity(model='quad', texture='round', scale=(0.1, 0.1, 0.1),
                            parent=camera.ui)
        self.arrow_up = Entity(model='quad', texture='arrow', scale=(0.05, 0.05, 0.05),
                               parent=camera.ui)
        self.arrow_up.rotation_z = -90
        self.arrow_down = Entity(model='quad', texture='arrow', scale=(0.05, 0.05, 0.05),
                                 parent=camera.ui)
        self.arrow_down.rotation_z = 90
        self.brake_gauge = Entity(model='quad', texture='gauge', scale=(0.2, 0.2, 0.2),
                            parent=camera.ui)
        self.brake_gauge_needle = Entity(model='quad', texture='needle', scale=(0.2, 0.2, 0.2),
                            parent=camera.ui)
        self.nitro = Entity(model='quad', texture='nitro', scale=(0.1, 0.1, 0.1),
                            position=(0.2, -0.3), parent=camera.ui)
        self.update_ui_pos()
        # Used to delete all UI
        self.ui = [self.gear_text, self.speed_text, self.round,
                   self.arrow_up, self.arrow_down, self.brake_gauge, self.brake_gauge_needle,
                   self.nitro]
    def update(self):
        camera.x = self.train.pos

        if self.gear_text is not None:
            self.gear_text.text = str(self.train.gear)
        if self.speed_text is not None:
            self.speed_text.text = str(round(self.train.current_speed)) + ' km/h'
        if self.round is not None:
            self.round.rotation_z = self.train.movement_q * 45
        if self.brake_gauge_needle is not None:
            self.brake_gauge_needle.rotation_z = self.train.brake_left * 250 - 190
            
        for i in self.world.obstacles:
            if camera.intersects(i).hit:
                self.lose()

        self.update_ui_pos()

    def end_game(self, msg):
        self.train.running = False
        Text(msg, position=(-0.1, 0), size=0.1)
        
        for i in self.ui:
            if i is not None:
                i.enabled = False
            else:
                print("Warning: UI element is None, but it shouldn't", file=sys.stderr)

        self.enabled = False
    
    def win(self):
        self.end_game('YOU WIN!')

    def lose(self):
        self.end_game('YOU LOSE!')


class Obstacle(Entity):
    DISAPPEARED_Z_POS = 3 # Z position when disappeared
    
    def __init__(self, pos, difficulty=Difficulty.MEDIUM):
        Entity.__init__(self, model='quad', position=(pos, 0, self.DISAPPEARED_Z_POS),
                        scale=(3, 3, 0.0001), collider='box', texture='wall2')
        self.rotation_y = 90

        self.difficulty = difficulty
        self.appeared = False
        self.main_appear()
        
    def appear(self):
        self.appeared = True
        self.animate('z', 0, duration=1)

    def disappear(self):
        self.appeared = False
        self.animate('z', self.DISAPPEARED_Z_POS, duration=1)

    def main_appear(self):
        self.appear()
        invoke(self.disappear, delay=2)
        
        invoke(self.main_appear, delay=(randint(*self.difficulty.obstacle_time_range) / 1000))


class World:
    def __init__(self, road_length, difficulty=Difficulty.MEDIUM):
        self.left_sides = []
        self.right_sides = []
        self.rails = []
        self.obstacles = []
        self.i = 0

        self.oops = None
        self.element_width = 1
        self.road_length = int(road_length - road_length % self.element_width * 5)
        self.difficulty = difficulty
        
    def add_element(self):
        rails = Entity(model='quad', position=(self.element_width * 5 / 2 + self.i, -0.5, 0),
                       scale=(self.element_width * 5, 1, 1), texture='rails')
        rails.rotation_x = 90
        self.rails.append(rails)

        for i in range(5):
            side_left = Entity(model='quad', position=(self.element_width / 2 + self.i, 0, 0.55),
                               scale=(1, 1, 1), texture='gravel')
            side_right = Entity(model='quad', position=(self.element_width / 2 + self.i, 0, -0.55),
                                scale=(1, 1, 1), texture='gravel')
            side_left.rotation_x = 30
            side_right.rotation_x = 30
            side_right.rotation_y = 180

            self.left_sides.append(side_left)
            self.right_sides.append(side_right)

            self.i += self.element_width

    def create_entities(self):
        camera.collider = BoxCollider(camera, size=(1, 1, 1))
        
        Sky()

        for i in range(self.road_length // 5):
            self.add_element()

        self.oops = Entity(model='quad', position=(self.road_length, 0, 0), scale=(3, 3, 3),
                           texture='wall')
        self.oops.rotation_y = 90

        for i in range(10):
            self.obstacles.append(Obstacle(randint(0, self.road_length), self.difficulty))


if __name__ == '__main__':
    main()
