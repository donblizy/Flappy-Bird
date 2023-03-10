import random

import pygame
from pygame.locals import *

pygame.init()

clock = pygame.time.Clock()
fps = 60

screen_width = 864
screen_height = 936

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Flappy Andy')

# define font
font = pygame.font.SysFont("Bauhaus 93", 60)

# define colours
white = (255, 255, 255)
black = (0, 0, 0)

# define game variables
ground_scroll = 0
scroll_speed = 4
is_flying = False
is_game_over = False
pipe_gap = 150
pipe_spawn_frequency = 1500  # 1.5 seconds
last_pipe = pygame.time.get_ticks() - pipe_spawn_frequency
score = 0
score_point = False

# load images
bg = pygame.image.load('assets/environment/bg.png')
ground_img = pygame.image.load('assets/environment/ground.png')
button = pygame.image.load("assets/ui/restart.png")
intro = pygame.image.load("assets/ui/intro.png")
end = pygame.image.load("assets/ui/end.png")


def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


def reset_game():
    pipe_group.empty()
    flappy.rect.x = 100
    flappy.rect.y = int(screen_height / 2)
    score = 0
    return score


class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        self.index = 0
        self.counter = 0
        for num in range(1, 4):
            img = pygame.image.load(f'assets/character/bird{num}.png')
            self.images.append(img)
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.velocity = 0
        self.clicked = False
        self.jump_sound = pygame.mixer.Sound("assets/sounds/jump.wav")
        self.jump_sound.set_volume(0.3)
        self.music = pygame.mixer.Sound("assets/sounds/music.wav")
        self.music.set_volume(0.6)
        self.music.play(loops=-1)

    def update(self):

        # handle gravity
        if is_flying:
            self.velocity += 0.5
            if self.velocity > 8:
                self.velocity = 8
            if self.rect.bottom < 768:
                self.rect.y += int(self.velocity)
        if is_game_over == False:
            # handle flap
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked = True
                self.jump_sound.play()
                self.velocity = -10
            if pygame.mouse.get_pressed()[0] == 0 and self.clicked == True:
                self.clicked = False

            # handle the flap animation
            self.counter += 1
            flap_cooldown = 5

            if self.counter > flap_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images):
                    self.index = 0
            self.image = self.images[self.index]

            # handle bird facing direction
            self.image = pygame.transform.rotate(
                self.images[self.index], self.velocity * -3)
        else:
            self.image = pygame.transform.rotate(
                self.images[self.index], -90)


class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, position):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("assets/obstacles/pipe.png")
        self.rect = self.image.get_rect()
        # position 1 is from the top, -1 is from the bot
        if position == 1:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x, y - int(pipe_gap / 2)]
        if position == -1:
            self.rect.topleft = [x, y + int(pipe_gap / 2)]

    def update(self):
        self.rect.x -= scroll_speed
        # delete old pipes to help with memory
        if self.rect.right < -20:
            self.kill()


class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def draw(self):
        action = False
        # get mouse position
        pos = pygame.mouse.get_pos()
        # check if mouse is over the button
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1:
                action = True
        # draw button
        screen.blit(self.image, (self.rect.x, self.rect.y))
        screen.blit(end, (screen_width // 2 - 110, screen_height // 2 - 50))
        return action


bird_group = pygame.sprite.Group()
pipe_group = pygame.sprite.Group()

flappy = Bird(100, int(screen_height / 2))

bird_group.add(flappy)
restart_button = Button(screen_width // 2 - 50,
                        screen_height // 2 - 100, button)


run = True
while run:

    clock.tick(fps)

    # draw background
    screen.blit(bg, (0, 0))

    # draw bird
    bird_group.draw(screen)
    bird_group.update()

    # draw pipes
    pipe_group.draw(screen)

    # draw ground
    screen.blit(ground_img, (ground_scroll, 768))

    if is_flying == False and is_game_over == False:
        screen.blit(intro, (432, 0))

        # check score
    if len(pipe_group) > 0:
        if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left\
                and bird_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right\
                and score_point == False:
            score_point = True
        if score_point == True:
            if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right:
                score += 1
                score_point = False

    draw_text(str(score), font, white, int(screen_width/2), 20)

    # check if bird hit a pipe
    if pygame.sprite.groupcollide(bird_group, pipe_group, False, False) or flappy.rect.top < 0:
        is_game_over = True

    # check if bird hit ground
    if flappy.rect.bottom > 768:
        is_game_over = True
        is_flying = False

    if is_game_over == False and is_flying == True:
        # generate new pipes
        time_now = pygame.time.get_ticks()
        if time_now - last_pipe > pipe_spawn_frequency:
            pipe_height = random.randint(-100, 100)
            btm_pipe = Pipe(screen_width, int(
                screen_height / 2) + pipe_height, -1)
            top_pipe = Pipe(screen_width, int(
                screen_height / 2) + pipe_height, 1)
            pipe_group.add(btm_pipe)
            pipe_group.add(top_pipe)
            last_pipe = time_now

        # scroll the ground under background
        ground_scroll -= scroll_speed
        if abs(ground_scroll) > 35:
            ground_scroll = 0

        pipe_group.update()

    # check for game over and reset
    if is_game_over == True:
        if restart_button.draw() == True:

            is_game_over = False
            score = reset_game()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        if event.type == pygame.MOUSEBUTTONDOWN and is_flying == False and is_game_over == False:
            is_flying = True

    pygame.display.update()

pygame.quit()
