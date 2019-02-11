#!/usr/bin/env python3

import sys
import math
import random
import pygame
import tkinter as tk
from tkinter import messagebox

class Cube(object):
    w = 500
    rows = 20

    def __init__(self, start, dirnx = 1, dirny = 0, color = (255, 0, 0)):
        self.pos = start
        self.dirnx = 1
        self.dirny = 0
        self.color = color

        
    def move(self, dirnx, dirny):
        self.dirnx = dirnx
        self.dirny = dirny
        self.pos = (self.pos[0] + self.dirnx, self.pos[1] + self.dirny)

    def draw(self, surface, eyes = False):
        dis = self.w // self.rows

        i = self.pos[0]
        j = self.pos[1]

        pygame.draw.rect(surface, self.color, (i * dis + 1, j * dis + 1, dis - 2, dis - 2))
        if eyes:
            centre = dis // 2
            radius = 3
            circleMiddle = (i * dis + centre - radius, j * dis + 8)
            circleMiddle2 = (i * dis + dis - radius * 2, j * dis + 8)
            pygame.draw.circle(surface, (0, 0, 0), circleMiddle, radius)
            pygame.draw.circle(surface, (0, 0, 0), circleMiddle2, radius)
        

class Snake(object):
    body = []
    turns = {}

    def __init__(self, color, pos):
        self.color = color
        self.head = Cube(pos)
        self.body.append(self.head)
        self.dirnx = 0
        self.dirny = 1

    def move(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            keys = pygame.key.get_pressed()

            for key in keys:
                if keys[pygame.K_LEFT]:
                    self.dirnx = -1
                    self.dirny = 0
                    self.turns[self.head.pos[:]] = [self.dirnx, self.dirny]

                elif keys[pygame.K_RIGHT]:
                    self.dirnx = 1
                    self.dirny = 0
                    self.turns[self.head.pos[:]] = [self.dirnx, self.dirny]

                elif keys[pygame.K_UP]:
                    self.dirnx = 0
                    self.dirny = -1
                    self.turns[self.head.pos[:]] = [self.dirnx, self.dirny]

                elif keys[pygame.K_DOWN]:
                    self.dirnx = 0
                    self.dirny = 1
                    self.turns[self.head.pos[:]] = [self.dirnx, self.dirny]

        for i, c in enumerate(self.body):
            p = c.pos[:]
            if p in self.turns:
                turn = self.turns[p]
                c.move(turn[0], turn[1])
                if i == (len(self.body) - 1):
                    self.turns.pop(p)
            else:
                if (c.dirnx == -1) and (c.pos[0] <= 0): c.pos = (c.rows - 1, c.pos[1])
                elif (c.dirnx == 1) and (c.pos[0] >= c.rows - 1): c.pos = (0, c.pos[1])
                elif (c.dirny == 1) and (c.pos[1] >= c.rows - 1): c.pos = (c.pos[0], 0)
                elif (c.dirny == -1) and (c.pos[1] <= 0): c.pos = (c.pos[0], c.rows - 1)
                else: c.move(c.dirnx,c.dirny)
        

    def reset(self, pos):
        self.head = Cube(pos)
        self.body = []
        self.body.append(self.head)
        self.turns = {}
        self.dirnx = 0
        self.dirny = 1


    def add_cube(self):
        tail = self.body[-1]
        dx, dy = tail.dirnx, tail.dirny

        if dx == 1 and dy == 0:
            self.body.append(Cube((tail.pos[0] - 1, tail.pos[1])))
        elif dx == -1 and dy == 0:
            self.body.append(Cube((tail.pos[0] + 1, tail.pos[1])))
        elif dx == 0 and dy == 1:
            self.body.append(Cube((tail.pos[0], tail.pos[1] - 1)))
        elif dx == 0 and dy == -1:
            self.body.append(Cube((tail.pos[0], tail.pos[1] + 1)))

        self.body[-1].dirnx = dx
        self.body[-1].dirny = dy
        

    def draw(self, surface):
        for i, c in enumerate(self.body):
            if i == 0:
                c.draw(surface, True)
            else:
                c.draw(surface)


def draw_wall(surface):
    global wall
    for w in wall:
        w.draw(surface)


def draw_grid(w, rows, surface):
    size_between = w // rows

    x = 0
    y = 0
    for i in range(rows):
        x = x + size_between
        y = y + size_between

        pygame.draw.line(surface, (255, 255, 255), (x, 0), (x, w))
        pygame.draw.line(surface, (255, 255, 255), (0, y), (w, y))
        

def redraw_window(surface):
    global rows, width, s, snack
    surface.fill((0, 0, 0))
    draw_wall(surface)
    s.draw(surface)
    snack.draw(surface)
    draw_grid(width, rows, surface)
    pygame.display.update()


def random_snack(rows, item):
    global wall
    positions = item.body

    while True:
        x = random.randrange(rows)
        y = random.randrange(rows)
        if len(list(filter(lambda z:z.pos == (x, y), positions))) > 0 or \
           len(list(filter(lambda z:z.pos == (x, y), wall))) > 0:
            continue
        else:
            break
        
    return (x, y)


def message_showinfo(subject, content):
    root = tk.Tk()
    root.attributes("-topmost", True)
    root.withdraw()
    messagebox.showinfo(subject, content)
    try:
        root.destroy()
    except:
        pass

def message_ask(subject, content):
    root = tk.Tk()
    root.attributes("-topmost", True)
    root.withdraw()
    msg_ask = tk.messagebox.askquestion(subject, content)
    if msg_ask == "yes": # continue to play?
        root.destroy()
    else:
        print("Thank you for playing!")
        sys.exit()


def load_level(rows):
    wall = []
    number_of_rows = 0

    if len(sys.argv) > 1: # load level
        file = open(sys.argv[1], "r")
        for line in file:
            number_of_rows += 1
        file.close()

        if number_of_rows != rows:
            print("Incompatible level size!")
            print("Compatible size is: ({}x{})".format(rows, rows))
            sys.exit()

        file = open(sys.argv[1], "r")
        for j, line in enumerate(file):
            for i, square in enumerate(line):
                if i >= number_of_rows:
                    break
                if (square == "X") or (square == "x"):
                    if (j == rows // 2) and (i >= rows // 2 - 1) and (i < rows - 1):
                        print("Incompatible level!")
                        print("Please make room in the middle for the snake")
                        print("{}.th line should be empty (without walls)".format(rows // 2))
                        sys.exit()
                    wall.append(Cube((i, j), color = (192, 192, 192)))
        file.close()
    return(wall)


def main():
    pygame.init()
    snack_sound = pygame.mixer.Sound("apple_crunch.wav")

    global width, rows, s, snack, wall
    width = 500
    rows = 20
    wall = load_level(rows)
    win = pygame.display.set_mode((width, width))
    s = Snake((255, 0, 0), (rows // 2, rows // 2))
    snack = Cube(random_snack(rows, s), color = (0, 255, 0))
    flag = True

    clock = pygame.time.Clock()
    
    while flag:
        pygame.time.delay(50)
        clock.tick(10)
        s.move()
        if s.body[0].pos == snack.pos:
            s.add_cube()
            pygame.mixer.Sound.play(snack_sound)
            snack = Cube(random_snack(rows, s), color = (0, 255, 0))

        for x in range(len(s.body)):
            if s.body[x].pos in list(map(lambda z:z.pos, s.body[x + 1:])) or \
               s.body[x].pos in list(map(lambda z:z.pos, wall)):
                game_over = "You lost! Your score: " + str(len(s.body))
                print(game_over)
                message_showinfo("You lost!", game_over)
                message_ask("Exit game", "Do you want to play again?")
                s.reset((rows // 2 ,rows // 2))
                break

        redraw_window(win)

main()
