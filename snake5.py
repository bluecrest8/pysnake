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

if not pygame.font: print ('Warning, fonts disabled')
if not pygame.mixer: print ('Warning, sound disabled')

main_dir = os.path.split(os.path.abspath(__file__))[0]
data_dir = os.path.join(main_dir, 'snake_res')

sprite_size = 16
log_mode = 0

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
    def __init__(self, name, n=40, angle = 90):
        self.bodys = []
        self.name = name
        self.angle = angle
        i = 0
        for i in range(n):
            self.grow()

    def grow(self):
        """grow add a snake piece"""
        count = len(self.bodys)
        if count == 0:
            screen = pygame.display.get_surface()
            area = screen.get_rect()
            x = area.left + area.width / 2 - sprite_size/2
            y = area.top + area.height / 2 - sprite_size/2
            snake = SnakeSprite(x, y, self.angle, count, 'head1.bmp', self)
        else:
            last_body = self.bodys[count - 1]
            x = last_body.rect.left
            y = last_body.rect.top + sprite_size
            angle = last_body.angle
            snake = SnakeSprite(x, y, angle, count, 'body1.bmp', self)
        self.bodys.append(snake)

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
    def __init__(self, x, y, angle, n, img, snake):
        pygame.sprite.Sprite.__init__(self) #call Sprite intializer
        self.index = n
        self.image, self.rect = load_image(img, -1, sprite_size, sprite_size)
        self.rect.left = x
        self.rect.top = y
        self.angle = angle
        self.speed = 5
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        self.image = pygame.transform.rotate(self.image, self.angle)
        self.snake = snake
        self.turns = []

    def update(self):
        """"walk"""
        self._walk()

    def _walk(self):
        """move the body, if is the head or same direction just follow the previous piece.
        if direction is not same with the last piece, we should move it before just follow
        if current piece direction changed we should set the angle and position for next"""
        if self.index == 0:
            x = self.speed * math.cos(self.angle*math.pi/180)
            y = self.speed * math.sin(self.angle*math.pi/180)
            self.rect.move_ip(x, -y)
        else:
            pre_sprite = self.snake.bodys[self.index - 1]
            direction = pre_sprite.get_direction()
            angle = direction[0]
            rc = direction[1]
            if angle == self.angle:
                x = rc.x - sprite_size * math.cos(self.angle * math.pi / 180)
                y = rc.y + sprite_size * math.sin(self.angle * math.pi / 180)
                self.rect.x = x
                self.rect.y = y
            else:
                rc_center = rc.inflate(-sprite_size + 20, -sprite_size + 20)
                if rc_center.collidepoint(self.rect.center):
                    direction = pre_sprite.remove_direction()
                    if direction != None:
                        angle = direction[0]
                        self.rect.center = rc.center
                        self.set_direction(angle)
                else:
                    x = self.speed * math.cos(self.angle * math.pi / 180)
                    y = self.speed * math.sin(self.angle * math.pi / 180)
                    self.rect.move_ip(x, -y)

    def set_direction(self, angle):
        """set angle and position for next piece"""
        if angle != self.angle:
            pre_angle = self.angle
            self.angle = angle
            self.image = pygame.transform.rotate(self.image, self.angle - pre_angle)
            rect = self.rect.copy()
            self.turns.append((angle,rect))

    def get_direction(self):
        """get angle nad position for current piece"""
        if len(self.turns) > 0:
            return self.turns[0]
        return (self.angle, self.rect)

    def remove_direction(self):
        """remove the angle and piece when it is used"""
        if len(self.turns) > 0:
            return self.turns.pop(0)
        return None

def main():
    """this function is called when the program starts.
       it initializes everything it needs, then runs in
       a loop until the function returns."""
    logging.basicConfig(filename='a.log',
                        format="%(asctime)s - %(name)s - %(levelname)s - %(module)s: %(message)s",
                        datefmt="%Y-%m-%d %H:%M:%S",
                        filemode="a", level=logging.DEBUG)
#Initialize Everything
    pygame.init()
    screen = pygame.display.set_mode((1920, 1080))
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
    #whiff_sound = load_sound('whiff.wav')
    #punch_sound = load_sound('punch.wav')
    allsprites = pygame.sprite.RenderUpdates()
    screen = pygame.display.get_surface()
    area = screen.get_rect()

#modified in snake2.py use Snake instead of SnakeSpirte
    snake = Snake('Kuaikuai')
    snake_bodys =  snake.get_bodys()
    for s in snake_bodys:
        allsprites.add(s)
#modified in snake2.py use Snake instead of SnakeSpirte

#Main Loop
    going = True
    while going:
        clock.tick(60)
        #Handle Input Events
        for event in pygame.event.get():
            if event.type == QUIT:
                going = False
            elif event.type == KEYDOWN:
                if event.key == K_RIGHT:
                    snake.set_direction(0)
                elif event.key == K_UP:
                    snake.set_direction(90)
                elif event.key == K_LEFT:
                    snake.set_direction(180)
                elif event.key == K_DOWN:
                    snake.set_direction(270)
                
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
