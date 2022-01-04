from ursina import *
from ursina.prefabs.health_bar import HealthBar
from phys import Train
from direct.stdpy import thread


premium = True


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


class System(Entity):
    def __init__(self):
        Entity.__init__(self)

        Text.size = 0.1

        self.textures_loaded = 0
        self.info = Text('Press space to start...', origin=(0, 0), size=0.1)
        self.textures_to_load = ['gravel', 'rails', 'wall', 'round', 'arrow']
        self.train = Train(40, 7, 2.5)
        self.texture_folder = 'textures_jpg'
        self.world = World(200)
        self.gear_text = None
        self.speed_text = None
        self.round = None
        self.arrow_up = None
        self.arrow_down = None

    def input(self, key):
        if key == 'escape':
            application.quit()
        elif key == 'space':
            if not self.textures_loaded:
                thread.start_new_thread(function=self.load_textures, args='')
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
        elif key == 'e' and premium:
            self.train.gear = 7
            self.train.movement_q = 1

    def load_textures(self):
        self.info.text = 'Loading...'
        bar = HealthBar(max_value=len(self.textures_to_load), value=0, position=(-0.5, -0.35, -2), scale_x=1,
                        animation_duration=0, bar_color=color.gray)

        for i in self.textures_to_load:
            load_texture(i, self.texture_folder)
            bar.value += 1

        self.textures_loaded = True
        self.info.enabled = False
        bar.enabled = False

        self.prepare_ui()
        self.world.create_entities()
        self.train.panda3d_start()

    def prepare_ui(self):
        round_pos = (0.4 * window.aspect_ratio, -0.35)

        self.gear_text = Text('', position=(-0.5 * window.aspect_ratio, -0.35), size=0.07)
        self.speed_text = Text('', position=(0, -0.35), size=0.05)
        self.round = Entity(model='quad', texture='round', scale=(0.1, 0.1, 0.1),
                            position=round_pos, parent=camera.ui)
        self.arrow_up = Entity(model='quad', texture='arrow', scale=(0.05, 0.05, 0.05),
                               position=(round_pos[0] + 0.1, round_pos[1] + 0.1), parent=camera.ui)
        self.arrow_up.rotation_z = -90
        self.arrow_down = Entity(model='quad', texture='arrow', scale=(0.05, 0.05, 0.05),
                                 position=(round_pos[0] - 0.1, round_pos[1] + 0.1), parent=camera.ui)
        self.arrow_down.rotation_z = 90

    def update(self):
        camera.x = self.train.pos

        if self.gear_text is not None:
            self.gear_text.text = str(self.train.gear)
        if self.speed_text is not None:
            self.speed_text.text = str(round(self.train.current_speed)) + ' km/h'
        if self.round is not None:
            self.round.rotation_z = self.train.movement_q * 45


class World:
    def __init__(self, road_length):
        self.left_sides = []
        self.right_sides = []
        self.rails = []
        self.i = 0

        self.oops = None
        self.element_width = 1
        self.road_length = int(road_length - road_length % self.element_width * 5)

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
        Sky()

        for i in range(self.road_length // 5):
            self.add_element()

        self.oops = Entity(model='quad', position=(self.road_length, 0, 0), scale=(3, 3, 3),
                           texture='wall')
        self.oops.rotation_y = 90


if __name__ == '__main__':
    main()
