import pygame
from PrimarySettings import *

Screen = pygame.display.set_mode((WIDTH,HEIGHT))

class Button():
    def __init__(self, x, y, image_on, image_off = None, is_sound_button = False, game = None):
        self.image_on = image_on
        self.image_off = image_off
        self.rect = self.image_on.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.clicked = False


    def draw(self):
        action = False
        pos = pygame.mouse.get_pos()

       # Kiểm tra trạng thái âm thanh nếu là nút âm thanh
        

        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and not self.clicked:
                action = True
                self.clicked = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False
        
        Screen.blit(self.image, self.rect)
        return action