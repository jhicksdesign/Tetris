'''
Created on Apr 23, 2017

@author: Jordan Hicks and Frank Ortwerth
'''

from collections import Counter
from random import shuffle

import pygame
from tkinter import *
# Tkinters message box before python 3 used the import tkMessageBox
from tkinter import messagebox
import os

from Shape import Tetrominoes


class Board:
    # Constant sizes for board and cells.
    CELL_SIZE = 40
    BOARD_WIDTH = 400
    BOARD_LENGTH = 800

    def __init__(self, parent):

        # Setting up the canvas for TKinter
        self.gameFrame = Canvas(master, background="BLACK", width=self.BOARD_WIDTH, height=self.BOARD_LENGTH)
        self.infoFrame = Canvas(master, width=200, height=self.BOARD_LENGTH)
        self.gameFrame.pack(side=LEFT, fill=BOTH, expand=0)
        self.infoFrame.pack(side=RIGHT, fill=BOTH, expand=0)

        # Setting title for tkinter and making it so the canvas is not resizable.
        master.title("Tetris!")
        master.resizable(0, 0)

        # Creates a box around where the next shape will go.
        self.infoFrame.create_rectangle(50, 60, 160, 140, width=4, outline="Grey")

        # Draws the new game button to the info frame.
        button1 = Button(master, text="New Game", command=self.newGame)
        button1.configure(width=10, activebackground="#33B5E5", relief='groove')
        self.button1_window = self.infoFrame.create_window(15, 230, anchor=NW, window=button1)

        # Draws the exit game button to the info frame.
        button2 = Button(master, text="Exit Game", command=lambda: self.exitGame())
        button2.configure(width=10, activebackground="#33B5E5", relief='groove')
        self.button2_window = self.infoFrame.create_window(110, 230, anchor=NW, window=button2)

        # Initializing important variables for the game.
        self.readScore = []
        self.getScores = None
        self.gamePaused = False
        
        self.parent = parent

        self.tickRate = 1000

        self.shapesList = [0, 1, 2, 3, 4, 5, 6]
        self.nextShapesList = [0, 1, 2, 3, 4, 5, 6]

        shuffle(self.shapesList)
        self.currentShape = self.shapesList.pop(0)
        self.nextShape = self.shapesList[0]

        self.completeLines = []
        self.totalLines = 0
        self.totalLineMult = 0
        self.levelInfo = 1
        self.paused = False
        self.currentScore = StringVar()
        self.currentScore.set(0)
        self.currentLevel = StringVar()
        self.currentLevel.set(1)
        self.gameOver = False

        self.getScores = StringVar()
        self.scores = []

        # Drawing important labels to the board.
        highScoresLabel = Label(self.infoFrame, text="High Scores!", font=('Helvetica', 20))
        highScoresLabel.pack()
        self.infoFrame.create_window(100, 550, window=highScoresLabel)

        highScores = Label(self.infoFrame, textvariable=self.getScores, font=('Helvetica', 12))
        highScores.pack()
        self.infoFrame.create_window(100, 675, window=highScores)

        scoreLabel = Label(self.infoFrame, text="Current Score", font=('Helvetica', 20))
        scoreLabel.pack()
        self.infoFrame.create_window(100, 360, window=scoreLabel)

        scoreBoard = Label(self.infoFrame, textvariable=self.currentScore, font=('Helvetica', 15))
        scoreBoard.pack()
        self.infoFrame.create_window(100, 400, window=scoreBoard)

        levelLabel = Label(self.infoFrame, text="Current Level", font=('Helvetica', 20))
        levelLabel.pack()
        self.infoFrame.create_window(100, 460, window=levelLabel)

        levelInfo = Label(self.infoFrame, textvariable=self.currentLevel, font=('Helvetica', 15))
        levelInfo.pack()
        self.infoFrame.create_window(100, 500, window=levelInfo)

        shapeLabel = Label(self.infoFrame, text="Next Shape", font=('Helvetica', 20))
        shapeLabel.pack()
        self.infoFrame.create_window(100, 40, window=shapeLabel)

        # Setting up the current shape.
        self.current_shape = Tetrominoes(self.gameFrame, self.infoFrame, self.currentShape, self.nextShape)

        self.current_shape.createShGame()
        self.current_shape.createShInfo()

        # Beginning timer for shape dropping.
        self.ticking = self.gameFrame.after(self.tickRate, self.tick)
        
        # Setting up keybinds.
        master.bind("<Key>", self.eventHandler)
        
        # Setting up sound and music.
        pygame.mixer.init()
        self.channel = pygame.mixer.Channel(0)
        self.music = pygame.mixer.Sound("Tetris.wav")
        self.channel.play(self.music, loops=-1)
        self.channel.set_volume(.05)
        self.lineClearSound = pygame.mixer.Sound("LineClear.ogg")
        self.lineClearSound.set_volume(.05)
        
        # Checks if word file is empty from closing game while entering high score, if it is populates it with default scores.
        self.populateWordFile()
        
        # Getting the current high scores and appending them to the board.
        self.getHighScores()
        self.showHighScores()

        # Setting up the game over image.
        self.gameOverImage = PhotoImage(file="gameOver.gif")
        
    # Checks if there are any completed lines, gets the next shape from the bag and creates a tetromino from it.
    # Then sets the currentScore variable, also checks if there are more than 10 lines cleared, if there are it
    # increases the current level by 1, sets the total line counter to 0 and reduces the tick rate by 75 if the user
    # is currently at a level lower than 12.
    def nextShapes(self):
        self.clearLines()
        self.shapeBag()
        self.createTetromino()
        self.currentScore.set((50 * self.totalLineMult) * self.levelInfo)
        if self.totalLines >= 10:
            self.totalLines = 0
            self.levelInfo += 1
            self.currentLevel.set(self.levelInfo)
            if self.levelInfo <= 12:
                self.tickRate -= 75

    # Uses TKinter's after method to queue a call of itself every tickrate.
    def tick(self):
        self.ticking = self.gameFrame.after(self.tickRate, self.tick)
        # Determines if the shape cannot move anymore and checks if the game is over, if it is pauses input from the
        # user and runs the game over animation, else it spawns the next shape.
        if not self.current_shape.move(0, 1):
            if self.gameOverCheck():
                self.paused = True
                self.gameOverAnimation()
            else:
                self.nextShapes()

    # First clears the info frame and then draws a tetromino to the board by calling the Tetrominoes class and passing
    # it the game and info frame as well as the current shape and the next shape. It then calls the createShGame
    # and createShInfo function from the Tetrominoes class to finally draw the shape to the game and info frame.
    def createTetromino(self):
        self.current_shape.clearInfo()
        self.current_shape = Tetrominoes(self.gameFrame, self.infoFrame, self.currentShape, self.nextShape)
        self.current_shape.createShGame()
        self.current_shape.createShInfo()

    # Determines how many shapes are currently left in the shapesList array, if there is only 1 it sets the current
    # shape to that shape, shuffles the next shapes list and sets the next shape to the first element in the
    # nextShapesList. It then sets the current shapes list to the next shapes list and generates a new nextShapesList.
    # If there are more than 1 shape in the current shape bag it removes the first item from the list and sets the
    # current shape to it as well as setting the next shape to the next shape.
    def shapeBag(self):
        if len(self.shapesList) == 1:
            self.currentShape = self.shapesList[0]
            shuffle(self.nextShapesList)
            self.nextShape = self.nextShapesList[0]
            self.shapesList = self.nextShapesList
            self.nextShapesList = [0, 1, 2, 3, 4, 5, 6]
        else:
            self.currentShape = self.shapesList.pop(0)
            self.nextShape = self.shapesList[0]

    # Handles events.
    def eventHandler(self, event):
        # Moves the current shape left on hitting left if the game isn't paused.
        if event.keysym == "Left" and not self.paused:
            self.current_shape.move(-1, 0)
        # Moves the current shape right on hitting right if the game isn't paused.
        if event.keysym == "Right" and not self.paused:
            self.current_shape.move(1, 0)
        # Moves the current shape down 1 on hitting down if the game isn't paused.
        if event.keysym == "Down" and not self.paused:
            self.current_shape.move(0, 1)
        # Rotates the current shape counter clockwise on hitting up if the game isn't paused.
        if event.keysym == "Up" and not self.paused:
            self.current_shape.rotate(1)
        # Rotates the current shape clockwise on hitting z if the game isn't paused.
        if event.keysym == "z" and not self.paused:
            self.current_shape.rotate(-1)
        # Hard drop on hitting space if the game isn't paused., moves shape down until it cannot move anymore, then
        # cancels any queued tick calls, spawns a shape and re calls ticking.
        if event.keysym == "space" and not self.paused:
            while self.current_shape.move(0, 1):
                self.current_shape.move(0, 1)
            self.parent.after_cancel(self.ticking)
            self.nextShapes()
            self.ticking = self.gameFrame.after(self.tickRate, self.tick)
        # Pauses game on hitting escape.
        if event.keysym == "Escape":
            self.pause()

    # Gets relative location of all blocks on the board and then determines if there are 10 cells connected horizontally
    # currently on the board. It then determines how many lines were cleared and adds that to the totalLines variable
    # as well as the totalLineMulti variable.
    def clearLines(self):
        blockLocation = self.getBlockLocation()
        blockArray = []
        for block in blockLocation:
            blockArray.append(block[2])
        # Uses Counter to keep track of how many occurrences of blocks occur on each row.
        counter = Counter(blockArray)
        # Converts counter from a dictionary to a tuple.
        counterTuple = counter.items()
        linesToMove = []
        # Iterates through the counter tuple getting the columns and rows.
        for col, rows in counterTuple:
            # Checks if there are currently 10 blocks in a row.
            if rows == 10:
                # If there is iterates through the current location of all blocks.
                for block in blockLocation:
                    # Checks if the blocks column is in the location of the column to remove.
                    if block[2] == col:
                        # Adds the column location to the lines to move array and gets the coordinates for it.
                        linesToMove.append(block[2] * self.CELL_SIZE)
                        # Deletes the current block id from the game frame.
                        self.gameFrame.delete(block[0])
                        # Plays a sound when the line is cleared.
                        self.lineClearSound.play()
        linesToMove = list(set(linesToMove))
        storage = self.gameFrame.find_all()
        linesCleared = len(linesToMove)
        for block in storage:
            tempCoords = self.gameFrame.coords(block)
            for counterTuple in linesToMove:
                if tempCoords[3] < counterTuple:
                    self.gameFrame.move(block, 0, 40)
        self.totalLines += linesCleared
        self.totalLineMult += (linesCleared * linesCleared)

    # Returns the relative location and id of the current blocks on the board using tkinter's find all method
    # and coords method.
    def getBlockLocation(self):
        blockLocation = []
        for x in self.gameFrame.find_all():
            coords = self.gameFrame.coords(x)
            # Appends the id and relative location to blockLocation by dividing the x2 and y2 of the cells bounding box
            # by the cell size.
            blockLocation.append([x, int(coords[2] / self.CELL_SIZE), int(coords[3] / self.CELL_SIZE)])
        return blockLocation

    # Uses tkinter's find overlapping method to determine if more than 4 boxes are overlapping at the top of the board
    # if there are it then returns True to start the game over animation.
    def gameOverCheck(self):
        x = self.gameFrame.find_overlapping(160, 0, 240, 80)
        if len(x) > 4:
            return True
        return False

    # Animation that plays upon gameover.
    def gameOverAnimation(self):
        drawDir = "Left"
        counter = 0

        # Cancels any queued tick functions.
        self.parent.after_cancel(self.ticking)
        # Slowly fades out the current audio.
        self.channel.fadeout(5000)

        # Iterates through current board and draws a grey square to the canvas until the entire board is filled.
        for y in range(800, -1, -40):
            if counter >= 10:
                drawDir = "Right"
            elif counter <= 0:
                drawDir = "Left"
            if drawDir == "Left":
                for x in range(400, -1, -40):
                    self.gameFrame.create_rectangle(x - self.CELL_SIZE, y - self.CELL_SIZE, x, y, outline="Black",
                                                    fill="Grey")
                    self.gameFrame.update()
                    self.gameFrame.after(20)
                    counter += 1
            if drawDir == "Right":
                for x in range(0, 401, 40):
                    self.gameFrame.create_rectangle(x + self.CELL_SIZE, y - self.CELL_SIZE, x, y, outline="Black",
                                                    fill="Grey")
                    self.gameFrame.update()
                    self.gameFrame.after(10)
                    counter -= 1
        # Fills the board from left to right with a black screen.
        for x in range(0, 401, 40):
            self.gameFrame.create_rectangle(x + self.CELL_SIZE, 0, x, 800, outline="Black", fill="Black")
            self.gameFrame.update()
            self.gameFrame.after(10)

        # Draws the game over image to the board.
        label = Label(self.gameFrame, image=self.gameOverImage, relief="sunken")
        label.pack()
        self.gameFrame.create_window(201, 400, window=label)
        self.setHighScores()
        self.gameOver = True

    # Reinitialize and clears all important values for a new game.
    def newGame(self):
        self.parent.after_cancel(self.ticking)
        self.gameFrame.delete("all")
        self.shapesList = [0, 1, 2, 3, 4, 5, 6]
        self.nextShapesList = [0, 1, 2, 3, 4, 5, 6]
        shuffle(self.shapesList)
        self.currentShape = self.shapesList.pop(0)
        self.nextShape = self.shapesList[0]
        self.createTetromino()
        self.completeLines = []
        self.totalLines = 0
        self.totalLineMult = 0
        self.tickRate = 1000
        self.currentScore.set(0)
        self.currentLevel.set(1)
        self.gameFrame.update()
        self.infoFrame.update()
        self.ticking = self.gameFrame.after(self.tickRate, self.tick)
        self.channel.play(self.music, loops=-1)
        self.gameOver = False
        self.paused = False

    # Toggles between pausing and resuming the game by canceling or resuming any queued tick function calls.
    def pause(self):
        if not self.paused:
            self.parent.after_cancel(self.ticking)
            self.paused = True
            self.channel.pause()
            pauseLabel = Label(self.infoFrame, text="Paused",
                                      font='Helvetica, 16', fg='black')
            pauseLabel.pack()
            self.infoFrame.create_window(100, 300, window=pauseLabel, tags='pause')
        elif self.paused:
            self.ticking = self.gameFrame.after(self.tickRate, self.tick)
            self.paused = False
            self.infoFrame.delete('pause')
            self.channel.unpause(
            )

    # Calls tkinters message box function after calling the pause function if the game is not over, if the user selects 
    # yes deletes the tkinter frames and exits the game, else it unpauses the game.
    def exitGame(self):
        self.channel.pause()
        if not self.gameOver:
            self.parent.after_cancel(self.ticking)
        if messagebox.askyesno("Quitting Time", "Are you sure you want to quit?"):
            self.gameFrame.delete("all")
            self.infoFrame.delete("all")
            sys.exit()
        else:
            if not self.gameOver:
                self.ticking = self.gameFrame.after(self.tickRate, self.tick)
            self.channel.unpause()

    # Opens the highscores text file as readable, iterates through the file and sets each line to a list named data, then 
    # splits the list into two parts based on two spaces. Afterwards it iterates through the data and sorts it by
    # highest score to lowest score. It then closes the file, reopens it as a writable, deletes the data currently in the file
    # and overwrites it with the current scores.
    def getHighScores(self):
        scoreFile = open('highScores.txt', 'r')
        self.readScore = []
        data = [i.strip() for i in scoreFile]
        sortedData = sorted(data, key=lambda j: int(j.split('  ')[1]), reverse=True)
        for x in data:
            self.scores.append(int(x.split('  ')[1]))
        for z in sortedData:
            self.readScore.append(z)
        scoreFile.close()
        scoreFile = open('highScores.txt', 'w')
        scoreFile.truncate(0)
        scoreFile.write('\n'.join(self.readScore[:10]))
        scoreFile.close()

    # Logic for getting a new high score from the user and appending it to the highscores file. Determines if the current users score
    # is higher than the lowest score in the list, if it is it adds a new text frame and input box prompting the user to input
    # their initials. Else it clears the current file and re inputs the user scores.
    def setHighScores(self):
        scoreFile = open('highScores.txt', 'w')
        userScore = int(self.currentScore.get())
        if userScore > self.scores[-1]:
            nameLabel = Label(self.gameFrame, text="New High Score! Enter your initials.", font=('Helvetica', 16),
                              bg='black', fg='white')
            nameLabel.pack()
            scoreLabel = Label(self.gameFrame, textvariable=self.currentScore, font=('Helvetica', 16),
                               bg='black', fg='white')
            scoreLabel.pack()
            self.gameFrame.create_window(200, 560, window=nameLabel)
            enterName = Entry(self.gameFrame)
            enterName.pack()

            def onButton():
                userName = enterName.get()

                if len(userName) == 3:
                    strScore = str(userScore)
                    nameScore = userName.upper() + "  " + strScore
                    enterName.delete(0, 'end')
                    submitButton.config(state="disabled")
                    enterName.config(state="disabled")
                    self.gameFrame.delete('fail')

                    submittedLabel = Label(self.gameFrame, text="High score submitted!", font=('Helvetica', 16),
                                           bg='black', fg='white')
                    submittedLabel.pack()
                    self.gameFrame.create_window(200, 720, window=submittedLabel)
                    scoreFile.truncate(0)
                    scoreFile.write(nameScore + '\n')
                    scoreFile.write('\n'.join(self.readScore[:9]))
                    scoreFile.close()
                    self.getHighScores()
                    self.showHighScores()
                else:
                    failLabel = Label(self.gameFrame, text="Please enter only 3 letters or numbers.",
                                      font='Helvetica, 16', bg='black', fg='white')
                    failLabel.pack()
                    self.gameFrame.create_window(200, 720, window=failLabel, tags='fail')

            submitButton = Button(self.gameFrame, text="Submit", command=lambda: onButton())
            submitButton.pack()
            self.gameFrame.create_window(200, 680, window=submitButton)
            self.gameFrame.create_window(200, 600, window=scoreLabel)
            self.gameFrame.create_window(200, 640, window=enterName)
        else:
            scoreFile.truncate(0)
            scoreFile.write('\n'.join(self.readScore[:10]))
            scoreFile.close()
            self.getHighScores()
            self.showHighScores()

    # Sets the getScores stringvar to the current highscores.
    def showHighScores(self):
        with open('highScores.txt', 'r') as scoreFile:
            self.getScores.set(scoreFile.read())

    # Checks if the size of the highscores file is 0, if it is populates it with default scores.
    def populateWordFile(self):
        if os.stat("highScores.txt").st_size == 0:
            scoreFile = open('highScores.txt', 'w')
            scoreFile.write('TMY  500000' '\n'
                            'RCK  499999' '\n'
                            'JTH  425700' '\n'
                            'BTH  350000' '\n'
                            'SMR  279999' '\n'
                            'MSK  157095' '\n'
                            'TNA  95123' '\n'
                            'BOB  68238' '\n'
                            'LND  63204' '\n'
                            'FRK  12900')
            scoreFile.close()

master = Tk()
Board(master)
master.mainloop()
