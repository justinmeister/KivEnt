from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import (StringProperty)
from kivy.clock import Clock
from kivent_cython import GameSystem
import random
from math import radians
from functools import partial


class DebugPanel(Widget):
    fps = StringProperty(None)

    def __init__(self, **kwargs):
        super(DebugPanel, self).__init__(**kwargs)
        Clock.schedule_interval(self.update_fps, .1)

    def update_fps(self, dt):
        self.fps = str(int(Clock.get_fps()))


class AsteroidSystem(GameSystem):
    def create_asteroid(self, pos):
        x, y = pos
        x_vel = random.randint(-100, 100)
        y_vel = random.randint(-100, 100)
        angle = radians(random.randint(-360, 360))
        angular_velocity = radians(random.randint(-150, -150))
        shape_dict = {'inner_radius': 0, 'outer_radius': 32,
                      'mass': 50, 'offset': (0, 0)}
        col_shape = {'shape_type': 'circle', 'elasticity': .5,
                     'collision_type': 1, 'shape_info': shape_dict,
                     'friction': 1.0}
        col_shapes = [col_shape]
        physics_component = {
            'main_shape': 'circle',
            'velocity': (x_vel, y_vel),
            'position': (x, y),
            'angle': angle,
            'angular_velocity': angular_velocity,
            'vel_limit': 250,
            'ang_vel_limit': radians(200),
            'mass': 50, 'col_shapes': col_shapes}
        asteroid_component = {'health': 2}
        create_component_dict = {
            'cymunk-physics': physics_component,
            'physics_renderer': {'texture': 'asteroid.png'},
            'asteroids': asteroid_component}
        component_order = ['cymunk-physics', 'physics_renderer', 'asteroids']
        self.gameworld.init_entity(create_component_dict, component_order)

    def asteroids_collide(self, space, arbiter):
        gameworld = self.gameworld
        entities = gameworld.entities
        asteroid1_id = arbiter.shapes[0].body.data
        asteroid2_id = arbiter.shapes[1].body.data
        asteroid1 = entities[asteroid1_id]
        asteroid2 = entities[asteroid2_id]
        print asteroid1_id, ' hit ', asteroid2_id
        asteroid1_data = asteroid1['asteroids']
        asteroid2_data = asteroid2['asteroids']
        asteroid1_data['health'] -= 1
        asteroid2_data['health'] -= 1
        if asteroid1_data['health'] <= 0:
            Clock.schedule_once(partial(
                gameworld.timed_remove_entity, asteroid1_id))
        if asteroid2_data['health'] <= 0:
            Clock.schedule_once(partial(
                gameworld.timed_remove_entity, asteroid2_id))
        return True


class TestGame(Widget):

    def __init__(self, **kwargs):
        super(TestGame, self).__init__(**kwargs)
        Clock.schedule_once(self._init_game)

    def init_game(self, *args):
        self.setup_states()
        self.set_state()
        self.setup_map()
        self.setup_collision_callbacks()
        self.load_stars()
        self.load_asteroids()
        Clock.schedule_interval(self.update, 0)

    def _init_game(self, *args):
        try:
            self.init_game()
        except:
            print 'failed: rescheduling init'
            Clock.schedule_once(self._init_game)

    def load_asteroids(self):
        asteroid_system = self.gameworld.systems['asteroids']
        for x in xrange(50):
            rand_x = random.randint(0, self.gameworld.currentmap.map_size[0])
            rand_y = random.randint(0, self.gameworld.currentmap.map_size[1])
            asteroid_system.create_asteroid((rand_x, rand_y))

    def load_stars(self):
        star_graphic = 'star.png'
        star_size = (28, 28)
        for x in xrange(50):
            rand_x = random.randint(0, self.gameworld.currentmap.map_size[0])
            rand_y = random.randint(0, self.gameworld.currentmap.map_size[1])
            create_component_dict = {
                'position': {'position': (rand_x, rand_y)},
                'quadtree_renderer': {'texture': star_graphic,
                                      'size': star_size}}
            component_order = ['position', 'quadtree_renderer']
            self.gameworld.init_entity(create_component_dict, component_order)

    def update(self, dt):
        self.gameworld.update(dt)

    def setup_states(self):
        self.gameworld.add_state(state_name='main', systems_added=[
            'quadtree_renderer', 'physics_renderer'],
            systems_removed=[],
            systems_paused=[],
            systems_unpaused=[
                'quadtree_renderer', 'physics_renderer', 'cymunk-physics'],
            screenmanager_screen='main')

    def setup_collision_callbacks(self):
        systems = self.gameworld.systems
        physics = systems['cymunk-physics']
        asteroid_system = systems['asteroids']
        physics.add_collision_handler(
            1, 1, separate_func=asteroid_system.asteroids_collide)

    def set_state(self):
        self.gameworld.state = 'main'

    def setup_map(self):
        self.gameworld.currentmap = self.gameworld.systems['map']


class BasicApp(App):
    def build(self):
        pass

if __name__ == '__main__':
    BasicApp().run()
