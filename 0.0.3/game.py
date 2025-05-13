import pygame
import math
import os
import json

pygame.init()
screen = pygame.display.set_mode((700,400))
running = True
clock = pygame.time.Clock()
dt = 1/30
c = pygame.Vector2(screen.get_width()/2,screen.get_height()/2)

#---------------------------------------------------------------------------------

s_file = 0
dir = os.getcwd()
levels = {}

listdir = os.listdir(os.path.join(dir,'levels'))
level_len = len(listdir)

#---------------------------------------------------------------------------------

font = {}
for i in range(10):
    font[str(i*10)] = pygame.font.SysFont('Courier New',i*10)
for i in range(10):
    font[str((i*10)+8)] = pygame.font.SysFont('Courier New',(i*10)+8)
for i in range(10):
    font[str((i*10)+4)] = pygame.font.SysFont('Courier New',(i*10)+4)
for i in range(10):
    font[str((i*10)+2)] = pygame.font.SysFont('Courier New',(i*10)+2)



freeze = pygame.Vector3()
freeze2 = 1
death_text = [font['40'].render('[SIGNAL LOST]',False,'green'),font['20'].render('CLICK TO RESTART',False,'red'),font['12'].render('[CONNECTION LIMIT]',False,'green')]

class CameraGroup(pygame.sprite.Group):
    def __init__(self, *sprites):
        super().__init__(*sprites)
        self.surface = pygame.display.get_surface()
        self.offset = pygame.Vector2()
    def custom_draw(self):
        global death_text
        if player.rect.bottom < 350:
            self.offset.x = c.x - player.rect.centerx
            self.offset.y = c.y - player.rect.centery

        for sprite in self.sprites():
            self.surface.blit(sprite.image,sprite.rect.topleft+self.offset)
        if player.rect.bottom > 350 or player.dead:
            screen.blit(death_text[0],(c.x-death_text[0].get_width()/2,c.y-death_text[0].get_height()))
            screen.blit(death_text[1],(c.x-death_text[1].get_width()/2,c.y-death_text[1].get_height()+20))

cameragroup = CameraGroup()
class Wall(pygame.sprite.Sprite):
    def __init__(self,width,height,topleft,*groups):
        super().__init__(*groups)
        self.image = pygame.Surface((width,height))
        self.image.fill('black')
        pygame.draw.rect(self.image,'red',pygame.Rect(0,0,width,height),5)
        self.rect = self.image.get_rect()
        self.rect.topleft = topleft
        self.add(cameragroup)
class End(pygame.sprite.Sprite):
    def __init__(self, *groups,topleft):
        super().__init__(*groups)
        self.image = pygame.Surface((20,20))
        self.image.fill('black')
        self.rect = self.image.get_rect()
        self.rect.center = topleft
        pygame.draw.circle(self.image,'yellow',(10,10),10)
        self.add(cameragroup)
class Player(pygame.sprite.Sprite):
    def __init__(self, *groups):
        super().__init__(*groups)
        self.image = pygame.Surface((20,20))
        self.image.fill('black')
        pygame.draw.rect(self.image,'blue',pygame.Rect(0,0,20,20),5)
        self.rect = self.image.get_rect()
        self.rect.topleft = c.x-10,c.y-10
        self.speed = pygame.Vector3()
        self.air = True
        self.dead = False
        self.add(cameragroup)
    def update(self, *args, **kwargs):
        global freeze2
        if mouse['press'][0] and abs(self.speed.y) == 0:
            freeze2 = dir_vector.x/abs(dir_vector.x) if dir_vector.x != 0 else 1
            self.air = True
            self.rect.top -= 1
            self.speed.x = (dir_vector.x)*220
            self.speed.y = (dir_vector.y)*220
            self.speed.z = math.sqrt(self.speed.x**2+self.speed.y**2)
            if self.speed.z != 0:
                freeze.x = self.rect.centerx
                freeze.y = self.rect.centery
                freeze.z = math.atan2(mouse['pos'][1] - c.y, mouse['pos'][0] - c.x)
            print(self.speed.z)
        if mouse['press'][0]:
            if self.rect.bottom > 350 or self.dead:
                self.dead = False
                self.rect.center = c
                self.speed -= self.speed

        self.speed.y -= g
        self.rect.left += self.speed.x*dt
        self.rect.top += self.speed.y*dt
        for wall in colliders:
            if self.rect.colliderect(wall.rect):
                dist = {'t':abs(self.rect.top-wall.rect.bottom),'b':abs(self.rect.bottom-wall.rect.top),'l':abs(self.rect.left-wall.rect.right),'r':abs(self.rect.right-wall.rect.left)}
                if dist['l'] < dist['t'] and dist['l'] < dist['r'] and dist['l'] < dist['b']:
                    self.rect.left = wall.rect.right
                    self.speed.x = 0
                if dist['r'] < dist['l'] and dist['r'] < dist['b'] and dist['r'] < dist['t']:
                    self.rect.right = wall.rect.left
                    self.speed.x = 0
                if dist['t'] < dist['b'] and dist['t'] < dist['l'] and dist['t'] < dist['r']:
                    self.rect.top = wall.rect.bottom
                    self.speed.y = 0
                if dist['b'] < dist['t'] and dist['b'] < dist['r'] and dist['b'] < dist['l']:
                    self.rect.bottom = wall.rect.top
                    self.speed.x -= self.speed.x/2
                    self.speed.y = 0
                    self.air = False
                
        if end != [] and self.rect.colliderect(end[0]):
            self.dead = True
        return super().update(*args, **kwargs)

player = Player()

colliders = pygame.sprite.Group()
end = []
with open(os.path.join(dir,'levels','0.json'),'r') as file:
    walls = json.load(file)
    for wall_data in walls['walls']:
        wall = Wall(wall_data['width'],wall_data['height'],wall_data['topleft'])
        wall.add(colliders)
    end = [End(topleft=walls['end'])]


def get_length(x):
    if abs(x) <= 90:
        y = - (abs(x) * 10 / 90) + 10
    elif abs(x) > 90:
        y = - (-(abs(x) / 9) + 20) + 10
    else:
        y = 0
    if y == 0:
        return 1
    return y

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    screen.fill('black')
    mouse = {'pos':pygame.mouse.get_pos(),'press':pygame.mouse.get_pressed()}

    dir_vector = pygame.Vector3(mouse['pos'][0]-c.x,mouse['pos'][1]-c.y,0)
    dir_vector.z = math.sqrt(dir_vector.x**2+dir_vector.y**2)
    if dir_vector.z != 0:
        dir_vector.x = dir_vector.x/dir_vector.z
        dir_vector.y = dir_vector.y/dir_vector.z

        pygame.draw.line(screen,'green',c,(c.x+(dir_vector.x*30),c.y+(dir_vector.y*30)))
        angle = math.atan2(mouse['pos'][1] - c.y, mouse['pos'][0] - c.x)

    g = -10
    V = player.speed.z/5

    p_x = 0
    p_y = 0


    length = 10
    if player.air:
        length = get_length(math.degrees(freeze.z))
        texts = [font['12'].render(str(math.degrees(freeze.z))+'°',False,'green'),font['12'].render('x: '+str(player.rect.centerx)+' / Vx: '+str(round(player.speed.x,3)),False,'green'),font['12'].render('y: '+str(player.rect.centery)+' / Vy: '+str(round(player.speed.y if player.air else 0.0,3)),False,'green')]
        for i in range(round(150*length)):
            if V != 0:
                x = i*length*freeze2
                y = 1*(x*math.tan(freeze.z) - (g*(x**2)/(2*(40**2)*math.cos(freeze.z)**2)))
                pygame.draw.circle(screen,'red',((freeze.x+x)+cameragroup.offset.x,(freeze.y+y)+cameragroup.offset.y),1)
                if p_y != 0 and p_x != 0:
                    pygame.draw.line(screen,'red',(p_x+cameragroup.offset.x,p_y+cameragroup.offset.y),(freeze.x+x+cameragroup.offset.x,freeze.y+y+cameragroup.offset.y))
                p_x = freeze.x+x
                p_y = freeze.y+y
    else:
        length = get_length(math.degrees(angle))
        texts = [font['12'].render(str(math.degrees(angle))+'°',False,'green'),font['12'].render('x: '+str(player.rect.centerx)+' / Vx: '+str(round(player.speed.x,3)),False,'green'),font['12'].render('y: '+str(player.rect.centery)+' / Vy: '+str(round(player.speed.y if player.air else 0.0,3)),False,'green')]
        for i in range(round(150*length)):
                x = i*length*(dir_vector.x/abs(dir_vector.x)) if dir_vector.x != 0 else i*10
                y = 1*(x*math.tan(angle) - (g*(x**2)/(2*(40**2)*math.cos(angle)**2)))
                pygame.draw.circle(screen,'red',(c.x+x,c.y+y),1)
                if p_y != 0 and p_x != 0:
                    pygame.draw.line(screen,'red',(p_x,p_y),(c.x+x,c.y+y))
                p_x = c.x+x
                p_y = c.y+y
    for i,text in enumerate(texts):
        screen.blit(text,(30,25+i*16))
    print(player.speed.y)
    

    pygame.draw.line(screen,'green',(0,cameragroup.offset.y+350),(700,cameragroup.offset.y+350))
    screen.blit(death_text[2],(c.x-(death_text[2].get_width()/2),cameragroup.offset.y+350))
    player.update()
    cameragroup.custom_draw()

    pygame.display.flip()
    clock.tick(30)/1000