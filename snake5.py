#!/usr/bin/env python
"""
This simple example is used for the line-by-line tutorial
that comes with pygame. It is based on a 'popular' web banner.
Note there are comments here, but for the full explanation,
follow along in the tutorial.
"""


#Import Modules
import os, pygame
from pygame.locals import *
from pygame.compat import geterror
import math
import logging
import random

if not pygame.font: print ('Warning, fonts disabled')
if not pygame.mixer: print ('Warning, sound disabled')

main_dir = os.path.split(os.path.abspath(__file__))[0]
data_dir = os.path.join(main_dir, 'snake_res')

sprite_size = 24
#functions to create our resources
def load_image(name, colorkey=None, w=0, h=0):
    fullname = os.path.join(data_dir, name)
    try:
        image = pygame.image.load(fullname)
        if w!= 0 and h != 0:
            image = pygame.transform.scale(image, (w, h))
    except pygame.error:
        print ('Cannot load image:', fullname)
        raise SystemExit(str(geterror()))
    image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, RLEACCEL)
    return image, image.get_rect()

def load_sound(name):
    class NoneSound:
        def play(self): pass
    if not pygame.mixer or not pygame.mixer.get_init():
        return NoneSound()
    fullname = os.path.join(data_dir, name)
    try:
        sound = pygame.mixer.Sound(fullname)
    except pygame.error:
        print ('Cannot load sound: %s' % fullname)
        raise SystemExit(str(geterror()))
    return sound

class Snake:
    def __init__(self, name, n=30, angle = 90):
        """create snake at the center of the window
        the move the body to correct postion"""
        self.bodys = []
        self.name = name
        self.angle = angle
        self.move = False  #control when the snake start move
        self.speed = 2

        screen = pygame.display.get_surface()
        area = screen.get_rect()
        x = area.x + area.w / 2 - sprite_size / 2 - (n - 1) * sprite_size * math.cos(self.angle * math.pi / 180)
        y = area.y + area.h / 2 - sprite_size / 2 + (n - 1) * sprite_size * math.sin(self.angle * math.pi / 180)
        i = 0
        for i in range(n, 0, -1):
            x2 = area.x + area.w / 2 - sprite_size / 2 - (i - 1) * sprite_size * math.cos(self.angle * math.pi / 180)
            y2 = area.y + area.h / 2 - sprite_size / 2 + (i - 1) * sprite_size * math.sin(self.angle * math.pi / 180)
            distance = math.sqrt((x - x2) * (x - x2) + (y - y2) * (y - y2))
            steps = int(distance / self.speed)
            self.make_body(i - 1, self.angle, x, y, steps, self)

        x2 = area.x + area.w / 2 - sprite_size / 2
        y2 = area.y + area.h / 2 - sprite_size / 2
        distance = math.sqrt((x-x2)*(x-x2)+(y-y2)*(y-y2))
        steps = int(distance/self.speed)
        for j in range(0, steps):
            for i in range(0, n):
                if j < self.bodys[i].initial_steps:
                    if i == 0:
                        self.bodys[i].walk()
                    else:
                        self.bodys[i].follow()
        self.move = True

    def make_body(self, index, angle, x, y, steps, snake):
        snake = SnakeSprite(x, y, angle, index, 'body1.bmp', steps, self)
        self.bodys.insert(0, snake)

    def set_direction(self, angle):
        """set current head direction"""
        if len(self.bodys):
            s = self.bodys[0]
            s.set_direction(angle)

    def get_bodys(self):
        """mget_bodys return spirtes object ot RenderUpdates"""
        return self.bodys

class SnakeSprite(pygame.sprite.Sprite):
    """moves a monkey critter across the screen. it can spin the
       monkey when it is punched."""
    def __init__(self, x, y, angle, n, img, steps, snake):
        pygame.sprite.Sprite.__init__(self) #call Sprite intializer
        self.index = n
        self.image, self.rect = load_image(img, -1, sprite_size, sprite_size)
        self.rect.left = x
        self.rect.top = y
        self.angle = angle
        self.speed = 2
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        self.snake = snake
        self.turns = []             #save the x, y for next body follow
        self.initial_steps = steps  #for move the body's correct position

    def update(self):
        """"walk inside the window sometimes change the angle"""
        if self.index == 0 and len(self.snake.bodys) > 0:
            if self.rect.left < self.area.left or \
                self.rect.right > self.area.right or \
                self.rect.top < self.area.top or \
                self.rect.top + self.rect.height > self.area.top + self.area.height:
                angle = (self.angle + 180)%360
                self.snake.set_direction(angle)
            else:
                if random.randint(0, 99) < 2:
                    angle = random.randrange(0,359, 1)
                    self.snake.set_direction(angle)

        if self.snake.move:
            if self.index == 0:
                self.walk()
            else:
                self.follow()

    def walk(self, save = False):
        x = self.rect.x + round(self.speed * math.cos(self.angle * math.pi / 180))
        y = self.rect.y - round(self.speed * math.sin(self.angle * math.pi / 180))
        self.rect.x = x
        self.rect.y = y
        logging.debug('{} walk- x:{} y:{}'.format(self.index, self.rect.x, self.rect.y))

        if save:
            self.set_direction(self.angle, True)
        else:
            if self.index != len(self.snake.bodys) - 1 and len(self.snake.bodys) > 0:
                self.set_direction(self.angle, True)

    def follow(self):
        """move the body, just follow the previous piece."""
        if self.index < 0:
            return

        pre_sprite = self.snake.bodys[self.index - 1]
        direction = pre_sprite.remove_direction()

        if direction != None:
            angle = direction[0]
            self.angle = angle
            x = direction[1]
            y = direction[2]
            self.rect.x = x
            self.rect.y = y

            if self.index != len(self.snake.bodys) - 1 and len(self.snake.bodys) > 0:
                self.set_direction(self.angle, True)

    def set_direction(self, angle, save = False):
        """set angle and position for next piece"""
        self.angle = angle
        if save == True:
            self.turns.append((angle, self.rect.x, self.rect.y))

    def remove_direction(self):
        """remove the angle and piece when it is used"""
        if len(self.turns) > 0:
            return self.turns.pop(0)
        return None

def main():
    """this function is called when the program starts.
       it initializes everything it needs, then runs in
       a loop until the function returns."""
    logging.basicConfig(filename='snake.log',
                        format="%(asctime)s - %(name)s - %(levelname)s - %(module)s: %(message)s",
                        datefmt="%Y-%m-%d %H:%M:%S",
                        filemode="a", level=logging.DEBUG)
#Initialize Everything
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption('Snake')
    pygame.mouse.set_visible(0)

#Create The Backgound
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((250, 250, 250))

#Put Text On The Background, Centered
    if pygame.font:
        #font = pygame.font.Font(None, 36)
        #text = font.render("Pummel The Chimp, And Win $$$", 1, (10, 10, 10))
        #textpos = text.get_rect(centerx=background.get_width()/2)
        #background.blit(text, textpos)
        pass

#Display The Background
    screen.blit(background, (0, 0))
    pygame.display.flip()

#Prepare Game Objects
    clock = pygame.time.Clock()
    allsprites = pygame.sprite.RenderUpdates()
    screen = pygame.display.get_surface()
    area = screen.get_rect()

    snake = Snake('Kuaikuai')
    snake_bodys =  snake.get_bodys()
    for s in snake_bodys:
        allsprites.add(s)

#Main Loop
    going = True
    while going:
        clock.tick(60)
        #Handle Input Events
        for event in pygame.event.get():
            if event.type == QUIT:
                going = False

        allsprites.update()
        #Draw Everything
        allsprites.clear(screen, background)
        rcs = allsprites.draw(screen)
        pygame.display.update(rcs)
    pygame.quit()
#Game Over

#this calls the 'main' function when this script is executed
if __name__ == '__main__':
    main()
