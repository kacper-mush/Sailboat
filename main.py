import copy
import pygame
import random
import sys
from pygame.locals import *
from point import Point
from enum import Enum


# Simple state machine
class Mouse:
    class State(Enum):
        IDLE = 0,
        JUST_PRESSED = 1,
        DRAGGED = 2,
        LET_OFF = 3

    def __init__(self):
        self.state = Mouse.State.IDLE

    def update(self, is_lmb_pressed):
        if is_lmb_pressed:
            if self.state == Mouse.State.IDLE or self.state == Mouse.State.LET_OFF:
                self.state = Mouse.State.JUST_PRESSED
            elif self.state == Mouse.State.JUST_PRESSED:
                self.state = Mouse.State.DRAGGED
        else:
            if self.state == Mouse.State.JUST_PRESSED or self.state == Mouse.State.DRAGGED:
                self.state = Mouse.State.LET_OFF
            elif self.state == Mouse.State.LET_OFF:
                self.state = Mouse.State.IDLE


class Boat:
    def __init__(self, points, scale_factor, starting_pos, color, thickness):
        self.points = copy.deepcopy(points)
        self.scale(scale_factor)
        self.translate(starting_pos)
        self.color = color
        self.thickness = thickness

    def copy_points(self, other_boat):
        self.points = copy.deepcopy(other_boat.points)

    def overlaps(self, other_boat, threshold):
        for point, other_point in zip(self.points, other_boat.points):
            if not point.is_close_to(other_point, threshold):
                return False
        return True

    def draw(self, surface):
        for idx, point in enumerate(self.points):
            pygame.draw.line(surface, self.color, point.tup(), self.points[idx - 1].tup(), self.thickness)

    def translate(self, translation):
        for point in self.points:
            point.translate(translation)

    def scale(self, scale_factor):
        for point in self.points:
            point.scale(scale_factor)

    def flip(self, start_point, end_point):
        for point in self.points:
            point.flip_by_line(start_point, end_point)

    # Flips around an axis constructed from this boat's points. It flips but not too far away from its current location
    def pseudo_random_flip(self):
        start_point = self.points[random.randint(0, len(self.points) - 1)]
        while True:
            end_point = self.points[random.randint(0, len(self.points) - 1)]
            if not start_point == end_point:
                break

        self.flip(start_point, end_point)


# ------- Setup for boats
# setup points are the shape of a boat, they can be then translated, scaled, etc.
SETUP_POINTS = [Point(50, 0), Point(83, 36), Point(96, 76), Point(50, 76), Point(50, 83), Point(98, 85), Point(88, 98),
                Point(20, 98), Point(1, 79), Point(42, 80)]
BOAT_SCALE_FACTOR = 1.5
BOAT_STARTING_POS = Point(800, 400)
BOAT_FINAL_POS = Point(100, 100)
WIN_THRESHOLD = 10  # +- amount that the game will accept as a win if the point is near the final position

MAIN_BOAT_THICKNESS = 5
FINAL_BOAT_THICKNESS = 2
GHOST_BOAT_THICKNESS = 1
LINE_THICKNESS = 2

# ------- Colors
TEXT_COLOR = Color(201, 22, 73)
TEXT_BACKGROUND_COLOR = Color(182, 212, 227)
BACKGROUND_COLOR = Color(50, 140, 140)
MAIN_BOAT_COLOR = Color(0, 0, 0)
FINAL_BOAT_COLOR = Color(71, 71, 71)
GHOST_BOAT_COLOR = Color(255, 0, 0)
LINE_COLOR = Color(70, 199, 156)

# Setup Pygame
WINDOW_WIDTH, WINDOW_HEIGHT = 1200, 800
FPS = 60
pygame.init()
fpsClock = pygame.time.Clock()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Sailboat')


# Text setup
BIG_FONT_SIZE = 32
SMALL_FONT_SIZE = 20
FONT = 'freesansbold.ttf'
WIN_TEXT_STR = 'SAILBOAT MATCHED! (press X to reset)'
RESET_TEXT_STR = 'Press X to reset.'
HINT_TEXT_STR = 'Press H to toggle hints.'
# -------
BIG_FONT = pygame.font.Font(FONT, BIG_FONT_SIZE)
SMALL_FONT = pygame.font.Font(FONT, SMALL_FONT_SIZE)
WIN_TEXT = BIG_FONT.render(WIN_TEXT_STR, True, TEXT_COLOR, TEXT_BACKGROUND_COLOR)
RESET_TEXT = SMALL_FONT.render(RESET_TEXT_STR, True, TEXT_COLOR, TEXT_BACKGROUND_COLOR)
HINT_TEXT = SMALL_FONT.render(HINT_TEXT_STR, True, TEXT_COLOR, TEXT_BACKGROUND_COLOR)
WIN_TEXT_RECT = WIN_TEXT.get_rect()
RESET_TEXT_RECT = RESET_TEXT.get_rect()
HINT_TEXT_RECT = HINT_TEXT.get_rect()
WIN_TEXT_RECT.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
RESET_TEXT_RECT.topright = (WINDOW_WIDTH, 0)
HINT_TEXT_RECT.topright = (WINDOW_WIDTH, SMALL_FONT_SIZE)


def setup_boats():
    main_boat = Boat(SETUP_POINTS, BOAT_SCALE_FACTOR, BOAT_STARTING_POS, MAIN_BOAT_COLOR, MAIN_BOAT_THICKNESS)
    main_boat.pseudo_random_flip()
    final_boat = Boat(SETUP_POINTS, BOAT_SCALE_FACTOR, BOAT_FINAL_POS, FINAL_BOAT_COLOR, FINAL_BOAT_THICKNESS)
    ghost_boat = Boat(SETUP_POINTS, BOAT_SCALE_FACTOR, BOAT_STARTING_POS, GHOST_BOAT_COLOR, GHOST_BOAT_THICKNESS)
    return main_boat, final_boat, ghost_boat


def main():
    main_boat, final_boat, ghost_boat = setup_boats()

    start_point = Point(0, 0)
    end_point = Point(0, 0)

    mouse = Mouse()
    hints_on = True

    # Game loop.
    while True:
        # Event handling
        for event in pygame.event.get():
            if event.type == KEYUP:
                if event.key == K_x:
                    main_boat, final_boat, ghost_boat = setup_boats()
                if event.key == K_h:
                    hints_on = not hints_on
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        # Update
        user_won = main_boat.overlaps(final_boat, WIN_THRESHOLD)
        if not user_won:
            mouse_pos = pygame.mouse.get_pos()
            mouse.update(pygame.mouse.get_pressed()[0])

            if mouse.state == Mouse.State.JUST_PRESSED:
                start_point = Point(*mouse_pos)
            elif mouse.state == Mouse.State.DRAGGED:
                end_point = Point(*mouse_pos)
                ghost_boat.copy_points(main_boat)
                ghost_boat.flip(start_point, end_point)
            elif mouse.state == Mouse.State.LET_OFF:
                main_boat.flip(start_point, end_point)

        # Draw
        screen.fill(BACKGROUND_COLOR)
        final_boat.draw(screen)
        main_boat.draw(screen)
        if mouse.state == Mouse.State.DRAGGED:
            pygame.draw.line(screen, LINE_COLOR, start_point.tup(), end_point.tup(), LINE_THICKNESS)
            if hints_on:
                ghost_boat.draw(screen)
        if user_won:
            screen.blit(WIN_TEXT, WIN_TEXT_RECT)

        screen.blit(RESET_TEXT, RESET_TEXT_RECT)
        screen.blit(HINT_TEXT, HINT_TEXT_RECT)

        pygame.display.flip()
        fpsClock.tick(FPS)


if __name__ == "__main__":
    main()
