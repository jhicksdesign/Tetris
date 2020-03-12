'''
Created on Apr 25, 2017

@author: Jordan Hicks and Frank Ortwerth
'''


class Tetrominoes:
    # Setting constants for board and cells.
    CELL_SIZE = 40
    BOARD_WIDTH = 400
    BOARD_LENGTH = 800
    
    # Array of tetrominoes, determines the color, if and how much the tetromino can rotate, the initial rotate direction
    # and the shape of the tetromino.
    SHAPES = [
        ["yellow", "noRot", 1, (0, 0), (1, 0), (0, 1), (1, 1)],  # square
        ["cyan", "halfRot", 1, (0, 0), (1, 0), (2, 0), (3, 0)],  # I shape
        ["orange", "rot", 1, (0, 0), (1, 0), (2, 0), (0, 1)],  # L shape
        ["blue", "rot", 1, (0, 0), (1, 0), (2, 0), (2, 1)],  # Reverse L shape
        ["green", "halfRot", -1, (0, 0), (1, 0), (1, 1), (2, 1)],  # S shape
        ["purple", "rot", 1, (0, 0), (1, 0), (2, 0), (1, 1)],  # T shape
        ["red", "halfRot", -1, (0, 1), (1, 1), (1, 0), (2, 0)]  # Reverse S shape
    ]


    # Initialization for the tetromino class, gets the required data to create the shapes in the game frame
    # as well as the info frame.
    def __init__(self, gameFrame, infoFrame, randomShape, nextShape):
        self.tetrominoes = []
        self.shape = self.SHAPES[randomShape]
        self.nextShape = self.SHAPES[nextShape]
        self.color = self.shape[0]
        self.gameFrame = gameFrame
        self.nextTetrominoes = []
        self.nextColor = self.nextShape[0]
        self.infoFrame = infoFrame

    # This function when called creates a tetromino on the game frame.
    def createShGame(self):
        # Each cell of the tetromino is drawn by iterating through a random shape chosen from the shapes list,
        # it then determines the bounding box by multiplying each item by the cell size and adding it to a location
        # near the center part of the canvas grid to tell create_rectangle the exact coordinates required to draw it.
        for block in self.shape[3:]:
            cell = self.gameFrame.create_rectangle(
                block[0] * self.CELL_SIZE + 160,
                block[1] * self.CELL_SIZE,
                block[0] * self.CELL_SIZE + 200,
                block[1] * self.CELL_SIZE + 40,
                fill=self.color)
            self.tetrominoes.append(cell)

    # This function when called creates a tetromino on the info frame.
    def createShInfo(self):
        # Utilizes the same logic in createShGame to determine where to draw the terominoes for the info box
        for block in self.nextShape[3:]:
            nextCell = self.infoFrame.create_rectangle(
                block[0] * self.CELL_SIZE / 2 + 80,
                block[1] * self.CELL_SIZE / 2,
                block[0] * self.CELL_SIZE / 2 + 100,
                block[1] * self.CELL_SIZE / 2 + 20,
                fill=self.nextColor)
            self.nextTetrominoes.append(nextCell)
            self.infoFrame.move(nextCell, -10, 80)

    # Iterates through the nextTetrominoes list and removes it from the canvas infoframe
    def clearInfo(self):
        for x in self.nextTetrominoes:
            self.infoFrame.delete(x)

    # Tests if the active tetromino can move, if it cannot then it returns false.

    def moveTest(self, cells, x, y):
        # Sets x and y to a value based on the size of the cell.
        x = x * self.CELL_SIZE
        y = y * self.CELL_SIZE

        # Getting the coordinates of the current tetromino.
        coords = self.gameFrame.coords(cells)

        # Checking if the current tetromino will overlap the board.
        if coords[3] + y > self.BOARD_LENGTH:
            return False
        if coords[0] + x < 0:
            return False
        if coords[2] + x > self.BOARD_WIDTH:
            return False
        
        # Checking if the current tetromino will overlap another shape using tkinters find_overlapping function.
        overlap = set(self.gameFrame.find_overlapping(
            (coords[0] + coords[2]) / 2 + x,
            (coords[1] + coords[3]) / 2 + y,
            (coords[0] + coords[2]) / 2 + x,
            (coords[1] + coords[3]) / 2 + y
        ))
        currentBoard = set(self.gameFrame.find_all()) - set(self.tetrominoes)
        if overlap & currentBoard:
            return False
        return True

    def testBounds(self, x, y):
        for cell in self.tetrominoes:
            if not self.moveTest(cell, x, y):
                return False
        return True

    def move(self, x, y):
        if not self.testBounds(x, y):
            return False
        else:
            for cell in self.tetrominoes:
                self.gameFrame.move(cell, x * self.CELL_SIZE, y * self.CELL_SIZE)
            return True

    # Checks to see if the current tetromino would overlap any shapes on the gameboard or the walls upon rotating.
    def rotTest(self):
        rotDir = self.shape[2]
        pivot = self.tetrominoes[1]
        pivotCoords = self.gameFrame.coords(pivot)
        # Coordinates of block used to pivot around.
        pivX = pivotCoords[0]
        pivY = pivotCoords[1]

        # Iterates through the current tetromino to get it's coordinates
        for block in self.tetrominoes:
            cellCoords = self.gameFrame.coords(block)

            # Bounding box coordinates
            x = cellCoords[0]
            x2 = cellCoords[2]
            y = cellCoords[1]
            y2 = cellCoords[3]

            # New location of shape is determined by
            newX = pivX - rotDir * pivY + rotDir * y
            newY = pivY + rotDir * pivX - rotDir * x

            # Adds rotation location to a list
            overlap = set(self.gameFrame.find_overlapping(
                (x + x2) / 2 + newX - x,
                (y + y2) / 2 + newY - y,
                (x + x2) / 2 + newX - x,
                (y + y2) / 2 + newY - y
            ))
            # Sets up a list of all shapes on the board excluding the current active shape.
            currentBoard = set(self.gameFrame.find_all()) - set(self.tetrominoes)
            # Checks if rotating will overlap an existing shape or the board itself, returns false if it would.
            if overlap & currentBoard or not (0 <= newX < self.BOARD_WIDTH and -40 <= newY < self.BOARD_LENGTH):
                return False

        return True

    # Executes the rotation if the rotation test returned true.
    def rotate(self, rotateDir):
        if self.shape[1] == "noRot":
            return
        else:
            pivot = self.tetrominoes[1]
            pivotCoords = self.gameFrame.coords(pivot)
            pivX = pivotCoords[0]
            pivY = pivotCoords[1]
            rotDir = self.shape[2] * rotateDir
            if self.rotTest():
                for block in self.tetrominoes:
                    cellCoords = self.gameFrame.coords(block)
                    x = cellCoords[0]
                    y = cellCoords[1]
                    newX = pivX - rotDir * pivY + rotDir * y
                    newY = pivY + rotDir * pivX - rotDir * x
                    self.gameFrame.move(block, newX - x, newY - y)
                if self.shape[1] == "halfRot":
                    self.shape[2] = self.shape[2] * -1



    def getCurrentShape(self):
        return self.tetrominoes
