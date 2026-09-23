import numpy as np
import pygame, sys
import time

WIDTH = 1000
HEIGHT = 800
DT = 0.05 #модельное время одного шага


def dist(p1, p2):
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    return np.sqrt(dx * dx + dy * dy)


# модель объекта
class Obj:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.reservedRobot = None  # назначенный робот
        self.finished = False  # флаг завершенности

    def getPos(self):
        return (self.x, self.y)

    def draw(self, screen):
        r = 10
        pygame.draw.ellipse(screen, self.color,
                            [self.x - r, self.y - r, 2 * r, 2 * r], 2)


# модель робота
class Robot:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.attachedObj = None  # прикрепленный объект
        self.target = None  # целевая точка

    def getPos(self):
        return (self.x, self.y)

    def draw(self, screen):
        r = 20
        pygame.draw.ellipse(screen, (255, 0, 0),
                            [self.x - r, self.y - r, 2 * r, 2 * r], 2)

    def simulate(self):
        if self.target != None:
            p1 = self.target
            p2 = (self.x, self.y)
            v = np.array(p1) - np.array(p2)
            d = dist(p1, p2)  # расстояние от робота до цели
            if d > 0:
                v = v / d
            self.x += v[0] * 5
            self.y += v[1] * 5
        if self.attachedObj != None:  # прикреплен ли объект к роботу
            self.attachedObj.x = self.x
            self.attachedObj.y = self.y

    def findNearestObj(self, objs, threshold=100500):
        res = None
        D = 100500
        for o in objs:
            if o.reservedRobot != None and o.reservedRobot != self:
                continue
            if o.finished:
                continue
            dNew = dist(o.getPos(), self.getPos())
            if dNew < D:
                D = dNew
                res = o
        if D > threshold:
            res = None
        return res

    def take(self, obj):
        if obj != None:
            self.attachedObj = obj


# распределение задач
def distributeTasks(robots, objs, goal):
    # назначение задач каждому из роботов
    for r in robots:
        # проверка окончания транспортировки до целевой точки
        if r.attachedObj != None and dist(r.getPos(), goal.getPos()) < 20:
            r.attachedObj.finished = True
            r.attachedObj = None  # отпускание объекта
            r.target = None
        else:
            # проверка возможности захвата объекта
            if r.attachedObj == None:
                obj = r.findNearestObj(objs)
                if obj != None and dist(r.getPos(), obj.getPos()) < 20:
                    r.take(obj)  # захват объекта
                    r.target = goal.getPos()
                    return

        # проверка возможности движения к другим объектам
        if r.target == None and r.attachedObj == None:
            obj = r.findNearestObj(objs)
            if obj == None:
                continue
            if obj.reservedRobot != None:
                continue
            r.target = obj.getPos()
            obj.reservedRobot = r  # фиксация выбора объекта роботом


# критерий окончания алгоритма
def checkMission(robots, objs, goal):
    if all(o.finished for o in objs):
        return True
    if len(robots) == 1 and any(o.finished for o in objs):
        return False
    for r in robots:
        if dist(r.getPos(), goal.getPos()) > 20:
            return False
    for o in objs:
        if o.reservedRobot == None:
            return False
    return True


def generateObjects(N):
    res = []
    for i in range(N):
        o = Obj(np.random.randint(50, WIDTH - 50),
                np.random.randint(50, HEIGHT - 50),
                (0, 255, 0))
        res.append(o)
    return res


def main(N, M):
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    # start = time.time()
    steps = 0
    
    robots = []
    for i in range(N):              
        robots.append(Robot(65 * (i + 1), 65 * (i + 1)))

    objs = generateObjects(M)
    goal = Obj(750, 450, (0, 0, 255))

    # цикл отрисовки
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        if checkMission(robots, objs, goal):
            break

        screen.fill((255, 255, 255))

        distributeTasks(robots, objs, goal)
        steps += 1
        
        for r in robots:
            r.simulate()
            r.draw(screen)

        for o in objs:
            o.draw(screen)

        goal.draw(screen)

        pygame.display.update()
        # pygame.time.delay(0)

    # end = time.time()
    return steps*DT
    
    
NN = [1, 2, 3, 4, 5]
MM = [5, 10, 15]
REPEATS = 15

# создаём файл с заголовком ("w" — перезаписать)
with open("results.csv", "w", encoding="utf-8") as f:
    f.write("N;M;run;T\n")

results = []  # сюда сложим усреднённые строки для таблицы

for N in NN:
    for M in MM:
        times = []
        for run in range(REPEATS):
            T = main(N, M)
            times.append(T)
            print(f"N={N} M={M} прогон {run + 1}: T = {T:.2f} c")
            # дописываем строку сразу ("a" — append)
            with open("results.csv", "a", encoding="utf-8") as f:
                f.write(f"{N};{M};{run + 1};{T:.3f}\n")

        T_avg = sum(times) / len(times)
        results.append((N, M, T_avg, T_avg * N))

pygame.quit()

print("\n  N   M     T, c    T2, c")
for N, M, T, T2 in results:
    print(f"{N:>3} {M:>3} {T:>8.2f} {T2:>8.2f}")





