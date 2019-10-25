import pygame
import os
import random
import datetime

# =================================================
# Auxiliary stuff
# =================================================

cheatmode = False
cheatlen = 1000

_image_library = {}
def get_image(path):
    imagepath = "resources/images/"
    path = imagepath + path
    global _image_library
    image = _image_library.get(path)
    if image == None:
            canonicalized_path = path.replace('/', os.sep).replace('\\', os.sep)
            image = pygame.image.load(canonicalized_path)
            _image_library[path] = image
    return image

class ScriptReader():

    main_script = []
    auxil_scripts = {}

    def __init__(self):
        self.main_script = [s.rstrip() for s in open("scripts/script.txt", 'r').readlines()]

    def getnextline(self):
        try:
            line = self.main_script.pop(0)
        except:
            return "\\NONE_LEFT"
        if (line == "\\DISABLE_SUCCESS"):
            return line
        if (line[0] == '\\'):
            name = line[1:]
            if not name in self.auxil_scripts:
                self.fill_auxil(name)
            return self.auxil_scripts[name].pop(0)
        return line

    def fill_auxil(self, name):
        self.auxil_scripts[name] = [s.rstrip() for s in open("scripts/" + name + ".txt", 'r').readlines()]

# =================================================
# The Sprites
# =================================================

# Template for Sprite objects
#    All sprites should have the following methods:
#     __init__(self)
#     event_update(self, event)
#     continuous_update(self)
#     render(self, screen)
class Sprite():
    _instances = list()
    def __init__(self, kwargs):
        Sprite._instances.append(self)
    def event_update(self, event, kwargs):
        pass
    def continuous_update(self, kwargs):
        pass
    def render(self, screen, kwargs):
        pass

    @classmethod
    def getinstances(cls):
        return cls._instances

    def delete(self):
        Sprite._instances.remove(self)

# Sets up game background and handles moving stripes
class Background(Sprite):
    shift = 0
    beginningtime = datetime.datetime.now()

    def __init__(self, kwargs):
        self.shift = 0
        self.beginningtime = datetime.datetime.now()
        Sprite.__init__(self, kwargs)

    def event_update(self, event, kwargs):
        Sprite.event_update(self, event, kwargs);

    def continuous_update(self, kwargs):
        Sprite.continuous_update(self, kwargs);

    def render(self, screen, kwargs):
        # Code for controlling stripe movement
        if (kwargs["state"] == "Typing"):
            self.shift += kwargs["wpm"]/10
        screen.blit(get_image("stripes.png"), (-self.shift % 800, 0))
        screen.blit(get_image("stripes.png"), (-self.shift % 800 - 800, 0))

        # Code for controlling sky background
        # Changes sky background based on time to simulate glitching
        if ((datetime.datetime.now() - self.beginningtime).total_seconds() < 1800): # Before 30 minutes
            index = round(68*datetime.datetime.now().minute/60)
            screen.blit(pygame.transform.scale(get_image("daynight/" + str(index) + ".gif"), (800,150)), (0,0))
        elif ((datetime.datetime.now() - self.beginningtime).total_seconds() < 2400): # 30-40 minutes
            screen.blit(pygame.transform.scale(get_image("glitchsky1.png"), (800,150)), (0,0))
        else: # After 40 minutes
            screen.blit(pygame.transform.scale(get_image("glitchsky2.png"), (800,150)), (0,0))

        screen.blit(get_image("background.png"), (0,0)) # Display racetrack background

        Sprite.render(self, screen, kwargs);

# Displays all text
class Dashboard(Sprite):
    def __init__(self, kwargs):
        pygame.font.init()
        Sprite.__init__(self, kwargs)

    def event_update(self, event, kwargs):
        Sprite.event_update(self, event, kwargs);

    def continuous_update(self, kwargs):
        Sprite.continuous_update(self, kwargs);

    def render(self, screen, kwargs):
        myfont = pygame.font.Font("resources/fonts/Consolas.ttf", 16)

        # Cuts prompt into the five lines to be actuallly rendered
        splitprompt = []
        cutlength = 65 # length of each line
        nolines = 5 # number of lines
        beginning = kwargs["position"]//cutlength*cutlength
        end = kwargs["position"]//cutlength*cutlength+cutlength*nolines
        remaining = kwargs["prompt"][beginning:end]
        while (len(remaining) > cutlength):
            splitprompt.append(remaining[0:cutlength])
            remaining = remaining[cutlength:]
        splitprompt.append(remaining)

        # Renders the text and highlighted character in the typing box
        if (kwargs["state"] == "Typing"):
            pygame.draw.rect(screen,(255,255,0),(30+(kwargs["position"])%cutlength*9,458,10,20))
        liney = 460
        for s in splitprompt:
            textsurface = myfont.render(s, False, (0, 0, 0))
            screen.blit(textsurface,(30,liney))
            liney += 18

        # Renders score, wpm, accuracy, title, subtitle, and subsubtitle
        textsurface = myfont.render(str(kwargs["score"]), False, (0, 0, 0))
        screen.blit(textsurface,(90,571))
        textsurface = myfont.render(str(kwargs["wpm"]), False, (255, 255, 255))
        screen.blit(textsurface,(675,474))
        textsurface = myfont.render(str(kwargs["accuracy"])+" %", False, (255, 255, 255))
        screen.blit(textsurface,(675,528))
        myfont = pygame.font.Font("resources/fonts/ComicSansMS.ttf", 50)
        textsurface = myfont.render(kwargs["title"], False, (200, 0, 0))
        screen.blit(textsurface,(200,250))
        myfont = pygame.font.Font("resources/fonts/ComicSansMS.ttf", 30)
        textsurface = myfont.render(kwargs["subtitle"], False, (200, 0, 0))
        screen.blit(textsurface,(200,310))
        myfont = pygame.font.Font("resources/fonts/ComicSansMS.ttf", 20)
        textsurface = myfont.render(kwargs["subsubtitle"], False, (200, 0, 0))
        screen.blit(textsurface,(200,350))

        # Renders the tiny car on the progress bar
        screen.blit(pygame.transform.scale(get_image("cars/0.png"), (30,10)), (220+540*kwargs["progress"],572))

        # Renders the ending screen upon the game's end state
        if (kwargs["state"] == "End game"):
            pygame.mixer.music.load('resources/sounds/buzz.ogg')
            pygame.mixer.music.play(-1)
            pygame.draw.rect(screen,(0,0,0),(0,0,800,600))
            myfont = pygame.font.Font("resources/fonts/Consolas.ttf", 14)
            endfile = open("scripts/end.txt", 'r')
            liney = 0
            for line in endfile:
                textsurface = myfont.render(line.strip(), False, (255, 255, 255))
                screen.blit(textsurface,(0,liney))
                liney += 20

        Sprite.render(self, screen, kwargs);

# Controls gameplay flow, reading script, listening to keystrokes, and starting and stopping rounds
class Engine(Sprite):
    sr = ScriptReader()

    def __init__(self, kwargs):
        # Iniitializes most of the global variables
        kwargs["prompt"] = ""
        kwargs["score"] = 0
        kwargs["wpm"] = 0
        kwargs["avg wpm"] = 40
        kwargs["accuracy"] = 0
        kwargs["title"] = "SuperTyper"
        kwargs["subtitle"] = "Press Enter to Begin."
        kwargs["subsubtitle"] = ""
        kwargs["state"] = "Start"
        kwargs["position"] = 0
        kwargs["progress"] = 0
        Sprite.__init__(self, kwargs)

    def event_update(self, event, kwargs):
        # State machine that listens for events
        if (kwargs["state"] == "Start"):
            if (event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN):
                kwargs["state"] = "Begin game"
        elif (kwargs["state"] == "Begin game"):
            pass
        elif (kwargs["state"] == "Start round"):
            pass
        elif (kwargs["state"] == "Typing"):
            if (event.type == pygame.KEYDOWN):
                if event.unicode == kwargs["prompt"][kwargs["position"]]:
                    kwargs["position"] += 1
                    kwargs["score"] += round(100 + kwargs["wpm"] + kwargs["accuracy"])
                if cheatmode and event.key == pygame.K_RETURN:
                    kwargs["position"] += cheatlen
                    kwargs["score"] += round(100 + kwargs["wpm"] + kwargs["accuracy"])
                kwargs["charstyped"] += 1
        elif (kwargs["state"] == "Success"):
            if (event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN):
                kwargs["state"] = "Start round"
        Sprite.event_update(self, event, kwargs);

    def continuous_update(self, kwargs):
        # State machine that handles continuous updates
        if (kwargs["state"] == "Start"):
            pass
        elif (kwargs["state"] == "Begin game"):
            pygame.mixer.music.load('resources/sounds/down.ogg')
            pygame.mixer.music.play(0)
            kwargs["disable success"] = False
            kwargs["title"] = ""
            kwargs["subtitle"] = ""
            kwargs["state"] = "Start round"
        elif (kwargs["state"] == "Start round" or kwargs["state"] == "Start round intermediate"):
            pygame.mixer.music.load('resources/sounds/start.ogg')
            pygame.mixer.music.play(0)
            kwargs["title"] = ""
            kwargs["subtitle"] = ""
            kwargs["subsubtitle"] = ""
            temp = self.sr.getnextline();
            if (temp == "\\DISABLE_SUCCESS"):
                kwargs["disable success"] = True
                kwargs["prompt"] = self.sr.getnextline();
            elif (temp == "\\NONE_LEFT"):
                kwargs["state"] = "End game"
                return;
            else:
                kwargs["prompt"] = temp;
            kwargs["position"] = 0
            kwargs["time begun"] = datetime.datetime.now()
            kwargs["charstyped"] = 0
            kwargs["progress"] = 0
            if (kwargs["state"] == "Start round intermediate"):
                kwargs["state"] = "Typing"
            else:
                kwargs["state"] = "Start round intermediate"
        elif (kwargs["state"] == "Typing"):
            pygame.mixer.music.load('resources/sounds/running.ogg')
            pygame.mixer.music.play(0)
            if (kwargs["position"] >= len(kwargs["prompt"]) - 1):
                kwargs["state"] = "Success"
            timepassed = datetime.datetime.now() - kwargs["time begun"]
            kwargs["wpm"] = round(kwargs["position"]/4.7/(timepassed.total_seconds()/60 + 0.01)) # 4.7 chars per word
            kwargs["accuracy"] = round(kwargs["position"]/(kwargs["charstyped"]+0.01)*100,1)
            kwargs["progress"] = kwargs["position"]/len(kwargs["prompt"])
        elif (kwargs["state"] == "Success"):
            pygame.mixer.music.load('resources/sounds/bell.ogg')
            pygame.mixer.music.play(0)
            if (not kwargs["disable success"]):
                kwargs["title"] = "Success!"
                kwargs["avg wpm"] = (kwargs["wpm"] + kwargs["avg wpm"]*2)/3
                addendum = ""
                if (kwargs["place"] == 1):
                    addendum = "You got 1st place."
                elif (kwargs["place"] == 2):
                    addendum = "You got 2nd place."
                elif (kwargs["place"] == 3):
                    addendum = "You got 3rd place."
                else:
                    addendum = "You got " + str(kwargs["place"]) + "th place."
                kwargs["subsubtitle"] = "Press Enter to Continue."
                kwargs["subtitle"] = addendum
            else:
                kwargs["state"] = "Start round"
        Sprite.continuous_update(self, kwargs);

    def render(self, screen, kwargs):
        Sprite.render(self, screen, kwargs);

# Displays all the cars
class Cars(Sprite):
    startx = 300
    carspeeds = []
    carimages = []
    carxs = []
    mainx = 300
    prevxstart = startx + 90
    beginningtime = datetime.datetime.now()

    def __init__(self, kwargs):
        Sprite.__init__(self, kwargs)
    
    def event_update(self, event, kwargs):
        Sprite.event_update(self, event, kwargs);
    
    def continuous_update(self, kwargs):
        # State machine
        if (kwargs["state"] == "Start round" or kwargs["state"] == "Start round intermediate"):
            self.carspeeds = [random.random()*50+(kwargs["avg wpm"]-40) for i in range(4)]
            if ((datetime.datetime.now() - self.beginningtime).total_seconds() < 2500):
                self.carimages = ["cars/"+str(random.randint(0,7))+".png" for i in range(4)]
            else:
                self.carimages = ["cars/"+str(random.randint(0,8))+".png" for i in range(4)]
            self.carxs = [Cars.startx for i in range(4)]
            self.mainx = Cars.startx
            self.prevxstart = Cars.startx+90
            if (kwargs["state"] == "Start round intermediate"):
                kwargs["state"] = "Typing"
            else:
                kwargs["state"] = "Start round intermediate"
        elif (kwargs["state"] == "Typing"):
            timepassed = datetime.datetime.now() - kwargs["time begun"]
            # Most of the time, we have the cars scrolling
            if (kwargs["progress"] < 0.97):
                for i in range(4):
                    target = (self.carspeeds[i]*timepassed.total_seconds()/60*4.7-kwargs["position"])*20+Cars.startx
                    self.carxs[i] += (target - self.carxs[i])/20
            else: # At the end, we have the cars move to the right end of the screen to finish
                self.mainx += (Cars.startx + (kwargs["progress"]-0.97)/0.02 * (800-Cars.startx) - self.mainx)/10
                for i in range(4):
                    carprogress = self.carspeeds[i]*timepassed.total_seconds()/60*4.7/len(kwargs["prompt"])
                    self.carxs[i] += ((carprogress-0.97)/0.02*800 - self.carxs[i])/10
            place = 5
            for n in self.carspeeds:
                if kwargs["wpm"] >= n:
                    place -= 1
            kwargs["place"] = place
        Sprite.continuous_update(self, kwargs);

    def render(self, screen, kwargs):
        if (kwargs["state"] == "Start round"):
            screen.blit(pygame.transform.scale(get_image("cars/0.png"), (80,25)), (Cars.startx,210))
            for i in range(4):
                screen.blit(pygame.transform.scale(get_image(self.carimages[i]), (80,25)), (Cars.startx,210+(i+1)*40))
        elif (kwargs["state"] == "Typing"):
            if (kwargs["progress"] < 0.1):
                target = Cars.startx+90-kwargs["progress"]/0.03*(Cars.startx+130)
                self.prevxstart += (target-self.prevxstart)/10
                screen.blit(pygame.transform.scale(get_image("start.png"), (30,220)), (self.prevxstart,199))
            if (kwargs["progress"] > 0.97):
                screen.blit(pygame.transform.scale(get_image("finish.png"), (30,220)), (800-30,199))
            screen.blit(pygame.transform.scale(get_image("cars/0.png"), (80,25)), (self.mainx,210))
            for i in range(4):
                screen.blit(pygame.transform.scale(get_image(self.carimages[i]), (80,25)), (self.carxs[i],210+(i+1)*40))
        Sprite.render(self, screen, kwargs);

# =================================================
# THE MAIN GAME LOOP
# =================================================

pygame.init()
screen = pygame.display.set_mode((800,600))
running = True
clock = pygame.time.Clock()

pygame.display.set_caption('SuperTyper')

# Dictionary that stores "global" variables
kwargs = {}
# Declare all sprites here
sprites_list = [Background(kwargs),
                Engine(kwargs),
                Dashboard(kwargs),
                Cars(kwargs),]

# Main loop
while running:

    sprites_list = Sprite.getinstances()
    
    # Continuous updates
    for sprite in sprites_list:
        sprite.continuous_update(kwargs)

    # Rendering
    screen.fill((255, 255, 255))
    spritescopy = sprites_list.copy()
    for sprite in spritescopy:
        sprite.render(screen, kwargs)

    pygame.display.update()
    clock.tick(60) # Limits frame rate to 60 fps

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break
        for sprite in sprites_list:
            sprite.event_update(event, kwargs)