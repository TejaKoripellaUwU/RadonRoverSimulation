import json
import math
import time
import Constants
import pygame

SCREEN_SIZE = (854, 480)
SURFACE_COLOR = (167, 255, 100)
COLOR = (255, 100, 98)
RED = (255, 0, 0)

robot_image = pygame.image.load('Sprites/Mecanum.png')
robot_sprite_size = (100, 100)
robot_image = pygame.transform.scale(robot_image, robot_sprite_size)

radiation_image = pygame.image.load("Sprites/RadiationSource.png")
radiation_sprite_size = (50, 50)
radiation_image = pygame.transform.scale(radiation_image, radiation_sprite_size)

with open(Constants.universe_geometry_path, "r") as file:
    file = json.load(file)
    ROBOT_COORDINATES = (int(file["RobotStartX"]), int(file["RobotStartY"]))
    SOURCE_COORDINATES = (int(file["SourceLocations"][0][0]),int(file["SourceLocations"][0][1]))
    UNIVERSE_SIZE = (int(file["UniverseSize"][0]),int(file["UniverseSize"][1]))


# size = (150, 150)
# robot_image = pygame.transform.scale(robot_image, size)

def _clamp(value, limits):
    lower, upper = limits
    if value is None:
        return None
    elif (upper is not None) and (value > upper):
        return upper
    elif (lower is not None) and (value < lower):
        return lower
    return value


def openmc_to_pygame(x, y):
    xConversion = SCREEN_SIZE[0] * x / (UNIVERSE_SIZE[0] * 2)
    yConversion = SCREEN_SIZE[1] * y / (UNIVERSE_SIZE[1] * 2)
    print(f"xConversion {xConversion} yConversion {yConversion}")

    if yConversion < 0:
        yConversion = math.fabs(yConversion) + SCREEN_SIZE[1] / 2
    else:
        yConversion = SCREEN_SIZE[1] / 2 - yConversion

    if xConversion < 0:
        xConversion = SCREEN_SIZE[0] / 2 - math.fabs(xConversion)
    else:
        xConversion += SCREEN_SIZE[1]

    return (xConversion, yConversion)


class PDController():
    def __init__(self, kP, kD, time_func=None) -> None:
        self.kP = kP
        self.kD = kD
        if time_func:
            self.time_func = lambda: time_func()
        else:
            self.time_func = time.time
        self.last_time = None
        self.last_error = None

    def calculate(self, setpoint, sensor_reading):
        error = setpoint - sensor_reading
        kP_output = error * self.kP
        kD_output = 0
        if self.last_time and self.kD:
            kD_output = (error - self.last_error) / (self.time_func() - self.last_time) * self.kD

        self.last_time = self.time_func()
        self.last_error = error

        return (kP_output + kD_output)


class GammaSource():
    def __init__(self, coords, screen):
        self.x = coords[0]
        self.y = coords[1]
        self.m_screen = screen

    def update(self):
        orig_rect = radiation_image.get_rect()
        self.rot_image = radiation_image.subsurface(orig_rect).copy()
        self.m_screen.blit(self.rot_image, (self.x, self.y))
        # pygame.display.flip()


class Robot():
    def __init__(self, x, y, max_vel, pdController: PDController, screen, theta=0):
        self.m_PD = pdController
        self.init_x = x
        self.init_y = y
        self.screen = screen
        self.init_theta = theta
        self.max_vel = max_vel
        self.m_screen = screen

    def move_to(self, des_x, des_y, update_func):
        while math.fabs(math.dist((self.init_x, self.init_y), (des_x, des_y))) > 1:
            x_out = self.m_PD.calculate(des_x, self.init_x)
            y_out = self.m_PD.calculate(des_y, self.init_y)

            self.set_chassis_speed(x_out, y_out, update_func)
            # update_func()
            # time.sleep(0.1)

    def set_chassis_speed(self, vel_x, vel_y, update_func):
        vel_x = _clamp(vel_x, (-self.max_vel, self.max_vel))
        vel_y = _clamp(vel_y, (-self.max_vel, self.max_vel))
        self.init_x += vel_x
        self.init_y += vel_y
        update_func()

    def follow_position_data(self, update_func):
        with open(str(Constants.pos_log_path), "r") as data:
            self.positon_data = json.load(data)
            for i in self.positon_data["travel_coords"]:
                print(fr"{openmc_to_pygame(i['x'], i['y'])}")
                self.move_to(*openmc_to_pygame(i["x"], i["y"]), update_func)
                # update_func()

    def update(self):
        orig_rect = robot_image.get_rect()
        self.rot_image = pygame.transform.rotate(robot_image, self.init_theta)
        rot_rect = orig_rect.copy()
        rot_rect.center = self.rot_image.get_rect().center
        self.rot_image = self.rot_image.subsurface(rot_rect).copy()
        self.m_screen.blit(self.rot_image, (self.init_x, self.init_y))


class Game:
    def __init__(
            self,
            caption: str = "pygame-starter",
            tick_speed: int = 30,
    ):
        pygame.init()
        pygame.display.set_caption(caption)

        self.screen_size = SCREEN_SIZE
        self.screen = pygame.display.set_mode(self.screen_size)
        self.clock = pygame.time.Clock()
        self.tick_speed = tick_speed
        self.mainPID = PDController(0.007, 0, time_func=self.clock.get_time)
        self.robot = Robot(*openmc_to_pygame(*ROBOT_COORDINATES), 1, self.mainPID, self.screen)
        self.gamma_sources = GammaSource(openmc_to_pygame(*SOURCE_COORDINATES),self.screen)
        self.running = True
        
        # self.surfs = [self.robot.get_blit()]

    def should_quit(self):
        """check for pygame.QUIT event and exit"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def update_semantic_states(self):
        self.screen.fill(SURFACE_COLOR)
        self.gamma_sources.update()
        self.robot.update()
        pygame.display.flip()


    def game(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            self.robot.set_chassis_speed(0, -2, self.update_semantic_states)
            print("k_up")

        if keys[pygame.K_DOWN]:
            self.robot.set_chassis_speed(0, 2, self.update_semantic_states)
            print("k_down")

        if keys[pygame.K_SPACE]:
            print("k_space")
            self.robot.follow_position_data(self.update_semantic_states)

        self.update_semantic_states()

    def update(self):
        self.screen.fill(SURFACE_COLOR)
        self.should_quit()
        self.game()

        pygame.display.flip()

        self.clock.tick(self.tick_speed)

    def run(self):
        while self.running:
            self.update()
        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()
