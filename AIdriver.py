import pygame
import random
import math
import neat
import visualize
import os
import sys
import pickle
import configparser
import matplotlib.pyplot as plt
import graphviz

sys.stdout = open('output.txt', 'w')

config_ini = configparser.ConfigParser()
config_ini.read('config.ini')


# Размеры окна
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 800
# Цвет фона
bg_color = (100, 149, 237)

# Initialize PyGame And The Display
pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame_icon = pygame.image.load("CAR-ICON.png")
pygame.display.set_icon(pygame_icon)
pygame.display.set_caption("Виртуальная модель обучения нейронной сети")


# Размеры изображения
TANK_SIZE_X = 30    
TANK_SIZE_Y = 60

current_generation = 0 # Generation counter

# Создаем массив препядствиий
obstacle_color = (60, 60, 60)
obstacle_radius = 40
num_obstacles = 10
obstacle_position = []
for i in range(num_obstacles):
    obstacle_pos = (random.randint(obstacle_radius+100, WINDOW_WIDTH - obstacle_radius), 
                    random.randint(obstacle_radius, WINDOW_HEIGHT - obstacle_radius-100))
    obstacle_position.append(obstacle_pos)

class Tank:

    def __init__(self):
        # Загружаем изображение танка
        self.image = pygame.image.load("car.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (TANK_SIZE_X , TANK_SIZE_Y))
        self.rotated_sprite = self.image
        
        # Стартовая позиция стартовый угол и начальная скорость
        self.position = [WINDOW_WIDTH-500, WINDOW_HEIGHT-200]
        self.angle = 0
        self.speed = 2

        # Центр танка для простоты расчетов
        self.center = [self.position[0]+TANK_SIZE_X/2, self.position[1]+TANK_SIZE_Y/2]

        # Радары
        self.radars = []
        self.radars_draw = []

        # Проверка на пульс
        self.alive = True
        self.award_die = False

        # Растояние до цели и время
        self.distance = 0
        self.time = 0

        self.speed_set = False

        self.y = 1000
        self.k = 0

        

    # Рисуем танк
    def draw(self, obstacle_position, obstacle_radius):
        rotated_image = pygame.transform.rotate(self.image, -self.angle)
        rotated_rect = rotated_image.get_rect(center=(self.position[0] + 60/2, self.position[1] + 60/2))
        screen.blit(rotated_image, rotated_rect)
        self.center=(self.position[0] + 60/2, self.position[1] + 60/2)
        self.radars.clear()
        for rad in (270, 315, 0 , 45, 90):
            self.check_radar(rad,obstacle_position, obstacle_radius)
        

    def move_up(self):
        if self.position[0] >= 0 and self.position[1] >= 0 and self.position[0] <= WINDOW_WIDTH and self.position[1] <= WINDOW_HEIGHT:
            self.position[0] += self.speed * math.cos(math.radians(self.angle-90))
            self.position[1] += self.speed * math.sin(math.radians(self.angle-90))
        

    def move_down(self):
        if self.position[0] >= 0 and self.position[1] >= 0 and self.position[0] <= WINDOW_WIDTH and self.position[1] <= WINDOW_HEIGHT:
            self.position[0] -= self.speed * math.cos(math.radians(self.angle-90))
            self.position[1] -= self.speed * math.sin(math.radians(self.angle-90))

    def rotate(self, angle):
        self.angle += angle
        if self.angle > 360:
            self.angle -= 360
        elif self.angle < 0:
            self.angle += 360


    # Рисуем радары
    def draw_radars(self):       

        for radar in self.radars:
            position = radar[0]
            pygame.draw.line(screen, (0, 0, 255), self.center, position, 1)
            pygame.draw.circle(screen, (0, 0, 255), position, 3)
        

    def check_radar(self, rad, obstacle_position, obstacle_radius):
        len = 0
        x = int(self.center[0] + math.cos(math.radians((self.angle + rad-90))) * len)
        y = int(self.center[1] + math.sin(math.radians((self.angle + rad-90))) * len)  

        obs = 0                 

        while  len < 200 and x > 0 and y > 0 and x < WINDOW_WIDTH and y < WINDOW_HEIGHT and obs == 0:
            len = len + 1
            x = int(self.center[0] + math.cos(math.radians((self.angle + rad-90))) * len)
            y = int(self.center[1] + math.sin(math.radians((self.angle + rad-90))) * len)
            for i in (obstacle_position): 
                if pygame.Rect(i[0], i[1], obstacle_radius, obstacle_radius).collidepoint(x, y):
                    obs = 1
                    # print(x,y)

        dist = int(math.sqrt(math.pow(x - self.center[0], 2) + math.pow(y - self.center[1], 2)))    
        self.radars.append([(x, y), dist])
        # print(self.radars)
    
    def collision(self, obstacle_position):
        self.alive = True
            
        # Полный размер в данной точке
        self.full_size = pygame.Rect(self.position[0], self.position[1], 60, 60)
        for i in (obstacle_position):
            self.obs = pygame.Rect((i[0], i[1], 40, 40))
            if pygame.Rect.colliderect(self.full_size, self.obs) or self.position[0] < 1 or self.position[1] < 1 or self.position[0] > WINDOW_WIDTH-40 or self.position[1] > WINDOW_HEIGHT-40:
                self.alive = False
                break

    def line(self, x_goal, y_goal):
        pygame.draw.line(screen, (255, 255, 255), (self.position[0]+30, self.position[1]+30), (x_goal, y_goal), 1)
        
    def get_data(self, x_goal, y_goal):
        # Get Distances To Border
        radars = self.radars
        return_values = [0, 0, 0, 0, 0, 0, 0]
        for i, radar in enumerate(radars):
            return_values[i] = int(radar[1])
        return_values[5] = float(math.dist((self.position[0]+30, self.position[1]+30), (x_goal, y_goal)))
        return_values[6] = self.angle
        # print(self.angle)
        
        return return_values
    
    def is_alive(self):
        # Basic Alive Function
        return self.alive
    
    def get_reward(self, counter, x_goal, y_goal):
        k = 0
        if self.is_alive():
            x = math.dist((self.position[0]+30, self.position[1]+30), (x_goal, y_goal))
            if x < self.y:
                k += 5
            else:
                k -= 0         
            # k += 1
            if self.angle < 270 and self.angle > 180:
                k += 1
            else:
                k -= 0
            self.y = x     
        else:
            if not self.award_die:
                shtaf_smert = int(config_ini.get('Section1', 'shtaf_smert'))
                k -= 10
                self.award_die = True
        
        self.k = k
        # print(k)
        return  k


def run_simulation(genomes, config):
    # Empty Collections For Nets and tanks
    nets = []
    tanks = []

    x_goal = 30
    y_goal = 700

    generation_font = pygame.font.SysFont("Arial", 30)
    alive_font = pygame.font.SysFont("Arial", 20)

    # For All Genomes Passed Create A New Neural Network
    for i, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        g.fitness = 0

        tanks.append(Tank())

        print("Genome ID:", g.key)
        for conn in g.connections.values():
            print("  Input Node:", conn.key[0], "Output Node:", conn.key[1], "Weight:", conn.weight)

    import graphviz

    global current_generation
    current_generation += 1

    


    # Simple Counter To Roughly Limit Time (Not Good Practice)
    counter = 0
    
    while True:
        # Exit On Quit Event
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)

        screen.fill(bg_color)

        # Рисуем препятствия        
        pygame.draw.rect(screen, (255,255,255), (x_goal, y_goal, obstacle_radius, obstacle_radius))
        for i in (obstacle_position):
            pygame.draw.rect(screen, obstacle_color, (i[0], i[1], obstacle_radius, obstacle_radius))

        # Куда двигаться
        for i, tank in enumerate(tanks):
            output = nets[i].activate(tank.get_data(x_goal, y_goal))
            choice = output.index(max(output))
            # print(choice)
            if choice == 0:
                tank.rotate(-2)
            elif choice == 1:
                tank.rotate(2)
            elif choice == 2:
                # pass
                tank.move_up()
            # elif choice  == 3:
            #     tank.move_down()
        
        # Если танк жив меняем положение
        still_alive = 0
        for i, tank in enumerate(tanks):
            if tank.is_alive():
                still_alive += 1
                tank.draw(obstacle_position, obstacle_radius)
                tank.draw_radars()
                tank.collision(obstacle_position)
                tank.line(x_goal, y_goal)
            genomes[i][1].fitness += tank.get_reward(counter, x_goal, y_goal)
        

        if still_alive == 0:
            break

        con = config_ini.get('Section1', 'con')
        con = int(con)
        
        counter += 1
        if counter == con: # Stop After About 20 Seconds
            break

        for tank in tanks:
            if tank.is_alive():
                tank.draw(obstacle_position, obstacle_radius)

        text = generation_font.render("Поколение: " + str(current_generation-1), True, (0,0,0))
        text_rect = text.get_rect()
        text_rect.center = (400, 250)
        screen.blit(text, text_rect)

        text = alive_font.render("Машин осталоь: " + str(still_alive), True, (0, 0, 0))
        text_rect = text.get_rect()
        text_rect.center = (400, 290)
        screen.blit(text, text_rect)

        text = alive_font.render("Счетчик: " + str(con - counter), True, (0, 0, 0))
        text_rect = text.get_rect()
        text_rect.center = (400, 310)
        screen.blit(text, text_rect)

        pygame.display.flip()

    

    folder_path = 'folder/'

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    filename = 'generation_' + str(current_generation) + '.pkl'
    file_path = os.path.join(folder_path, filename)

    with open(file_path, 'wb') as f:
        pickle.dump(population, f)
    

if __name__ == "__main__":    
    # Load Config
    config_path = "neat.txt"
    config = neat.config.Config(neat.DefaultGenome,
                                neat.DefaultReproduction,
                                neat.DefaultSpeciesSet,
                                neat.DefaultStagnation,
                                config_path)
    
     # Проверяем наличие сохраненных файлов
    folder_path = "folder"

    if not os.path.exists(folder_path):
        os.mkdir(folder_path)

    generation_files = [f for f in os.listdir(folder_path) if f.startswith('generation_') and f.endswith('.pkl')]
    if generation_files:
        # Сортируем файлы по номеру поколения и выбираем последний
        latest_generation_file = sorted(generation_files, key=lambda x: int(x.split('_')[1].split('.')[0]))[-1]
        # Загружаем последнее поколение
        with open(os.path.join(folder_path, latest_generation_file), 'rb') as f:
            population = pickle.load(f)
        current_generation = int(latest_generation_file.split('_')[1].split('.')[0])

    else:
        # Создаем новое поколение
        population = neat.Population(config)
        population.add_reporter(neat.StdOutReporter(True))

    stats = neat.StatisticsReporter()
    population.add_reporter(stats)
    
    # Run Simulation For A Maximum of 1000 Generations
    population.run(run_simulation, 500)