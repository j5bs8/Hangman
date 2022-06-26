import pygame as pg
import sys
import os
import math
import bs4
import requests
from tkinter import messagebox

if not pg.font:
    messagebox.showerror('Error', 'Pygame failed to find font')
if not pg.mixer:
    messagebox.showerror('Error', 'Pygame failed to find audio device')

main_dir = os.path.split(os.path.abspath(__file__))[0]
data_dir = os.path.join(main_dir, "data")

def load_sound(name):
    '''Checks if mixer module was imported correctly.
    Returns dummy instance if so or returns Sound object'''
    class NoneSound:
        
        def play(self):
            pass
    
    if not pg.mixer or not pg.mixer.get_init():
        return NoneSound()

    fullname = os.path.join(data_dir, name)
    sound = pg.mixer.Sound(fullname)

    return sound

class Game:

    RESOLUTION = WIDTH, HEIGHT = 1000, 600

    LIGHT_BLUE = pg.color.Color(135,206,250)
    BLUE = pg.color.Color(30, 100, 170)
    WHITE = pg.color.Color(255, 255, 255)
    BLACK = pg.color.Color(0, 0, 0)
    RED = pg.color.Color(255, 0, 0)

    LETTERS = [chr(letter) for letter in range(65, 91)]
    BUTTON_POSITONS_FIRST_ROW = [(x, 430) for x in range(100, WIDTH, 60)]
    BUTTON_POSITONS_SECOND_ROW = [(x, 500) for x in range(100, WIDTH, 60)]    

    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode(self.RESOLUTION)
        pg.display.set_caption('Hangman')
        self.word_font = pg.font.Font(pg.font.match_font('comicsans'), 30)
        self.letter_font = pg.font.Font(pg.font.match_font('comicsans'), 24)
        self.description_font = pg.font.Font(pg.font.match_font('comicsans'), 16)
        self.clock = pg.time.Clock()
        self.correct = load_sound('correct.mp3')
        self.wrong = load_sound('wrong.mp3')
        self.soundtrack = load_sound('background.mp3')
        self.lost = load_sound('lost.mp3')
        self.win = load_sound('win.mp3')
        #self.soundtrack.play()
        self.new_game()
    
    def __check_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT or event.type == pg.K_ESCAPE:
                sys.exit() 
            
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    self.new_game()
            
            if event.type == pg.MOUSEBUTTONDOWN:
                for sprite in self.all_buttons.sprites():
                    if sprite.is_clicked():
                        sprite.control_button()
                        self.all_buttons.remove(sprite)
                        self.word.draw()
                                 
    def update(self):
        self.clock.tick(60)
        self.all_platforms.update()
        self.all_buttons.update()
        self.hangman.update()
        self.word.update()
        pg.display.flip()

    def new_game(self):
        
        self.buttons_platform = Platform(self, 20, 400, self.WIDTH - 40, 180)
        self.hangman_platform = Platform(self, 20, 20, self.buttons_platform.width / 2, 390 - 20)
        self.word_platform = Platform(self, self.hangman_platform.width + 30,
                                             self.hangman_platform.height/ 4 - 10,
                                             self.hangman_platform.width - 10,
                                             self.hangman_platform.height / 4 )

        self.description_platform = Platform(self, self.hangman_platform.width + 30,
                                             self.hangman_platform.height/ 2,
                                             self.hangman_platform.width - 10,
                                             self.hangman_platform.height / 2 + 20)

        self.all_platforms = pg.sprite.RenderPlain([self.buttons_platform, self.hangman_platform, self.word_platform, self.description_platform])
        self.all_buttons = pg.sprite.RenderPlain()
        self.create_buttons()
        self.hangman = Hangman(self)
        self.word = Word(self)

        self.word.draw()
        
    
    def create_buttons(self):

        for index, button in enumerate(self.LETTERS):
            self.button = Button(self)
            self.button.letter = button

            if index < 13: self.button.rect = self.BUTTON_POSITONS_FIRST_ROW[index]
            elif index <= 26: self.button.rect = self.BUTTON_POSITONS_SECOND_ROW[index - 13]
            
            self.text = self.letter_font.render(self.button.letter, True, (255, 255, 255))
            self.button.letter_pos = self.text.get_rect(centerx=self.button.width / 2, centery=self.button.height / 2)
            self.all_buttons.add(self.button)
            self.button.image.blit(self.text, self.button.letter_pos)
    
    def draw_text(self,platform , font, string, pos_x, pos_y):
        self.text = font.render(string, True, self.BLACK)
        self.textpos = self.text.get_rect(x=pos_x, y=pos_y)
        platform.image.blit(self.text, self.textpos)

    def draw(self):
        self.screen.fill(self.LIGHT_BLUE)
        self.all_platforms.draw(self.screen)
        self.all_buttons.draw(self.screen)
        self.hangman.draw_hangman()
    
    def game_over(self, state):
        self.menu = Menu(self)
        self.menu.message = 'Game Over!'
        self.menu.instruction = 'PRESS [SPACE] TO RESTART'
        self.menu.word_text = "Your word was: '{}'".format(self.word.word)
        if state:
            self.menu.message = 'Congratulations!'
            self.menu.instruction = 'PRESS [SPACE] FOR NEXT WORD'

        self.menu.draw()
        self.all_buttons.empty()
        self.all_platforms.empty()

    def run(self):
        while True:
            self.__check_events()
            self.update()
            self.draw()

class Button(pg.sprite.Sprite):

    def __init__(self, game):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        self.letter = ''
        self.letter_pos = (0, 0)
        self.width = 52
        self.height = 52
        self.radius = 26
        self.color = self.game.BLUE
        self.image = pg.surface.Surface((self.width, self.height), pg.SRCALPHA)
    
        self.draw_button()

    def draw_button(self):
        pg.draw.circle(self.image, self.color, (self.width / 2, self.height /2), self.radius)

    def is_clicked(self):
        px = pg.mouse.get_pos()[0]
        py = pg.mouse.get_pos()[1]

        cx = self.rect[0] + self.width / 2
        cy = self.rect[1] + self.height / 2

        dx = px - cx
        dy = py - cy

        if math.sqrt(dx ** 2 + dy ** 2) < self.radius: 
            return True
        return False
    
    def control_button(self):
        if self.letter in self.game.word.word:
            for index, letter in enumerate(self.game.word.word):
                if self.letter == letter:
                    self.game.word.change_word(index, letter)
            self.game.correct.play()
        else:
            self.game.hangman.add_segment()
            self.game.wrong.play()
            


class Platform(pg.sprite.Sprite):

    def __init__(self, game, left, top, width, height):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        self.width = width
        self.height = height
        self.left = left
        self.top = top
        self.image = pg.surface.Surface((self.width, self.height), pg.SRCALPHA).convert()
        self.rect = pg.rect.Rect(left, top, width, height)
        self.draw()
    
    def draw(self):
        pg.draw.rect(self.image, self.game.WHITE, (0, 0, self.width, self.height))
        pg.draw.rect(self.image, self.game.BLUE, (0, 0, self.width, self.height), 7)



class Hangman:

    SEGMENTS_COORDS = (((80, 300), (400, 300)),    
                        ((140, 300), (140, 60)),    
                        ((110, 100), (300, 80)),
                        ((285, 80), (285, 150)),
                        ((285, 165), 15),
                        ((280, 165), (280, 230)),
                        ((280, 170), (300, 210)),
                        ((280, 170), (260, 210)),
                        ((280, 230), (290, 270)),
                        ((280, 230), (270, 270)))

    def __init__(self, game):
        self.game = game
        self.errors = 4
        self.segments = [((80, 300), (400, 300)),    
                        ((140, 300), (140, 60)),    
                        ((110, 100), (300, 80)),
                        ((285, 80), (285, 150))]

    def update(self):
        self.check_hangman()

    def draw_hangman(self):
        for index, segment in enumerate(self.segments):
            if index == 4:
                self.draw_circle(segment[0], segment[1])
                continue
            self.draw_line(segment[0], segment[1])

    def add_segment(self):
        self.segments.append(self.SEGMENTS_COORDS[self.game.hangman.errors])
        self.errors += 1

    def draw_line(self, start_pos, end_pos):
        pg.draw.line(self.game.hangman_platform.image, self.game.BLACK, start_pos, end_pos, 10)
    
    def draw_circle(self, centre_pos, radius):
        pg.draw.circle(self.game.hangman_platform.image, self.game.BLACK, centre_pos, radius)
    
    def check_hangman(self):
        if len(self.segments) == len(self.SEGMENTS_COORDS):
            self.game.game_over(False)
            self.game.lost.play()

class Word:
    
    def __init__(self, game):
        self.game = game
        self.errors = 0
        self.url = 'https://randomword.com/'

        self.generate_new_word()

        self.secret_word = ('_ ' * len(self.word)).rstrip(' ')
        self.secret_word = self.secret_word.split(' ')

    def generate_new_word(self):
        r = requests.get(self.url).text
        soup = bs4.BeautifulSoup(r, 'html.parser')
        self.word = soup.find('div', attrs={'id':'random_word'}).string.upper()
        self.word_description = soup.find('div', attrs={'id':'random_word_definition'}).string.capitalize()
        self.game.draw_text(self.game.description_platform, self.game.description_font, self.word_description, 10, 10) 

    def update(self):
        self.check_word()

    def draw(self):
        self.new_secret_word = ''
        for letter in self.secret_word:
            self.new_secret_word += letter + ' '

        self.game.word_platform.draw()
        self.text = self.game.word_font.render(self.new_secret_word, True, self.game.BLACK)
        self.textpos = self.text.get_rect(centerx=self.game.word_platform.width / 2, centery=self.game.word_platform.height / 2)
        self.game.word_platform.image.blit(self.text, self.textpos)

    def change_word(self, index, letter):
        self.secret_word[index] = letter

    def check_word(self):
        if set(self.word) == set(self.secret_word):
            self.game.game_over(True)
            self.game.win.play()

class Menu:
 
    def __init__(self, game):
        self.game = game
        self.menu = pg.surface.Surface((self.game.WIDTH, self.game.HEIGHT)).convert()
        self.menu.fill(self.game.BLUE)
        self.rect = self.menu.get_rect(centerx=self.game.WIDTH / 2, centery=self.game.HEIGHT / 2)

        self.message = ''
        self.instruction = ''
        self.word_text = ''
        
    def draw(self):
        self.game.screen.blit(self.menu, self.rect)

        self.text = self.game.letter_font.render(self.message, True, self.game.WHITE)
        self.text_pos = self.text.get_rect(centerx=self.game.WIDTH / 2, centery=self.game.HEIGHT / 2)
        self.game.screen.blit(self.text, self.text_pos)

        self.text = self.game.letter_font.render(self.word_text, True, self.game.WHITE)
        self.text_pos = self.text.get_rect(centerx=self.game.WIDTH / 2, centery=self.game.HEIGHT / 2 + 30)
        self.game.screen.blit(self.text, self.text_pos)

        self.text = self.game.letter_font.render(self.instruction, True, self.game.WHITE)
        self.text_pos = self.text.get_rect(centerx=self.game.WIDTH / 2, centery=self.game.HEIGHT / 2 + 60)
        self.game.screen.blit(self.text, self.text_pos)


if __name__ == '__main__':
    game = Game()
    game.run()