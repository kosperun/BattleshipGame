"""Module for buttons."""

from typing import Optional

import pygame

from elements.constants import BLACK, BLOCK_SIZE, GREEN_BLUE, UPPER_MARGIN, WHITE
from graphics.drawing import screen

class Button:
    """
    Creates buttons and prints explanatory message for them
    ----------
    Attributes:
        __title (str): Button's name (title)
        __message (str): explanatory message to print on screen
        __x_start (int): horizontal offset where to start drawing button
        __y_start (int): vertical offset where to start drawing button
        __rect_for_draw (tuple of four ints): button's rectangle to be drawn
        rect (pygame Rect): pygame Rect object
        __rect_for_button_title (tuple of two ints): rectangle within button to print text in it
        __color (tuple): color of button (Default is BLACK, hovered is GREEN_BLUE, disabled is LIGHT_GRAY)
    ----------
    Methods:
    draw(): Draws button as a rectangle of color (default is BLACK)
    change_color_on_hover(): Draws button as a rectangle of GREEN_BLUE color
    print_message(): Prints explanatory message next to button
    """

    def __init__(
        self, x_offset: int, button_title: str, message_to_show: str, font: pygame.font.Font, color: tuple = BLACK
    ) -> None:
        self.__title = button_title
        self.__font = font
        self.__title_width, self.__title_height = self.__font.size(self.__title)
        self.__message = message_to_show
        self.__button_width = self.__title_width + BLOCK_SIZE
        self.__button_height = self.__title_height + BLOCK_SIZE
        self.__x_start = x_offset
        self.__y_start = UPPER_MARGIN + 10 * BLOCK_SIZE + self.__button_height
        self.__rect_for_draw = self.__x_start, self.__y_start, self.__button_width, self.__button_height
        self.rect = pygame.Rect(self.__rect_for_draw)
        self.__rect_for_button_title = (
            self.__x_start + self.__button_width / 2 - self.__title_width / 2,
            self.__y_start + self.__button_height / 2 - self.__title_height / 2,
        )
        self.__color = color

    def draw(self, color: Optional[tuple] = None, text_color: tuple = WHITE) -> None:
        """
        Draws button as a rectangle of color (default is BLACK)
        Args:
            color (tuple, optional): Button's color. Defaults to None (BLACK).
        """
        if not color:
            color = self.__color
        pygame.draw.rect(screen, color, self.__rect_for_draw)
        text_to_blit = self.__font.render(self.__title, True, text_color)
        screen.blit(text_to_blit, self.__rect_for_button_title)

    def change_color_on_hover(self, hover_color: tuple = GREEN_BLUE) -> None:
        """
        Draws button as a rectangle of GREEN_BLUE color
        """
        mouse = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse):
            self.draw(hover_color)

    def print_message(self, text_color: tuple = BLACK) -> None:
        """
        Prints explanatory message next to button
        """
        message_width, message_height = self.__font.size(self.__message)
        rect_for_message = (
            self.__x_start / 2 - message_width / 2,
            self.__y_start + self.__button_height / 2 - message_height / 2,
        )
        text = self.__font.render(self.__message, True, text_color)
        screen.blit(text, rect_for_message)
