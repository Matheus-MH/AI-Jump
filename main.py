import random

import pygame

import os

import neat

ai_play = True

pygame.init()

white = (255, 255, 255)
black = (0, 0, 0)
gray = (128, 128, 128)
background = gray
WIDTH = 400
HEIGHT = 500

generation = 0
score = 0

fps = 60
font = pygame.font.Font('freesansbold.ttf', 16)
end_font = pygame.font.Font('freesansbold.ttf', 25)
timer = pygame.time.Clock()

# Janela do jogo
screen = pygame.display.set_mode([WIDTH, HEIGHT])
pygame.display.set_caption('AI Jump')

Boneco = pygame.transform.scale(pygame.image.load('char.png'), (90, 70))
Imagem_Feno = pygame.transform.scale(pygame.image.load('hay (1).png'), (15, 20))

class Alpaca:


    IMG = Boneco
    Velocidade_pulo = 10
    Velocidade_movimento = 3


    def __init__(self):
        self.img = self.IMG
        self.x = 150
        self.y = 360
        self.vel_x = 0
        self.vel_y = 0
        self.velocity = 10
        self.tempo = 0
        self.height = self.y
        self.alpaca_jump = False
        self.jump_height = 10
        self.gravity = .4
        self.left_pressed = False
        self.right_pressed = False
        self.speed = self.Velocidade_movimento
        self.score = 0
        self.jump_points = 10

    def left(self):
        self.left_pressed = True

    def right(self):
        self.right_pressed = True

    def stop(self):
        self.left_pressed = False
        self.right_pressed = False

    def update_horizontal(self):

        #movimento horizontal
        self.vel_x = 0
        if self.left_pressed and not self.right_pressed:
            self.vel_x = -self.speed
        if self.right_pressed and not self.left_pressed:
            self.vel_x = self.speed

        self.x += self.vel_x

    def update_vertical(self):
        #movimento vertical

        if self.alpaca_jump and self.jump_points > 0 and self.vel_y >= 0:
            self.vel_y = -self.jump_height
            self.alpaca_jump = False
            self.jump_points -= 1
        self.y += self.vel_y
        self.vel_y += self.gravity

    def draw(self,tela):
        tela.blit(self.img, (self.x, self.y))

    def score_count(self, feno):
        if feno.collide(self):
            self.score += 1
        else:
            pass

class Feno:

    Fenos = []

    def __init__(self,x,y):
        self.img = Imagem_Feno
        self.x = x
        self.y = y
        self.size_x = 10
        self.size_y = 10
        self.Fenos = [[self.x, self.y]]


    def desenhar(self,tela):
        for i,feno in enumerate(self.Fenos):
            self.ponto = pygame.draw.rect(tela, black, [feno[0],feno[1], 10,10], 0, 3)

    def collide(self,alpaca):
        if self.ponto.colliderect([alpaca.x,alpaca.y, 70, 70]):
            self.Fenos.pop()
            self.Fenos.append([random.randint(10, 320),random.randint(15, 480)])
            return True
        else:
            return False


def draw_screen(screen,alpacas_fenos,generation):

    global ai_play

    for i, alpaca_feno in enumerate(alpacas_fenos):
        alpaca_feno[0].draw(screen)
        alpaca_feno[1].desenhar(screen)
        score_text = font.render('Score: ' + str(alpaca_feno[0].score), True, black)
        screen.blit(score_text, (320, 20))

    if ai_play:
        generation_text = font.render('Generation: ' + str(generation), True, black)
        screen.blit(generation_text, (15, 20))

def main(genomas, config):

    global score
    global generation

    generation += 1
    redes = []
    lista_genomas = []
    alpacas_fenos = []

    if ai_play:
        for _,genoma in genomas:
            rede = neat.nn.FeedForwardNetwork.create(genoma, config)
            redes.append(rede)
            genoma.fitness = 0
            lista_genomas.append(genoma)
            alpacas_fenos.append((Alpaca(), Feno(random.randint(10, 320),random.randint(15, 450))))
    else:
        alpacas_fenos = [(Alpaca(), Feno(random.randint(10, 320), random.randint(15, 450)))]


    running = True
    while running == True:

        timer.tick(fps)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.QUIT()
                quit()

            if not ai_play:
                for i in alpacas_fenos:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_a:
                            i[0].left()
                        if event.key == pygame.K_d:
                            i[0].right()
                        if event.key == pygame.K_k:
                            i[0].alpaca_jump = True
                    if event.type == pygame.KEYUP:
                        if event.key == pygame.K_a:
                            i[0].stop()
                        if event.key == pygame.K_d:
                            i[0].stop()

        for i in alpacas_fenos:
            if i[0].x < -40:
                i[0].x = 350
            elif i[0].x > 350:
                i[0].x = -40

        if len(alpacas_fenos) == 0:
            running = False

        for j,i in enumerate(alpacas_fenos):
            i[0].update_horizontal()
            i[0].update_vertical()
            if ai_play:
                lista_genomas[j].fitness += 0.1
                output = redes[j].activate((i[0].y, ((i[1].Fenos[0][0] - i[0].x)**2 + (i[1].Fenos[0][1] - i[0].y)**2)**0.5))
                if output[0] <= -0.5:
                    i[0].left()
                elif output[0] > 0 and output[0] < 0.25:
                    i[0].alpaca_jump = True
                elif output[0] >= 0.5:
                    i[0].right()
                #else:
                   # i[0].stop()

        screen.fill(background)
        draw_screen(screen, alpacas_fenos, generation)

        for j,i in enumerate(alpacas_fenos):
            i[0].score_count(i[1])
            if i[1].collide(i[0]) and ai_play:
                lista_genomas[j].fitness += 5
                i[0].jump_points += 10
            if i[1].collide(i[0]) and not ai_play:
                i[0].jump_points += 10

        for j,i in enumerate(alpacas_fenos):
            if i[0].y > 490 or i[0].y < -250:
                alpacas_fenos.pop(j)
                if ai_play:
                    lista_genomas[j].fitness -= 1
                    lista_genomas.pop(j)
                    redes.pop(j)
            else:
                pass

        pygame.display.flip()


def run(path_config):

    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, path_config)

    population = neat.Population(config)
    population.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    population.add_reporter(stats)

    if ai_play:
        population.run(main, 50)
    else:
        main(None, None)

if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    path_config = os.path.join(local_dir, 'config.txt')
    run(path_config)