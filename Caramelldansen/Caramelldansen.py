import sys
import pygame
from pygame.locals import *
import math
import time
import os
import random

#Init
pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.mixer.init()
pygame.init()

#Screen
screenWidth = 800
screenHeight = 800
dispSurf = pygame.display.set_mode((screenWidth,screenHeight))
pygame.display.set_caption("Caramelldansen")

#Time
deltaTime = 0
fpsLimit = 500
clock = pygame.time.Clock()

#Colors
color = (255,0,0)
darkGrey = pygame.Color(30,30,30)
midGrey = pygame.Color(70,70,70)
lightGrey = pygame.Color(100,100,100,100)

#Rainbow
phase = 0
rainbowTimer = 0
rainbowSpeed = 7

#Fonts
pygame.font.init()
font1 = pygame.font.Font('freesansbold.ttf', 26)
font1.bold = True
font1.underline = True
font2 = pygame.font.Font('freesansbold.ttf', 26)
font3 = pygame.font.Font('freesansbold.ttf', 60)
font4 = pygame.font.Font('freesansbold.ttf', 40)

#Texts
text1 = font1.render('Epilepsy warning!', True, (255,0,0), None)
textRect1 = text1.get_rect()
textRect1.center = (screenWidth // 2, screenHeight // 2)

text2 = font2.render('Controls: Arrow keys or DFJK', True, (0,0,255), None)
textRect2 = text2.get_rect()
textRect2.center = (screenWidth // 2,screenHeight // 2 + text1.get_height() + 50)

text5 = font2.render('Press space to start', True, (0,0,255), None)
textRect5 = text5.get_rect()
textRect5.center = (screenWidth // 2,screenHeight // 2 + text1.get_height() + text2.get_height() + 100)

text6 = font3.render('SONG FINISHED!', True, (100,0,255), None)
textRect6 = text6.get_rect()
textRect6.center = (screenWidth // 2, screenHeight // 2 - 220)

text3 = font3.render('GAME OVER!', True, (100,0,255), None)
textRect3 = text3.get_rect()
textRect3.center = (screenWidth // 2, screenHeight // 2 - 220)

fonts = pygame.font.get_fonts()
scoreFont = pygame.font.SysFont(fonts[random.randint(0,len(fonts)-1)]+'.ttf', 70)

#Game
playModeOn = False
secondGame = False
victory = False
timeGameStartPressed = 0
timeMusicStarted = 0

#Board
boardOffset = 30
notesXoffset = boardOffset + 14

#Hitting notes
hitEffectTime = 0
noteHit = -1

#Score
score = 0

#Health
health = 400
missDamage = 70
hitHealAmount = 10

#Sounds

pygame.mixer.music.load(os.path.join('sounds', 'caramelldansen.mp3'))
pygame.mixer.music.set_volume(0.3)
hitSound = pygame.mixer.Sound(os.path.join('sounds', 'hit.ogg'))
missSound = pygame.mixer.Sound(os.path.join('sounds', 'miss.ogg'))
hitSound.set_volume(0)
missSound.set_volume(1)

#Images
arrows, emptyArrows, hitArrows, animationFrames = ([],[],[],[])
for x in range(4):
    arrows.append(pygame.image.load(os.path.join('arrows', str(x) + '.png')))
    emptyArrows.append(pygame.image.load(os.path.join('arrows', 'empty_'+str(x) + '.png')))
    hitArrows.append(pygame.image.load(os.path.join('arrows', 'hit_'+str(x) + '.png')))

for x in range(7):
    animationFrames.append(pygame.image.load(os.path.join('dance', str(x) + '.png')))

#Animation
animationFrame = 0
animationFPS = 9.8
animationTimer = 0

danceHeight = animationFrames[0].get_height()
danceWidth = animationFrames[0].get_width()
animationChoords = (screenWidth-danceWidth-20,(screenHeight//2)-(danceHeight//2))

#Hitzone
hitZoneHeight = 100
hitZoneOffset = 0.5
hitZoneCenter = screenHeight-60
hitZone = (hitZoneCenter-hitZoneHeight*(1-hitZoneOffset),hitZoneCenter+hitZoneHeight*hitZoneOffset)

#Notes
noteSpeed = 700
songLength = 180.0
songTimeToFirstNote = 1.2
songTimeToLastNote = 175.0
BPM = 164.7

noteImageHeight = arrows[0].get_height()
halfNoteImgHeight = noteImageHeight//2
noteSpawnHeight = -noteImageHeight

noteTravelDistance = hitZoneCenter-noteSpawnHeight
noteTravelTime = noteTravelDistance/noteSpeed

timeSpawnFirstNote = songTimeToFirstNote - noteTravelTime
timeSpawnLastNote = songTimeToLastNote - noteTravelTime
timeBetweenNoteSpawns = 60/BPM
noteTimer = 0


class Note():
    def __init__(self, noteNumber, height, image):
        self.noteNumber = noteNumber
        self.height = height
        self.image = image

def MenuScreen():
    global secondGame, score, victory
    #Display text
    dispSurf.fill((255,200,200))
    dispSurf.blit(text1, textRect1)
    dispSurf.blit(text2, textRect2)
    dispSurf.blit(text5, textRect5)

    #Only display these texts if one game already played
    if secondGame:
        if victory:
            dispSurf.blit(text6, textRect6)
        else:
            dispSurf.blit(text3, textRect3)
        text4 = font4.render('Score: '+str(score), True, (100,0,255), None)
        textRect4 = text4.get_rect()
        textRect4.center = (screenWidth // 2, screenHeight // 2 - 150)
        dispSurf.blit(text4, textRect4)
        
    pygame.display.update()

MenuScreen()

def StartGame():
    global playModeOn, timeGameStartPressed, health, score, notes, noteTimer, animationTimer, phase, rainbowTimer, timeMusicStarted
    playModeOn = True

    #Reset values
    victory = False
    health = 400
    score = 0
    notes = []
    noteTimer = 0
    animationTimer = 0
    phase = 0
    rainbowTimer = 0
    pygame.mixer.music.play()
    timeMusicStarted = time.time()

def Events():
    #Get events from pygame
    for event in pygame.event.get():
        #On press the window's X button
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
            
        #Key inputs
        elif event.type == pygame.KEYDOWN:
            
            #Start game on space pressed
            if not playModeOn:
                if event.key == pygame.K_SPACE:
                    timeGameStartPressed = time.time()
                    StartGame()
                    
            #Arrow keys and dfjk
            else:
                if (event.key == pygame.K_LEFT or event.key == pygame.K_d):
                    NoteKeyPressed(0)
                elif (event.key == pygame.K_DOWN or event.key == pygame.K_f):
                    NoteKeyPressed(1)
                elif (event.key == pygame.K_UP or event.key == pygame.K_j):
                    NoteKeyPressed(2)
                elif (event.key == pygame.K_RIGHT or event.key == pygame.K_k):
                    NoteKeyPressed(3)
                        

def Rainbow():
    global phase, rainbowTimer, rainbowSpeed, deltaTime, color
    
    #Cycle through the rgb values to make a rainbow
    r=0
    g=0
    b=0
    rainbowTimer += rainbowSpeed * deltaTime
    if (rainbowTimer >= 1):
        rainbowTimer -= 1
        phase = (phase + 1) % 6

    if (phase == 0):
        r = 255
        g = 255*rainbowTimer
        b = 0
    elif (phase == 1):
        r = 255*(1-rainbowTimer)
        g = 255
        b = 0
    elif (phase == 2):
        r = 0
        g = 255
        b = 255*rainbowTimer
    elif (phase == 3):
        r = 0
        g = 255*(1-rainbowTimer)
        b = 255
    elif (phase == 4):
        r = 255*rainbowTimer
        g = 0
        b = 255
    elif (phase == 5):
        r = 255
        g = 0
        b = 255*(1-rainbowTimer)

    color = (r,g,b)
    dispSurf.fill(color)

def Dance():
    #Draw current animation frame
    global animationFrame, animationTimer
    danceImg = animationFrames[animationFrame]
    dispSurf.blit(danceImg,animationChoords)
    
    #Periodically switch animation frame
    animationTimer += deltaTime
    if (animationTimer >= 1/animationFPS):
        animationTimer -= 1/animationFPS
        animationFrame = (animationFrame + 1)%7

def Board():
    #Base
    pygame.draw.rect(dispSurf, midGrey,(boardOffset,0,400,screenHeight))
    
    #Hit zone
    pygame.draw.rect(dispSurf, lightGrey, (boardOffset,hitZone[0],400,hitZone[1]-hitZone[0]))
    
    #Vertical lines
    for x in range(5):
        pygame.draw.rect(dispSurf, darkGrey, (boardOffset+100*x,0,10,screenHeight))
    
    #Health bar
    pygame.draw.rect(dispSurf, midGrey, (boardOffset+410,screenHeight//2-200,40,400))
    pygame.draw.rect(dispSurf, (255-color[0],255-color[1],255-color[2]), (boardOffset+410,screenHeight//2+200-health,40,health))

    #Empty arrows
    for x in range(4):
        dispSurf.blit((hitArrows[x] if noteHit == x else emptyArrows[x]),(notesXoffset+100*x,hitZoneCenter-halfNoteImgHeight))

def HandleNotes():
    global noteSpawnHeight, timeBetweenNoteSpawns, noteTimer, noteSpeed, notes, noteImageHeight, timeGameStartPressetimeSpawnFirstNote, health
    
    #Move notes down and kill if below screen
    songTime = time.time()-timeMusicStarted
    if songTime < timeSpawnFirstNote or songTime > timeSpawnLastNote:
        return
    noteTimer += deltaTime
    for x in range(1,len(notes)):
        notes[-x].height += noteSpeed * deltaTime
        if notes[-x].height > screenHeight:
            notes.pop(-x)
            health -= missDamage
        else:
            dispSurf.blit(notes[-x].image,(notesXoffset+(notes[-x].noteNumber*100), notes[-x].height))
            
    #Spawn new notes periodically
    if noteTimer < timeBetweenNoteSpawns:
        return
    noteTimer -= timeBetweenNoteSpawns
    randomInt = random.randint(0,3)
    noteImg = arrows[randomInt]
    notes.append(Note(randomInt, noteSpawnHeight, noteImg))

def NoteKeyPressed(numPressed):
    global notes, hitZone, score, noteHit, hitEffectTime, health, noteImageHeight
    
    #Check if there is a note in the zone matching the key pressed
    for x in range(1,len(notes)):
        noteHeight = notes[-x].height+halfNoteImgHeight
        if notes[-x].noteNumber == numPressed and noteHeight >= hitZone[0] and noteHeight <= hitZone[1]:
            hitSound.play()
            score += 1
            notes.pop(-x)
            hitEffectTime = time.time()
            noteHit = numPressed
            
            if health < 400:
                health += hitHealAmount
            break
        
    #If not, kill lowest note and lower health
    else:
        missSound.play()
        health -= missDamage
        if (len(notes)!=0):
            notes.pop(0)

def EffectTimer():
    global noteHit
    #Time the white flash effect on the empty keys on note hit
    if (time.time()-hitEffectTime > 0.1):
        noteHit = -1
        

def Score():
    #Display score
    text = scoreFont.render(str(score),True,(255-color[0],255-color[1],255-color[2]))
    dispSurf.blit(text,(screenWidth-text.get_width()-70,50))
     
def GameEndLogic():
    global timeMusicStarted, songLength, health, victory
    
    #Game Over
    if health <= 0:
        EndGameRoutine();
        return
    
    #Song Finished
    if time.time()-timeMusicStarted > songLength:
        victory = True
        EndGameRoutine()
            
def EndGameRoutine():
    global playModeOn, secondGame
    playModeOn = False
    secondGame = True
    pygame.mixer.music.stop()
    MenuScreen()

def Main():
    global deltaTime
    deltaTime = clock.tick(fpsLimit)*0.001
    Events()
    if not playModeOn:
        return
    Rainbow()
    Dance()
    Board()
    HandleNotes()
    Score()
    EffectTimer()
    GameEndLogic()
    pygame.display.update()

while True:
    Main()
