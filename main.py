from pygame import *
from random import randint
'''Необходимые классы'''

#класс-родитель для спрайтов 
class GameSprite(sprite.Sprite):    #конструктор класса
    def __init__(self, in_image, in_size_x, in_size_y, in_coord_x, in_coord_y):
        super().__init__()
        # каждый спрайт должен хранить свойство image - изображение
        if type(in_image) == tuple:
            self.image = Surface((in_size_x, in_size_y))
            self.image.fill(in_image)
        elif type(in_image) == str:
            self.image = transform.scale(image.load(in_image), (in_size_x, in_size_y))
        else:
            self.image = in_image

        self.rect = self.image.get_rect()
        self.rect.x = in_coord_x
        self.rect.y = in_coord_y
        self.size_x = in_size_x
        self.size_y = in_size_y


    def blit(self):
        window.blit(self.image, (self.rect.x, self.rect.y))

class MoveSprite(GameSprite):    #конструктор класса
    def __init__(self, in_image, in_size_x, in_size_y, in_coord_x, in_coord_y, in_speed):
        super().__init__(in_image, in_size_x, in_size_y, in_coord_x, in_coord_y)
        self.speed = in_speed
    def move(self,x,y):
        self.rect.x += self.speed*x
        self.rect.y += self.speed*y        

class PlayerSprite(MoveSprite):
#Убрал лишние клавиши
    def move(self):       
        keys = key.get_pressed()
        if keys[K_a] and self.rect.x > self.speed:
           super().move(-1,0)
        if keys[K_d] and self.rect.x < win_width - self.size_x:
           super().move(1,0)
        if keys[K_w] and self.rect.y > self.speed:
           super().move(0,-1)
        if keys[K_s] and self.rect.y < win_height - self.size_y:
           super().move(0,1)
    def remove(self):       
        keys = key.get_pressed()
        if keys[K_a] and self.rect.x > self.speed:
           super().move(1,0)
        if keys[K_d] and self.rect.x < win_width - self.size_x:
           super().move(-1,0)
        if keys[K_w] and self.rect.y > self.speed:
           super().move(0,1)
        if keys[K_s] and self.rect.y < win_height - self.size_y:
           super().move(0,-1)
#2021.03.07 Выстрел пули для класса PlayerSprite
    def fire(self):
        bullets.add(BulletSprite('bullet.png', 30,30,self.rect.centerx-30/2,self.rect.top,5))

class EnemySprite(MoveSprite):
    def move(self):
        if self.rect.y >= win_height - 85:
            self.rect.y = 0
            self.rect.x = randint(1,win_width-10)
            self.speed = randint(2,4)
#2021.02.28 увеличиваю счетчик
            bots.lost += 1
        super().move(0,1)
#2021.03.07 Пуля попала в корабль
    def kill(self):
        self.rect.y = 0
        self.rect.x = randint(1,win_width-10)
        self.speed = randint(2,4)
        self.update()
        bots.kills += 1

    def update(self):
        self.move()
        self.blit()
#2021.03.07
class BulletSprite(MoveSprite):
    def move(self):
        if self.rect.y <= 0:
            bullets.remove(self)
        super().move(0,-1)
    def update(self):
        self.move()
        self.blit()

#Игровая сцена:

win_width = 700
win_height = 500
sprite_size = 50
window = display.set_mode((win_width, win_height))
display.set_caption("Догонялки")
background = GameSprite('galaxy.jpg', win_width,win_height,0,0)

player = PlayerSprite('rocket.png', sprite_size,sprite_size,win_width/2,win_height-100,5)
#2021.02.28 Ботсы создаются группой
bots = sprite.Group()
for i in range(3):
    bots.add(EnemySprite('ufo.png', sprite_size,sprite_size,randint(1,win_width-85),randint(10,200),randint(2,4)))

#2021.02.28 Счетчик запихнул в ботов
bots.lost = 0

#2021.03.07 Создал пули для группы
bullets = sprite.Group()

#2021.03.07 Создал счетчик для пуль
bots.kills = 0

game = True
clock = time.Clock()
FPS = 120

#музыка
mixer.init()
mixer.music.load('jungles.ogg')
#mixer.music.play()

font.init()
font1 = font.SysFont('Arial', 70)
win = font1.render('YOU WIN!', True, (255, 215, 0))
lose = font1.render('YOU LOSE!', True, (180, 0, 0))

#2021.02.28 Новый фон для счетчиковpyinstaller --onefile shooter_game.py.
font2 = font.SysFont('Arial', 25)

finish = False
while game:

    for e in event.get():
        if e.type == QUIT:
            game = False
#2021.03.07 Выстрел осуществляется в while
        elif e.type == KEYDOWN:
            if e.key == K_SPACE:
                player.fire()
    
    background.blit()
    if finish != True:
        player.blit()
        player.move()
#2021.02.28 Двигаются группой
        bots.update()
#2021.02.28 Ботсы проверяются группой (новый метод)
        if sprite.spritecollide(player,bots,False):
            finish = True
            result = lose      
#2021.02.28 В игровом цикле формируем текст счетчика
        text_lose = font2.render("Пропущено: " + str(bots.lost), 1, (255, 255, 255))


#2021.03.07 Пули необходимо обновлять
        bullets.update()
#2021.03.07 Проверка на попадание, при попадании из группы автоматически удаляется пуля
        bots_kill = sprite.groupcollide(bullets,bots, True, True)
            # этот цикл повторится столько раз, сколько монстров подбито
        for bot in bots_kill:
            bot.kill()
            #bots.add(bot)
        text_kills = font2.render("Убито: " + str(bots.kills), 1, (255, 255, 255))
        window.blit(text_kills, (10, 100))

        window.blit(text_lose, (10, 50))
    else:
        window.blit(result, (200, 200))

    display.update()
    clock.tick(FPS)