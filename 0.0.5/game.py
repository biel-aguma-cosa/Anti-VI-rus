import pygame
import math
import os
import sys
import json
import asyncio

pygame.init()
screen = pygame.display.set_mode((700,400))
running = True
clock = pygame.time.Clock()
dt = 1/30
c = pygame.Vector2(screen.get_width()/2,screen.get_height()/2)

#---------------------------------------------------------------------------------

s_file = 0
direct = os.path.dirname(os.path.abspath(sys.argv[0]))
levels = {}
print(direct)
listdir = os.listdir(os.path.join(direct,'levels'))
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
death_text_2 = [font['40'].render('[PROBE LOST]',False,'green'),font['20'].render('CLICK TO RESTART',False,'red'),font['12'].render('[CONNECTION LIMIT]',False,'green')]
win_text = [font['40'].render('[ATTACKER NEUTRALIZED]',False,'green'),font['20'].render('CLICK TO CONTINUE',False,'red')]

test_button = [font['20'].render('[butaum]',False,'red'),font['40'].render('hihihihihihihi',False,'blue')]

def test():
    print('a')

class Button(pygame.sprite.Sprite):
    def __init__(self,img,pos,function = test, *groups):
        super().__init__(*groups)
        self.img = [img[0],img[1]]
        self.image = img[0]
        self.function = function
        self.rect = self.image.get_rect(center = pos)
    def update(self):
        global mouse
        global event
        if self.rect.collidepoint(mouse['pos']):
            self.image = self.img[1]
            pos = self.rect.center
            self.rect = self.image.get_rect(center=pos)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.function()
                    pygame.time.delay(100)
        else:
            self.image = self.img[0]
            pos = self.rect.center
            self.rect = self.image.get_rect(center=pos)

class CameraGroup(pygame.sprite.Group):
    def __init__(self, *sprites):
        super().__init__(*sprites)
        self.surface = pygame.display.get_surface()
        self.offset = pygame.Vector2()
    def custom_draw(self):
        global death_text
        global player
        if player.rect.bottom < 340:
            self.offset.x = c.x - player.rect.centerx
            self.offset.y = c.y - player.rect.centery

        for sprite in self.sprites():
            if not((type(sprite) == Player or type(sprite) == End) and player.passed):
                self.surface.blit(sprite.image,sprite.rect.topleft+self.offset)
            elif player.dead and player.rect.bottom < 350:
                self.offset == 0
                player.speed.x = 0
                player.speed.y = 0
                player.rect.centerx = c.x
                player.rect.centery = c.y
            elif player.passed:
                self.offset == 0
                player.speed.x = 0
                player.speed.y = 0
                player.rect.centerx = c.x
                player.rect.centery = c.y
        
        pygame.draw.line(self.surface,'green',(0,cameragroup.offset.y+350),(700,cameragroup.offset.y+350))
        self.surface.blit(death_text[2],(c.x-(death_text[2].get_width()/2),cameragroup.offset.y+350))

        if player.dead and player.rect.bottom > 350:
            self.surface.blit(death_text[0],(c.x-death_text[0].get_width()/2,c.y-death_text[0].get_height()))
            self.surface.blit(death_text[1],(c.x-death_text[1].get_width()/2,c.y-death_text[1].get_height()+20))
        elif player.dead:
            self.surface.blit(death_text_2[0],(c.x-death_text_2[0].get_width()/2,c.y-death_text_2[0].get_height()))
            self.surface.blit(death_text_2[1],(c.x-death_text_2[1].get_width()/2,c.y-death_text_2[1].get_height()+20))
        elif player.passed:
            self.surface.blit(win_text[0],(c.x-win_text[0].get_width()/2,c.y-win_text[0].get_height()))
            self.surface.blit(win_text[1],(c.x-win_text[1].get_width()/2,c.y-win_text[1].get_height()+20))

class Wall(pygame.sprite.Sprite):
    def __init__(self,width,height,topleft,*groups):
        super().__init__(*groups)
        self.image = pygame.Surface((width,height))
        self.image.fill('black')
        pygame.draw.rect(self.image,'red',pygame.Rect(0,0,width,height),5)
        self.rect = self.image.get_rect()
        self.rect.topleft = topleft
class End(pygame.sprite.Sprite):
    def __init__(self, *groups,topleft):
        super().__init__(*groups)
        self.image = pygame.Surface((20,20))
        self.image.fill('black')
        self.rect = self.image.get_rect()
        self.rect.topleft = topleft
        pygame.draw.circle(self.image,'yellow',(10,10),10)
        pygame.draw.circle(self.image,'black',(10,10),6)
        pygame.draw.rect(self.image,'yellow',pygame.Rect(4,4,12,6))
        pygame.draw.circle(self.image,'black',(6,6),3)
        pygame.draw.circle(self.image,'black',(14,6),3)
class Enemy(pygame.sprite.Sprite):
    def __init__(self,topleft,points):
        super().__init__()
        self.image = pygame.Surface((20,20))
        self.image.fill('black')
        self.rect = self.image.get_rect()
        self.rect.topleft = topleft
        pygame.draw.circle(self.image,'yellow',(10,10),10)
        pygame.draw.polygon(self.image,'black',((4,14),(8,10),(11,10),(16,14)))
        pygame.draw.circle(self.image,'black',(6,6),3)
        pygame.draw.circle(self.image,'black',(14,6),3)

        self.points = []
        self.vectors = []
        self.target = 0
        for i,p in enumerate(points):
            self.points.append(p)
            if i < len(points)-1:
                self.vectors.append(pygame.Vector2(points[i+1][0]-p[0],points[i+1][1]-p[1]))
            else:
                self.vectors.append(pygame.Vector2(p[0]-points[0][0],p[1]-points[0][1]))
        for vector in self.vectors:
            vector = vector.normalize()
    def update(self, *args, **kwargs):
        self.target %= len(self.points)
        
        if self.target < len(self.points)-1:
            if pygame.Vector2(self.rect.centerx,self.rect.centery).distance_to(self.points[self.target+1]) < 0.5:
                self.rect.center = self.points[self.target+1]
                self.target += 1
            else:
                self.rect.center += self.vectors[self.target]*dt/2
        elif self.target == len(self.points)-1:
            if pygame.Vector2(self.rect.centerx,self.rect.centery).distance_to(self.points[0]) < 0.5:
                self.rect.center = self.points[0]
                self.target += 1
            else:
                self.rect.center += self.vectors[self.target]*dt/2

        return super().update(*args, **kwargs)

class Player(pygame.sprite.Sprite):
    def __init__(self, *groups):
        super().__init__(*groups)
        self.image = pygame.Surface((20,20))
        self.image.fill('black')
        pygame.draw.rect(self.image,'blue',pygame.Rect(0,0,20,20),5)
        self.rect = self.image.get_rect()
        self.rect.center = c
        self.speed = pygame.Vector3()
        self.air = True
        self.passed = False
        self.dead = False
        self.add(cameragroup)
    def update(self, *args, **kwargs):
        global lvl
        global end
        global levels
        global freeze2
        global md
        if self.rect.bottom > 350:
            self.dead = True
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and abs(self.speed.y) == 0:
                freeze2 = dir_vector.x/abs(dir_vector.x) if dir_vector.x != 0 else 1
                self.air = True
                self.rect.top -= 1
                self.speed.x = (dir_vector.x)*220
                self.speed.y = (dir_vector.y)*220
                self.speed.z = 220
                if self.speed.z != 0:
                    freeze.x = self.rect.centerx
                    freeze.y = self.rect.centery
                    freeze.z = math.atan2(mouse['pos'][1] - c.y, mouse['pos'][0] - c.x)
                print(self.speed.z)
            if event.button == 1 and md == False:
                if self.dead:
                    self.rect.center = c
                    self.speed -= self.speed
                    self.dead = False
                elif self.passed:
                    lvl += 1
                    self.passed = False
                    self.speed -= self.speed


        self.speed.y -= g
        self.rect.centerx += self.speed.x*dt
        self.rect.centery += self.speed.y*dt
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
                
        if end != [] and self.rect.colliderect(end[0]) and not(self.passed):
            for wall in colliders:
                end[0].kill()
                wall.kill()
            self.passed = True
        return super().update(*args, **kwargs)

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

end = []
gaming = False
event = None
p_lvl = 0
lvl = 0
g = -10
V = 0
p_x = 0
p_y = 0
md = False

def game():
    global gaming
    gaming = True

cameragroup = CameraGroup()
menu = pygame.sprite.Group(Button(test_button,(0,0),game))
player = Player()
colliders = pygame.sprite.Group()
enemies = pygame.sprite.Group()

levels = []
babi = []
for i, level in enumerate(os.listdir(os.path.join(direct,'levels'))):
    babi = []
    with open(os.path.join(direct,'levels',level),'r') as file:
        walls = json.load(file)
        babi.append(End(topleft=walls['end']))
        for wall_data in walls['walls']:
            wall = Wall(wall_data['width'],wall_data['height'],wall_data['topleft'])
            babi.append(wall)
        for enemy_data in walls['enemies']:
            wall = Enemy(topleft=enemy_data['topleft'],points=enemy_data['points'])
            babi.append(wall)
        if i == 0:
            end = [babi[0]]
            for wall in babi[1:]:
                wall.add(cameragroup)
                if type(wall) == Wall:
                    wall.add(colliders)
                else:
                    wall.add(enemies)
            end[0].add(cameragroup)
        levels.append(babi)

async def main():
    global running
    global event
    global dt
    global player
    global cameragroup
    global end
    global colliders
    global dir_vector
    global mouse
    global g
    global p_x, p_y
    global md
    global p_lvl
    global lvl
    global gaming
    global menu

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == 32:
                    if gaming:
                        gaming = False
                    else:
                        gaming = True
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    md = False
        if (p_lvl != lvl) and (0 < lvl < len(levels)):
            for i,wall in enumerate(levels[lvl]):
                if i == 0:
                    end = [wall]
                    end[0].add(cameragroup)
                else:
                    if type(wall) == Wall:
                        wall.add(colliders)
                    elif type(wall) == Enemy:
                        wall.add(enemies)
                    wall.add(cameragroup)
            p_lvl += 1

        mouse = {'pos':pygame.mouse.get_pos(),'press':pygame.mouse.get_pressed()}
        
        screen.fill('black')
        if gaming:

            dir_vector = pygame.Vector3(mouse['pos'][0]-c.x,mouse['pos'][1]-c.y,0)
            dir_vector.z = math.sqrt(dir_vector.x**2+dir_vector.y**2)
            if dir_vector.z != 0:
                dir_vector.x = dir_vector.x/dir_vector.z
                dir_vector.y = dir_vector.y/dir_vector.z

                pygame.draw.line(screen,'green',c,(c.x+(dir_vector.x*30),c.y+(dir_vector.y*30)))
                angle = math.atan2(mouse['pos'][1] - c.y, mouse['pos'][0] - c.x)

            g = -10
            V = player.speed.z

            p_x = 0
            p_y = 0

            length = 10

            cameragroup.custom_draw()
            if player.air and not(player.passed):
                length = get_length(math.degrees(freeze.z))
                texts = [font['12'].render(str(math.degrees(freeze.z))+'°',False,'green'),font['12'].render('x: '+str(player.rect.centerx)+' / Vx: '+str(round(player.speed.x,3)),False,'green'),font['12'].render('y: '+str(player.rect.centery)+' / Vy: '+str(round(-player.speed.y if player.air else 0.0,3)),False,'green'),font['12'].render('target: x-'+str(end[0].rect.centerx)+' / y-'+str(end[0].rect.centery),False,'green')]
                for i in range(round(150*length)):
                    if V != 0:
                        x = i*length*freeze2
                        y = 1*(x*math.tan(freeze.z) - (g*(x**2)/(2*(40**2)*math.cos(freeze.z)**2)))
                        pygame.draw.circle(screen,'red',((freeze.x+x)+cameragroup.offset.x,(freeze.y+y)+cameragroup.offset.y),1)
                        if p_y != 0 and p_x != 0:
                            pygame.draw.line(screen,'red',(p_x+cameragroup.offset.x,p_y+cameragroup.offset.y),(freeze.x+x+cameragroup.offset.x,freeze.y+y+cameragroup.offset.y))
                        p_x = freeze.x+x
                        p_y = freeze.y+y
            elif not(player.passed):
                length = get_length(math.degrees(angle))
                texts = [font['12'].render(str(math.degrees(angle))+'°',False,'green'),font['12'].render('x: '+str(player.rect.centerx)+' / Vx: '+str(round(player.speed.x,3)),False,'green'),font['12'].render('y: '+str(player.rect.centery)+' / Vy: '+str(round(-player.speed.y if player.air else 0.0,3)),False,'green'),font['12'].render('target: x-'+str(end[0].rect.centerx)+' / y-'+str(end[0].rect.centery),False,'green')]
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
            print(player.speed.z)

            player.update()
            enemies.update()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    md = True
        else:
            menu.update()
            menu.draw(screen)
            pygame.draw.circle(screen,'red',c,10,5)

        pygame.display.flip()
        await asyncio.sleep(0)
        clock.tick(30)/1000

asyncio.run(main())