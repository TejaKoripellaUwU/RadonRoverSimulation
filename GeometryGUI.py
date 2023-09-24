import json
import math
import time
import Constants
import pygame
import Utils

SCREEN_SIZE = (1700, 1000)
SURFACE_COLOR = (167, 255, 100)
COLOR = (255, 100, 98)
RED = (255, 0, 0)
BLACK = (0,0,0)
WHITE = (255,255,255)

robot_image = pygame.image.load('Sprites/Mecanum.png')
robot_sprite_size = (100, 100)
robot_image = pygame.transform.scale(robot_image, robot_sprite_size)

radiation_image = pygame.image.load("Sprites/RadiationSource.png")
radiation_sprite_size = (25, 25)
radiation_image = pygame.transform.scale(radiation_image, radiation_sprite_size)

with open(Constants.universe_geometry_path, "r") as file:
    file = json.load(file)
    ROBOT_COORDINATES = (int(file["RobotStartX"]), int(file["RobotStartY"]))
    SOURCE_COORDINATES = (int(file["SourceLocations"][0][0]),int(file["SourceLocations"][0][1]))
    UNIVERSE_SIZE = (int(file["UniverseSize"][0]),int(file["UniverseSize"][1]))


def openmc_to_pygame(x, y):
    # print(f"x: {x} y: {y}")
    xConversion = SCREEN_SIZE[0] * x / (UNIVERSE_SIZE[0] * 2)
    yConversion = SCREEN_SIZE[1] * y / (UNIVERSE_SIZE[1] * 2)
    # print(f"xConversion {xConversion} yConversion {yConversion}")

    if yConversion <= 0:
        yConversion = math.fabs(yConversion) + SCREEN_SIZE[1] / 2
    else:
        yConversion = SCREEN_SIZE[1] / 2 - yConversion

    if xConversion < 0:
        xConversion = SCREEN_SIZE[0] / 2 - math.fabs(xConversion)
    else:
        xConversion += SCREEN_SIZE[0]/2
        # print(f"Conversion {xConversion}")

    return (xConversion, yConversion)

def pygame_to_openmc(x,y):
    if y > SCREEN_SIZE[1]/2:
        y = - (y - SCREEN_SIZE[1] / 2)
    else:
        y = SCREEN_SIZE[1]/2 - y

    x-=SCREEN_SIZE[0]/2
    return (x*UNIVERSE_SIZE[0]*2/SCREEN_SIZE[0],y*UNIVERSE_SIZE[1]*2/SCREEN_SIZE[1])


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
        # pygame.draw.circle(self.m_screen,color=RED,center=(self.x,self.y),radius=5)
        orig_rect = radiation_image.get_rect()
        self.rot_image = radiation_image.subsurface(orig_rect).copy()
        self.m_screen.blit(self.rot_image, (self.x-radiation_sprite_size[0]/2, self.y-radiation_sprite_size[1]/2))
        # pygame.display.flip()
class InfoCaption():
    def __init__(self,m_screen):
        self.captions = {}
        self.screen = m_screen


    def create_text(self,key,generator,coords):
        font = pygame.font.Font(None, 30)
        text = font.render(f"{key}:{generator()} ",True,BLACK,SURFACE_COLOR)
        rect = text.get_rect()
        rect.midleft = coords
        self.captions[key] = {"generator":generator,"font":key,"rect":rect}
        self.screen.blit(text,rect)

    def update(self):
        for i in self.captions:
            self.create_text(self.captions[i]["font"],self.captions[i]['generator'],self.captions[i]["rect"].midleft)




class Robot():
    def __init__(self, x, y, max_vel, pdController: PDController, screen,update_func, theta=0):
        self.update_func = update_func
        self.m_PD = pdController
        self.init_x = x-radiation_sprite_size[0]/2
        self.init_y = y-radiation_sprite_size[0]/2
        self.screen = screen
        self.init_theta = theta
        self.max_vel = max_vel
        self.m_screen = screen


    def move_to(self, des_x, des_y):
        # a = lambda: self.init_x
        # # print(a())
        des_x -= radiation_sprite_size[0]/2
        des_y -= radiation_sprite_size[1]/2

        while math.fabs(math.dist((self.init_x, self.init_y), (des_x, des_y))) > 2:
            x_out = self.m_PD.calculate(des_x, self.init_x)
            y_out = self.m_PD.calculate(des_y, self.init_y)

            self.set_chassis_speed(x_out, y_out)

            # update_func()
            # time.sleep(0.1)

    def set_chassis_speed(self, vel_x, vel_y):
        vel_x = Utils.clamp(vel_x, (-self.max_vel, self.max_vel))
        vel_y = Utils.clamp(vel_y, (-self.max_vel, self.max_vel))
        self.init_x += vel_x
        self.init_y += vel_y
        self.update_func()
    def follow_position_data(self):
        with open(str(Constants.pos_log_path), "r") as data:
            self.positon_data = json.load(data)
            for i in self.positon_data["travel_coords"]:
                # print(fr"{openmc_to_pygame(i['x'], i['y'])}")
                self.move_to(*openmc_to_pygame(i["x"], i["y"]))
                # time.sleep(0.01)

                # update_func()

    def draw_prediction(self):
        pygame.draw.circle(self.m_screen,color=RED,center=openmc_to_pygame(*self.positon_data["best_guess"]),radius=10)


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
            caption: str = "RadiationSimulator",
            tick_speed: int = 40,
    ):
        pygame.init()
        pygame.display.set_caption(caption)
        self.display_best_guess = False
        self.screen_size = SCREEN_SIZE
        self.screen = pygame.display.set_mode(self.screen_size)
        self.caption_engine = InfoCaption(self.screen)
        self.clock = pygame.time.Clock()
        self.tick_speed = tick_speed
        self.mainPID = PDController(0.05, 0, time_func=self.clock.get_time)
        self.robot = Robot(*openmc_to_pygame(*ROBOT_COORDINATES), 3, self.mainPID, self.screen,self.update_semantic_states)
        self.gamma_sources = GammaSource(openmc_to_pygame(*SOURCE_COORDINATES),self.screen)
        self.running = True

        # self.surfs = [self.robot.get_blit()]

    def should_quit(self):
        """check for pygame.QUIT event and exit"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
    def create_captions(self):
        self.caption_engine.create_text("x",lambda:round(pygame_to_openmc(self.robot.init_x,0)[0],3),(100,100))
        self.caption_engine.create_text("y", lambda: round(pygame_to_openmc(0, self.robot.init_y)[1], 3), (100, 80))
        self.caption_engine.create_text("guess error",self.guess_error_callback,(100,120))
    def update_semantic_states(self):
        self.screen.fill(SURFACE_COLOR)
        self.gamma_sources.update()
        if self.display_best_guess:
            self.robot.draw_prediction()
        self.robot.update()
        self.caption_engine.update()

        pygame.display.flip()
    def guess_error_callback(self):
        if self.display_best_guess:
            return round(math.dist(SOURCE_COORDINATES,json.load(open(Constants.pos_log_path))["best_guess"]),3)
        else:
            return " "

    def game(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            self.robot.set_chassis_speed(0, -2)
            print("k_up")

        if keys[pygame.K_DOWN]:
            self.robot.set_chassis_speed(0, 2)
            print("k_down")
        if keys[pygame.K_RIGHT]:
            self.robot.set_chassis_speed(2, 0)
            print("k_down")
        if keys[pygame.K_LEFT]:
            self.robot.set_chassis_speed(-2, 2)
            print("k_down")

        if keys[pygame.K_SPACE]:
            self.display_best_guess = False
            print("k_space")
            self.robot.follow_position_data()
            self.display_best_guess = True

        self.update_semantic_states()

    def update(self):
        self.screen.fill(SURFACE_COLOR)
        self.should_quit()
        self.game()

        pygame.display.flip()

        self.clock.tick(self.tick_speed)

    def run(self):
        self.create_captions()
        while self.running:
            self.update()
        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()
