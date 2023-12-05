import socket
import pygame

sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
sock.setsockopt(socket.IPPROTO_TCP,socket.TCP_NODELAY,1)
sock.connect(('localhost',2048))

#nick
nickname = 'nikita'

#Создание окна игры
WIDTH_WINDOW, HEIGHT_WINDOW = 1920,1080
pygame.init()
screen = pygame.display.set_mode((WIDTH_WINDOW,HEIGHT_WINDOW))
pygame.display.set_caption('Agar.io')


#Цвета
colour ={'0':(255,255,0),'1':(255,0,0),'2':(0,255,0),'3':(128,128,0),'4':(0,255,255)}

old_vector = (0,0)

#отправляем серверу данные о себе
sock.send(('.'+nickname+' '+str(WIDTH_WINDOW)+' '+str(HEIGHT_WINDOW)+'.').encode())
data = sock.recv(64).decode()

#отправляем готовность
sock.send('!'.encode())


def find(s):
    otkr = None
    for i in range(len(s)):
        if s[i] == '<':
            otkr = i
        if s[i] == '>' and otkr != None:
            zakr = i
            res = s[otkr + 1:zakr]
            return res
    return ''

def write_name(x,y,r,name):
    font = pygame.font.Font(None, r )
    text = font.render(name, True, (0,0,0))
    rect = text.get_rect(center = (x,y))
    screen.blit(text,rect)


def draw_enemy(data):
    for i in range(len(data)):
        j = data[i].split(' ')

        x = WIDTH_WINDOW // 2 + int(j[0])
        y = HEIGHT_WINDOW // 2 + int(j[1])
        r = int(j[2])
        c = colour[j[3]]
        pygame.draw.circle(screen, c, (x, y), r)

        if len(j) == 5: write_name(x,y,r,j[4])



class Me():
    def __init__(self,data):
        data = data.split()
        self.r = int(data[0])
        self.my_color = data[1]

    def update(self, new_r):
        self.r = new_r

    def draw(self):
        if self.r != 0:
            pygame.draw.circle(screen, colour[self.my_color], (WIDTH_WINDOW // 2, HEIGHT_WINDOW // 2), self.r)
            write_name(WIDTH_WINDOW // 2, HEIGHT_WINDOW // 2, self.r,nickname)

me = Me(data)
game = True
while game:
    #обработка событий
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit()
    #считывает команды(мышки, клавиш и тд.)
    if pygame.mouse.get_focused(): #проверка есть ли курсор на экране
        pos = pygame.mouse.get_pos() #если курсор на экране , мы получаем информацию позиции
        vector = (pos[0] - WIDTH_WINDOW//2,pos[1] - HEIGHT_WINDOW//2)
        if (vector[0])**2 + (vector[1])**2 <= me.r **2:
            vector=(0,0)

    #отправляем команду на сервер
        if vector != old_vector:
            old_vector = vector
            message = '<' + str(vector[0]) + ',' + str(vector[1]) + '>'
            sock.send(message.encode())

    #получаем новое состояние
    try:
        data = sock.recv(2**20)#получаем данные в виде байта
        data = data.decode()#расшифровывем сообщение
        data = find(data)
        data = data.split(',')

    except:
        game = False
        continue

    screen.fill('gray99')
    if data != ['']:
        me.update(int(data[0]))
        draw_enemy(data[1:])
        me.draw()
    pygame.display.update()

pygame.quit()