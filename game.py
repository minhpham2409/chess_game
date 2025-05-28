from os import environ

environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

import pygame
from src.MenuScreen import MenuScreen
from src.PlayMode import PlayMode
from src.PlayAIMode import PlayAIMode
from src.config import *


class GameController:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Cờ vua AI")
        self.icon = pygame.image.load('data/images/icon.jpg')

        pygame.display.set_icon(self.icon)
        self.screen = pygame.display.set_mode((WIDTH_WINDOW, HEIGHT_WINDOW))

    def run(self):
        # Entry point for game
        self.__inMenuScreen()

    def __inMenuScreen(self):
        menuScreen = MenuScreen(self.screen)

        # Apply function handler for each button
        menuScreen.menu.get_widget('PvP').set_onreturn(self.__inPlayScreen)
        menuScreen.menu.get_widget('PvC').set_onreturn(self.__inPlayAIScreen)
        menuScreen.menu.get_widget('AIVsAI').set_onreturn(self.__inPlayAIVsAIScreen)

        # Start menu loop
        menuScreen.mainLoop()

    def __inPlayScreen(self):
        playMode = PlayMode()
        playMode.mainLoop()

    def __inPlayAIScreen(self):
        playAIMode = PlayAIMode()
        playAIMode.mainLoop()
        self.screen = pygame.display.set_mode((WIDTH_WINDOW, HEIGHT_WINDOW))

    def __inPlayAIVsAIScreen(self):
        from src.PlayAIVsAIMode import PlayAIVsAIMode
        playAIVsAIMode = PlayAIVsAIMode()
        playAIVsAIMode.mainLoop()
        self.screen = pygame.display.set_mode((WIDTH_WINDOW, HEIGHT_WINDOW))


if __name__ == "__main__":
    game = GameController()
    game.run()
