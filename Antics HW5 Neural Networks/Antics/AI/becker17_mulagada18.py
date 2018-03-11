import random
import sys
sys.path.append("..")  #so other modules can be found in parent dir
from Player import *
from Constants import *
from Construction import CONSTR_STATS
from Ant import UNIT_STATS
from Move import Move
from GameState import *
from AIPlayerUtils import *
from Ant import *
import numpy as np
from array import array

##
#
# HW3 - MiniMax
# Abhinav Mulagada and Garrett Becker
#
##

##
#AIPlayer
#Description: The responsbility of this class is to interact with the game by
#deciding a valid move based on a given game state. This class has methods that
#will be implemented by students in Dr. Nuxoll's AI course.
#
#Variables:
#   playerId - The id of the player.
##
neural_array = array('f')
NEURAL_LAYERS = 2
NEURAL_INPUTS = 4



class Node(object):
    def __init__(self,yourMove=None, stateReached=None, evalState=None, depth=None):
        self.yourMove = yourMove
        self.stateReached = stateReached
        self.evalState = evalState
        self.depth = depth
        
class AIPlayer(Player):

    #__init__
    #Description: Creates a new Player
    #
    #Parameters:
    #   inputPlayerId - The id to give the new player (int)
    ##
    def __init__(self, inputPlayerId):
        super(AIPlayer,self).__init__(inputPlayerId, "NEURAL_G")
        self.myFood = None
        self.myTunnel = None
        self.n_weights = NEURAL_INPUTS*NEURAL_LAYERS

        self.set_weights(self.generate_weights(-.1,.1))
    ##
    #getPlacement
    #
    #Description: called during setup phase for each Construction that
    #   must be placed by the player.  These items are: 1 Anthill on
    #   the player's side; 1 tunnel on player's side; 9 grass on the
    #   player's side; and 2 food on the enemy's side.
    #
    #Parameters:
    #   construction - the Construction to be placed.
    #   currentState - the state of the game at this point in time.
    #
    #Return: The coordinates of where the construction is to be placed
    ##
    def getPlacement(self, currentState):
        numToPlace = 0
        #implemented by students to return their next move
        if currentState.phase == SETUP_PHASE_1:    #stuff on my side
            numToPlace = 11
            moves = []
            for i in range(0, numToPlace):
                move = None
                while move == None:
                    #Choose any x location
                    x = random.randint(0, 9)
                    #Choose any y location on your side of the board
                    y = random.randint(0, 3)
                    #Set the move if this space is empty
                    if currentState.board[x][y].constr == None and (x, y) not in moves:
                        move = (x, y)
                        #Just need to make the space non-empty. So I threw whatever I felt like in there.
                        currentState.board[x][y].constr == True
                moves.append(move)
            return moves
        elif currentState.phase == SETUP_PHASE_2:   #stuff on foe's side
            numToPlace = 2
            moves = []
            for i in range(0, numToPlace):
                move = None
                while move == None:
                    #Choose any x location
                    x = random.randint(0, 9)
                    #Choose any y location on enemy side of the board
                    y = random.randint(6, 9)
                    #Set the move if this space is empty
                    if currentState.board[x][y].constr == None and (x, y) not in moves:
                        move = (x, y)
                        #Just need to make the space non-empty. So I threw whatever I felt like in there.
                        currentState.board[x][y].constr == True
                moves.append(move)
            return moves
        else:
            return [(0, 0)]
    
    ##
    #getMove
    #Description: Gets the next move from the Player.
    #
    #Parameters:
    #   currentState - The state of the current game waiting for the player's move (GameState)
    #
    #Return: The Move to be made
    ##
    def getMove(self, currentState):
       
        selectedMove = self.det_move(currentState,0)
     
        return selectedMove
    
    ##
    #getAttack
    #Description: Gets the attack to be made from the Player
    #
    #Parameters:
    #   currentState - A clone of the current state (GameState)
    #   attackingAnt - The ant currently making the attack (Ant)
    #   enemyLocation - The Locations of the Enemies that can be attacked (Location[])
    ##
    def getAttack(self, currentState, attackingAnt, enemyLocations):
        #Attack a random enemy.
        return enemyLocations[random.randint(0, len(enemyLocations) - 1)]

    ##
    #examine_state
    #Description: examine a state and assign a score to it
    #
    #Parameters:
    #   currentState - A clone of the current state (GameState)
    ##
    def examine_state(self, currentState):
        opponentID = (currentState.whoseTurn + 1) % 2
        me = currentState.whoseTurn
        myInv = getCurrPlayerInventory(currentState)
        enemy_inv = [inv for inv in currentState.inventories if inv.player == opponentID].pop()

        currentStatus = 0 ##game is equal at the start
        #Assign player IDs to dummy variables

        myWorkers = getAntList(currentState, me, (WORKER,))
        theirWorkers = getAntList(currentState, opponentID, (WORKER,))

        if self.myFood == None:
           foods = getConstrList(currentState, None, (FOOD,))
           self.myFood = foods[0]
        if (self.myTunnel == None):
            self.myTunnel = getConstrList(currentState, me, (TUNNEL,))[0]

         ##Check to see if someone's won
        if(myInv.foodCount == 12 or len(theirWorkers) == 0):
            return 1.0
        elif (enemy_inv.foodCount == 12 or len(myWorkers) == 0):
            return 0.0

        #compare food supply
        if(myInv.foodCount <= enemy_inv.foodCount):
            currentStatus = currentStatus -.1
        else:
            currentStatus = currentStatus +.1
        
        for i in myWorkers:
            if i.carrying == False and approxDist(i.coords, self.myFood.coords) > 1:
                currentStatus = currentStatus -.2

        for i in myWorkers:
            if i.carrying == True and approxDist(i.coords, self.myTunnel.coords) > 1:
                currentStatus = currentStatus -.4

        if currentStatus < 0:
            currentStatus = 0
        if currentStatus > 1:
            currentStatus = 1
                  
        return currentStatus
     ##
    #eval_nodes
    #Description: evaluates a list of nodes and returns the one with the greatest score
    #
    #Parameters:
    # myNodes[] which is a list of nodes
    ##
    def eval_nodes(self, myNodes = [], *args):
        #Find the node with the greatest value
        #i.e. gives us the best score for the move

        ##list of the scores
        maxScore = max(myNodes, key=lambda item: item.evalState)
        
        return maxScore.yourMove
            
            
     ##
    #det_move
    #Description: returns the best move for the agent
    #
    #Parameters:
    #   currentState - A clone of the current state (GameState)
    #   depth - how far we want to look ahead in our move process

    def det_move(self, currentState, depth):
        self.depth = depth
        depthLimit = 1
        ##Generate list of all legal moves
        legalMoves = listAllLegalMoves(currentState)
        
        gamestateObjs = []

        nodeList = []

        if len(legalMoves) < 3:
            return Move(END, None, None);

        #generate a list of GameState objects
        #that result from each move
        for i in legalMoves:
            if i.moveType == END:
                continue
            moveResults = getNextState(currentState, i)

            #Gamestate objs that are generated from each move
            gamestateObjs.append(moveResults)
            #Save the score that we would receive for making that move
            moveScore = self.examine_state(moveResults)

            rand = random.uniform(.01, .05)
            moveScore = moveScore + rand

            #### store the move results in our neural net array
            self.neural_storage(moveResults)
            ############################################

            newNode = Node(i, currentState,moveScore, depth)
            nodeList.append(newNode)


        #prune nodes that we don't want for better time complexity
        nodeList.sort()
        if len(nodeList) > 10:
            del nodeList[0:10]
        elif len(nodeList) > 20:
            del nodeList[0:20]
        elif len(nodeList) > 40:
            del nodeList[0:40]
        elif len(nodeList) > 80:
            del nodeList[0:80]
        
        #recursively call det_move() in order to create
        #more nodes to add to the nodeList[]
        

        if depth != depthLimit:
            depth = depth + 1
            for x in gamestateObjs:
                self.det_move(x, depth)
        

        #evaluate our list of nodes
        #and return the one with the best score
        theMove = self.eval_nodes(nodeList)
        return theMove


    def generate_weights(self, low = -.1, high = .1):
        #Generate new random weights 
        return np.random.uniform(low, high, size =(self.n_weights))

    def set_weights(self, weight_list):
        weights = []
        for i in range(self.n_weights):
            weights.append(weight_list[i])

    def neural_storage(self, currentState):
        ##Current inputs for our neural net
        input1, input2, input3, input4 = 0, 0, 0, 0 
        
        
        opponentID = (currentState.whoseTurn + 1) % 2
        me = currentState.whoseTurn
        myInv = getCurrPlayerInventory(currentState)
        enemy_inv = [inv for inv in currentState.inventories if inv.player == opponentID].pop()

        currentStatus = 0 ##score per state starts at 0
        #Assign player IDs to dummy variables

        myWorkers = getAntList(currentState, me, (WORKER,))
        theirWorkers = getAntList(currentState, opponentID, (WORKER,))
        numAnts = len(myInv.ants)
        myQueen = myInv.getQueen()


        if self.myFood == None:
           foods = getConstrList(currentState, None, (FOOD,))
           self.myFood = foods[0]
        if (self.myTunnel == None):
            self.myTunnel = getConstrList(currentState, me, (TUNNEL,))[0]

         ##Check to see if someone's won
        if(myInv.foodCount == 12 or len(theirWorkers) == 0):
            return 1.0
        elif (enemy_inv.foodCount == 12 or len(myWorkers) == 0):
            return 0.0

        #compare food supply
        if(myInv.foodCount <= enemy_inv.foodCount):
            currentStatus = currentStatus -.1
            input1 = 0
        else:
            currentStatus = currentStatus +.1 
            input1 = 1
        
        for i in myWorkers:
            if i.carrying == False and approxDist(i.coords, self.myFood.coords) > 1:
                currentStatus = currentStatus -.2
                input2 = 0

        for i in myWorkers:
            if i.carrying == True and approxDist(i.coords, self.myTunnel.coords) > 1:
                currentStatus = currentStatus +.2
                input2 = 1

        if (numAnts == 1):
            input3 = 0
        else:
            input3 = 1

        if(myQueen.coords == myInv.getAnthill().coords):
            input4 = 1
        else:
            input4 = 0

        if currentStatus < 0:
            currentStatus = 0
        if currentStatus > 1:
            currentStatus = 1
        #convert the value to be between 0..1

        #Store the value in an array so it can be processed by the nueral net
        neural_array.append(currentStatus)
