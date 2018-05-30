import os
import sys
import pygame as pg
from game import Game

CAPTION = "Expressions"
SCREEN_SIZE = (500, 500)


def main():
    """
    Initialize; create an App; and start the main loop.
    """
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    pg.init()
    pg.display.set_caption(CAPTION)
    pg.display.set_mode(SCREEN_SIZE)
    Game().main_loop()
    pg.quit()
    sys.exit()


if __name__ == '__main__':
    main()
