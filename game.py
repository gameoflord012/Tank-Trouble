HOST = '192.168.1.8'  # Replace with server's hostname or IP address
PORT = 65432

import socket
import pygame
import threading
import pickle

from PrimarySettings import *
from sprites import *
from os import path
import random

class Game:
    def __init__(self):
        pygame.init()  # initialize all imported pygame modules
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()  # create an object to help track time
        pygame.display.set_caption(TITLE)
        self.SCORE1 = 0
        self.SCORE2 = 0
        self.data()
        self.is_online = None

    def data(self):
            folder_of_game = path.dirname(__file__)  # location of main.py
            image_folder = path.join(folder_of_game, 'imagefolder')
            Mazefolder = path.join(folder_of_game, 'MAZEFOLDER')
            sound_folder = path.join(folder_of_game, 'snd')
            self.maze = []
            i = 1
            with open(path.join(Mazefolder, 'MAZE{}.txt'.format(i)), 'rt') as f:
                for line in f:
                    self.maze.append(line)
            self.player_image = pygame.image.load(path.join(image_folder, PLAYER_IMAGE)).convert()
            self.player_image.set_colorkey(WHITE)
            self.enemy_image = pygame.image.load(path.join(image_folder, ENEMY_IMAGE)).convert()
            self.enemy_image.set_colorkey(WHITE)
            self.wall_image = pygame.image.load(path.join(image_folder, WALL_IMAGE)).convert()
            self.bullet_image = pygame.image.load(path.join(image_folder, BULLET_IMAGE)).convert()
            self.bullet_image.set_colorkey(WHITE)
            self.shoot_sound = pygame.mixer.Sound(path.join(sound_folder, 'shoot.wav'))
            self.explosion_sound = pygame.mixer.Sound(path.join(sound_folder, 'Explosion20.wav'))
            self.explosion_list = []
            for j in range(9):
                picture_name = 'regularExplosion0{}.png'.format(j)
                self.image_loading_of_explosion = pygame.image.load(path.join(image_folder, picture_name)).convert()
                self.image_loading_of_explosion.set_colorkey(BLACK)
                self.image = pygame.transform.scale(self.image_loading_of_explosion, (50, 50))
                self.explosion_list.append(self.image)

    def new_common(self):
        self.all_sprites = pygame.sprite.Group()
        self.walls = pygame.sprite.Group()  # created the walls group to hold them all
        self.bullets = pygame.sprite.Group()
        for row, tiles in enumerate(self.maze):
            for col, tile in enumerate(tiles):
                if tile == '1':
                    Wall(self, col, row)
                if tile == '*':
                    self.player = Player(self, col, row)
                if tile == '-':
                    self.enemy = Enemy(self, col, row)

    def new_online(self):
        self.new_common()

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((HOST, PORT))

        self.is_online = True
        self.player_id = -1
        self.closing_online = False

        self.online_thread = threading.Thread(target=self.handle_server)
        self.online_thread.start()

    def close_online(self):
        self.all_sprites.empty()
        self.walls.empty()
        self.bullets.empty()

        self.socket.close()
        self.closing_online = True
        self.is_online = False
        self.online_thread.join()

    def new_offline(self):
        self.is_online = False
        self.new_common()

    def close_offline(self):
        self.all_sprites.empty()
        self.walls.empty()
        self.bullets.empty()

    def run(self):
        self.playing = True
        self.Score = False

        while self.playing:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.playing = False
                    break

            self.changing_time = self.clock.tick(FPS) / 1000  # shows how long the previous frame took
            self.events()
            self.update()
            self.draw()
        if self.Score:
            self.SCORE2 = 0
            self.SCORE1 = 0

    def grid(self):
        for x in range(0, WIDTH, SQSIZE):
            pygame.draw.line(self.screen, WHITE, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, SQSIZE):
            pygame.draw.line(self.screen, WHITE, (0, y), (WIDTH, y))

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()

    def update(self):

        new_key_state = pygame.key.get_pressed()

        if self.is_online:
            # send keys data to server
            if self.player_id == 0:
                self.player.last_key_state = new_key_state
                self.socket.sendall(pickle.dumps([self.player.position, self.player.rot, new_key_state[pygame.K_m]]))


            if self.player_id == 1:
                self.enemy.last_key_state = new_key_state
                self.socket.sendall(pickle.dumps([self.enemy.position, self.enemy.rot, new_key_state[pygame.K_m]]))

        else:

            self.player.last_key_state = new_key_state
            self.enemy.last_key_state = new_key_state

        self.all_sprites.update()
        self.hit()

    def hit(self):

        self.hits1 = pygame.sprite.spritecollide(self.player, self.bullets, True, collide)
        for hit in self.hits1:
            if hit:
                Explosion(self, hit.rect.center)
                self.explosion_sound.play()
                self.player.kill()
                self.SCORE1 += 1
                self.playing = False

                self.data()
                self.new()
                if self.SCORE1 == 5:
                    self.show_go_screen1()
        self.hits2 = pygame.sprite.spritecollide(self.enemy, self.bullets, True, collide)
        for hit in self.hits2:
            if hit:
                Explosion(self, hit.rect.center)
                self.explosion_sound.play()
                self.enemy.kill()
                self.SCORE2 += 1
                self.playing = False
                self.data()
                self.new()
                if self.SCORE2 == 5:
                    self.show_go_screen2()

    def draw(self):
        # flip all the thing to screen
        self.screen.fill(BGCOLOR)
        self.grid()
        self.all_sprites.draw(self.screen)
        drawing_text(self.screen, str(self.SCORE1) + ':Green Tank', 25, 150, 710, GREEN)
        drawing_text(self.screen, 'Blue Tank:' + str(self.SCORE2), 25, 900, 710, BLUE)
        pygame.display.flip()

    def quit(self):
        pygame.quit()  # uninitialize all pygame modules
        quit()

    def show_go_screen1(self):
        self.screen.fill(BROWN)
        drawing_text(self.screen, 'Green Tank wins', 80, WIDTH / 2, HEIGHT / 3, GREEN)
        drawing_text(self.screen, 'Press a key to begin or escape key to quit', 40, WIDTH / 2, HEIGHT / 2, WHITE)
        pygame.display.flip()
        self.wait_for_key()

    def show_go_screen2(self):
        self.screen.fill(BROWN)
        drawing_text(self.screen, 'Blue Tank Wins', 80, WIDTH / 2, HEIGHT / 3, BLUE)
        drawing_text(self.screen, 'Press a key to begin or escape key to quit', 40, WIDTH / 2, HEIGHT / 2, WHITE)
        pygame.display.flip()
        self.wait_for_key()

    def wait_for_key(self):
        pygame.event.wait()
        waiting = True
        while waiting:
            self.clock.tick(FPS)  # keep loop running
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                    self.quit()
                if event.type == pygame.KEYUP:
                    self.Score = True
                    waiting = False

    def handle_server(self):
        while not self.closing_online:
            if self.player_id == -1:
                self.socket.send(pickle.dumps([None, None, None])) # need modify
                print("Waiting for player id")

            try:
                byte_data = self.socket.recv(1024)
                if not byte_data:
                    print(f"Online session closed")
                    break
            except:
                print(f"Online session closed")
                break

            try:
                data = pickle.loads(byte_data)
            except pickle.UnpicklingError:
                continue
        
            if self.player_id == -1:
                self.player_id = data[0] 
                print(f"Player id: {self.player_id}")
                continue

            # do nothing if game is not initialized
            if g_game == None:
                continue

            if self.player_id == 0:
                if data[1] != None:
                    g_game.enemy.position = data[1]
                if data[2] != None:
                    g_game.enemy.rot = data[2]
                if data[3] != None:
                    g_game.enemy.should_fire = data[3]

            
            if self.player_id == 1:
                if data[1] != None:
                    g_game.player.position = data[1]
                if data[2] != None:
                    g_game.player.rot = data[2]
                if data[3] != None:
                    g_game.player.should_fire = data[3]


            print(f"Received key states from server")
    
g_game = Game()

g_game.new_offline()
g_game.run()
g_game.close_offline()

g_game.new_online()
g_game.run()
g_game.close_online()


