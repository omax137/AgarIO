import socket
import pygame
import random
import os


# Создание относительного пути к файлу
file_path = os.path.join("папка", "подпапка", "файл.txt")
    

WIDTH_ROOM,HEIGHT_ROOM = 6000,6000
WIDTH_SERVER,HEIGHT_SERVER = 300,300
#создание сокета
main_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM) #(ip v.4; TCP протокол)
main_socket.setsockopt(socket.IPPROTO_TCP,socket.TCP_NODELAY,1) #отключает алгоритм Нейгла
main_socket.bind(('localhost', 2048)) #привязка к порту компьютеру с которым будет общаться
main_socket.setblocking(0) #непрерывная работа сервера. "Не нужно ждать изменений, если их нет работай дальше"
main_socket.listen(5) #режим прослушивания/сколько человек может подключиться одновременно

#создание окна сервера
pygame.init()
screen = pygame.display.set_mode((WIDTH_SERVER,HEIGHT_SERVER))
pygame.display.set_caption('Server')
clock = pygame.time.Clock()
FPS = 100


MOBS = 25
FEED = (WIDTH_ROOM * HEIGHT_ROOM)//60000
colour ={'0':(255,255,0),'1':(255,0,0),'2':(0,255,0),'3':(128,128,0),'4':(0,255,255)}

START_PLAYER_SIZE = 30
FEED_SIZE = 20

def new_r(R,r):
    return (R**2 + r**2)**0.5

def find(s):
    otkr = None
    for i in range(len(s)):
        if s[i] == '<':
            otkr = i
        if s[i] == '>' and otkr != None:
            zakr = i
            res = s[otkr+1:zakr]
            res = list(map(int,res.split(',')))
            return res
    return ''

class Feed():
    def __init__(self,x,y,r,color):
        self.x = x
        self.y = y
        self.r = r
        self.color = color

class Player():
    def __init__(self,connect,addr,x,y,r,color):
        self.connect = connect
        self.addr = addr
        self.x = x
        self.y = y
        self.r = r
        self.color = color

        self.L = 1 #масштаб(1 к 1)

        self.name = 'Bot'
        self.width_window = 500
        self.height_window = 500
        self.w_vision = 500
        self.h_vision = 500

        self.dead = 0
        self.errors = 0

        self.ready = False

        self.abs_speed = 30 / (self.r ** 0.5)
        self.speed_x = 0
        self.speed_y = 0

    def set_options(self,data):
        data = data[1:-1].split(' ')
        self.name = data[0]
        self.width_window = int(data[1])
        self.height_window = int(data[2])
        self.w_vision = int(data[1])
        self.h_vision = int(data[2])

    def change_vector(self,vector):
        if vector[0] == 0 and vector [1] == 0:
            self.speed_x = 0
            self.speed_y = 0
        else:
            dlina_vectora = (vector[0]**2 + vector[1]**2)**0.5
            vector = ((vector[0]/dlina_vectora)*self.abs_speed,(vector[1]/dlina_vectora)*self.abs_speed)
            self.speed_x , self.speed_y = vector[0] , vector [1]
            
    def coor(self):
        if self.x - self.r <= 0: #x
            if self.speed_x >= 0:
                self.x +=self.speed_x
        else:
            if self.x + self.r >= WIDTH_ROOM:
                if self.speed_x <= 0:
                    self.x += self.speed_x
            else:
                self.x += self.speed_x
        if self.y - self.r <= 0: #y
            if self.speed_y >= 0:
                self.y +=self.speed_y
        else:
            if self.y + self.r >= HEIGHT_ROOM:
                if self.speed_y <= 0:
                    self.y += self.speed_y
            else:
                self.y += self.speed_y


        #change abs_speed
        if self.r != 0:
            self.abs_speed = 30/(self.r ** 0.5)
        else:
            self.abs_speed = 0
        #chnge r
        if self.r >= 100:
            self.r -=self.r/18000

        #change L(масштаб)
        if (self.r >= self.w_vision/4) or (self.r >= self.h_vision/4):
            if (self.w_vision <= WIDTH_ROOM) or (self.h_vision <= HEIGHT_ROOM):
                self.L *= 2
                self.w_vision = self.width_window * self.L
                self.h_vision = self.height_window * self.L
        if (self.r <= self.w_vision/8) and (self.r <= self.h_vision/8):
            if self.L >1:
                self.L = self.L // 2
                self.w_vision = self.width_window * self.L
                self.h_vision = self.height_window * self.L

#Спавн мобов
players = [Player(None,None,
                  random.randint(0,WIDTH_ROOM),
                  random.randint(0,HEIGHT_ROOM),
                  random.randint(100,200),
                  str(random.randint(0,4))
                  )
           for i in range(MOBS)
           ]

#Спавн корма
feed = [Feed(random.randint(0,WIDTH_ROOM),
             random.randint(0,HEIGHT_ROOM),
             FEED_SIZE,
             str(random.randint(0,4)))
        for i in range(FEED)]


tick = 0
server = True
while server:
    tick += 1
    clock.tick(FPS)
    if tick == 200:
        tick = 0

        try:
            new_socket, addr = main_socket.accept()
            print('Подключился:', addr)
            new_socket.setblocking(0)
            spawn_player = random.choice(feed)
            new_player = Player(new_socket,
                                addr,
                                spawn_player.x,
                                spawn_player.y,
                                START_PLAYER_SIZE,
                                str(random.randint(0,4))
                                )
            
            feed.remove(spawn_player)
            players.append(new_player)
            
        except: #если ошибка, то ничего не делай
            pass
        #респавн mobs
        for i in range(MOBS - len(players)):
            if len(feed) != 0:
                spawn_mobs = random.choice(feed)
                players.append(Player(None,None,
                                      spawn_mobs.x,
                                      spawn_mobs.y,
                                      random.randint(100,200),
                                      str(random.randint(0,4))
                                      )
                               )
                feed.remove(spawn_mobs)
        new_feed = [Feed(random.randint(0,WIDTH_ROOM),
                         random.randint(0,HEIGHT_ROOM),
                         FEED_SIZE,
                         str(random.randint(0,4))
                         )
                    for i in range(FEED - len(feed))
                    ]
        
        feed = feed + new_feed
        
    #считываем команды игроков
    for player in players:
        if player.connect != None:
            try:
                data = player.connect.recv(2048) #получаем данные в виде байта
                data = data.decode() #расшифровывем сообщение
                if data[0] == '!': #начало сообщения диалога
                    player.ready = True
                else:
                    if data[0] =='.' and data[-1] == '.': #nickname and size
                        player.set_options(data)
                        player.connect.send((str(START_PLAYER_SIZE)+' '+player.color).encode())
                    else: #vector
                        data = find(data) #находим конкретные числа
                        #обрабатываем команды
                        player.change_vector(data)
            except:
                pass
        else:
            if tick == 100:
                data = [random.randint(-100,100),random.randint(-100,100)]
                player.change_vector(data)
        player.coor()
    
    #определяем, что видит игрок
    visible_balls = [[] for i in range(len(players))]
    for i in range(len(players)):
        #Какой корм видит i-игрок
        for k in range(len(feed)):
            dist_x = feed[k].x - players[i].x
            dist_y = feed[k].y - players[i].y

            # i-игрок видит [k]orm
            if (((abs(dist_x) <= (players[i].w_vision) // 2 + feed[k].r))
                    and
                    ((abs(dist_y) <= (players[i].h_vision) // 2 + feed[k].r))):
                # i-игрок может съесть [k]orm???
                if (((dist_x ** 2 + dist_y ** 2) ** 0.5) <= players[i].r and (players[i].r > 1.1 * feed[k].r)):
                    # изменим радиус i-игрока
                    players[i].r = new_r(players[i].r,feed[k].r)
                    feed[k].r = 0
                if (players[i].connect != None) and (feed[k].r != 0):
                    # подготовка данных к отправке в список
                    x_ = str(round(dist_x/players[i].L))
                    y_ = str(round(dist_y/players[i].L))
                    r_ = str(round(feed[k].r/players[i].L))
                    c_ = feed[k].color

                    visible_balls[i].append(x_ + ' ' + y_ + ' ' + r_ + ' ' + c_)

        for j in range(i+1,len(players)):
            #рассматриваем i и j игрока
            dist_x=players[j].x - players[i].x
            dist_y=players[j].y - players[i].y

            #i-игрок видит j-игрока
            if (((abs(dist_x) <= (players[i].w_vision)// 2 + players[j].r))
                and
                ((abs(dist_y) <= (players[i].h_vision)// 2 + players[j].r))):
                #i-игрок может съесть j-игрока???
                if ((dist_x**2 + dist_y**2)**0.5) <= players[i].r and (players[i].r > 1.1*players[j].r):
                    #изменим радиус i-игрока
                    players[i].r = new_r(players[i].r, players[j].r)
                    players[j].r, players[j].speed_x, players[j].speed_y = 0,0,0

                if  players[i].connect != None:
                #подготовка данных к отправке в список
                    x_ = str(round(dist_x/players[i].L))
                    y_ = str(round(dist_y/players[i].L))
                    r_ = str(round(players[j].r/players[i].L))
                    c_ = players[j].color
                    n_ = players[j].name
                    if players[j].r >= 30*players[i].L:
                        visible_balls[i].append(x_+' '+y_+' '+r_+' '+c_+' '+n_)
                    else:
                        visible_balls[i].append(x_ + ' ' + y_ + ' ' + r_ + ' ' + c_)
            #j-игрок видит i-игрока
            if (((abs(dist_x) <= (players[j].w_vision)// 2 + players[i].r))
                and
                ((abs(dist_y) <= (players[j].h_vision)// 2 + players[i].r))):
                #j-игрок может съесть i-игрока???
                if (((dist_x**2 + dist_y**2)**0.5) <= players[j].r and (players[j].r > 1.1*players[i].r)):
                    #изменим радиус j-игрока
                    players[j].r = new_r(players[j].r, players[i].r)
                    players[i].r, players[i].speed_x, players[i].speed_y = 0,0,0

                    
                #подготовка данных к отправке в список
                if players[j].connect != None:
                    x_ = str(round(-dist_x/players[j].L))
                    y_ = str(round(-dist_y/players[j].L))
                    r_ = str(round(players[i].r/players[j].L))
                    c_ = players[i].color
                    n_ = players[i].name

                    if players[i].r >= 30*players[j].L:
                        visible_balls[j].append(x_+' '+y_+' '+r_+' '+c_+' '+n_)
                    else:
                        visible_balls[j].append(x_+' '+y_+' '+r_+' '+c_)

    otvets = ['' for i in range(len(players))]
    for i in range(len(players)):
        r_ = str(round(players[i].r/players[i].L))
        visible_balls[i] = [r_] + visible_balls[i]
        otvets[i] = '<'+(','.join(visible_balls[i]))+'>'
    for i in range(len(players)):
        if (players[i].connect != None) and (players[i].ready):
            try:
                players[i].connect.send(otvets[i].encode())
                players[i].errors = 0
            except:
                players[i].errors += 1
            
    #очистка сервера от игроков
    for player in players:
        if player.r == 0:
            if player.connect != None:
                player.dead += 1
            else:
                player.dead += 300

        if (player.errors == 500) or (player.dead == 300):
            if player.connect != None:
                player.connect.close()
            players.remove(player)
    #очистка от корма
    for m in feed:
        if m.r == 0:
            feed.remove(m)
            

    #отрисовка состояния комнаты
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            server = False
    screen.fill('gray99')
    for player in players:
        x = round(player.x * WIDTH_SERVER // WIDTH_ROOM)
        y = round(player.y * HEIGHT_SERVER // HEIGHT_ROOM)
        r = round(player.r * WIDTH_SERVER // WIDTH_ROOM)
        c = colour[player.color]
        pygame.draw.circle(screen,c,(x,y),r)

    pygame.display.update()
            
pygame.quit()
main_socket.close()