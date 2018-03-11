import random
import sys
import time
sys.path.append("..")  #so other modules can be found in parent dir
from Player import *
from Constants import *
from Construction import CONSTR_STATS
from Ant import UNIT_STATS
from Move import Move
from Construction import Construction
from GameState import *
from AIPlayerUtils import *

##
#
# HW2 - Heuristic Search AI
# Jarrett Oney and Abhinav Mulagada
#
##

##
#AIPlayer
#Description: The responsbility of this class is to interact with the game by
#deciding a valid move based on a given game state. This class has methods that
#will be implemented by students in Dr. Nuxoll's AI course.
#
#This bot employs a Heuristic Search algorithm to select the correct move,
#with the heuristic evaluating the state from a "FoodGatherer" point of view
#
#Variables:
#   playerId - The id of the player.
##
class AIPlayer(Player):

    #Target depth level for the seach
    depth = 2
    totalEval = 0
    
    #__init__
    #Description: Creates a new Player
    #
    #Parameters:
    #   inputPlayerId - The id to give the new player (int)
    ##
    def __init__(self, inputPlayerId):
        super(AIPlayer,self).__init__(inputPlayerId, "SEEEEARCH")
        self.unitTest()
    
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
        self.totalEval = 0;
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
        return self.searchMove(currentState, 0)
    ##
    #evaluate
    #Description: Analyzes the current state with the "FoodGatherer" State of Mind
    #
    #Param:
    #   state - The state to be evaluated
    #
    #Return:
    #   The numeric score of the state (float)
    ##
    def evaluate(self, state):
        #initialize stuff
        score = 0.0
        myInv = None
        theirInv = None
        me = state.whoseTurn
        bases = getConstrList(state, me, (TUNNEL, ANTHILL,))
        foods = []
        for food in getConstrList(state, None, (FOOD,)):
            if food.coords[1] < 5:
                foods.append(food)
                
        for inv in state.inventories:
            if inv.player == me:
                myInv = inv
            else:
                theirInv = inv

        #Get how much food we have
        score += myInv.foodCount *2

        #Detract how much food they have
        score -= theirInv.foodCount * 2

        #Add half for each carried food and dist from respective target
        workers = getAntList(state, me, (WORKER,))
        
        for worker in workers:
            dist = 999
            if worker.coords[1] >= 4:
                score -= 2
            if worker.carrying:
                score += 1
                for cache in bases:
                    temp = approxDist(worker.coords, cache.coords)
                    if temp < dist:
                        dist = temp
                score += (-.0333)*dist + 1
            else:
                for food in foods:
                    temp = approxDist(worker.coords, food.coords)
                    if temp < dist:
                        dist = temp
                score += (-.0333)*dist + .5
                

        #Dead worker, we need a new one
        if(len(workers) == 0):
            score -= 5

        #Detract half for their carried food
        enemyWorkers = getAntList(state, (me + 1) % 2, (WORKER,))
        for worker in enemyWorkers:
            if worker.carrying:
                score -= 1

        #Detract based on our ant count with theirs
        enemyAnts = getAntList(state, (me+1)%2)
        score -= len(enemyAnts)*2

        #Calc dist score for queen   
        dist = 999
        for ant in enemyAnts:
            temp = approxDist(ant.coords, getCurrPlayerQueen(state).coords)
            if temp < dist:
                dist = temp
        score +=  20 - dist

        #Detract score if queen is standing on a food
        for food in foods:
            if getCurrPlayerQueen(state).coords == food.coords:
                score -= 5
                break
            
        #self.totalEval += 1
        return score

    ##
    #bestScore
    #Description: Determines the average score of the list, gives the best move if depth = 0
    #
    #Parameters:
    #   listOfNodes -   The nodes correlating to a given states possible moves
    #   depthLevel -    The current depth level of the search
    #
    #Return: The Move to be made if depthLevel is 0, the best score in the list otherwise
    ##
    def bestScore(self, listOfNodes, depthLevel):
        score = None
        
        #If depthLevel is 0, then we need to return the best move
        if depthLevel == 0:
            #if multiple "equal" moves, pick one at random
            bestList = []
            for node in listOfNodes:
                if score == None:
                    score = node["Score"]
                    bestList.append(node)
                elif node["Score"] > score:
                    score = node["Score"]
                    del bestList[:]
                    bestList.append(node)
                elif node["Score"] == score:
                    bestList.append(node)
            #print self.totalEval
            return random.choice(bestList)["Move"]

        #If depth level is over 0, then return the average value of the set
        else:
            total = 0
            for node in listOfNodes:
                total += node["Score"]

            return total/len(listOfNodes)


    ##
    #searchMove
    #Description:   Recursively searches for the best move by analyzing the gameStates
    #               that result from a given move
    #
    #Parameters:
    #   currentState -  The state of the game (GameState)
    #   depthLevel -    The current depth of the search
    #
    #Return:
    #   The Move to be made
    #   The "score" of a subtree
    ##
    def searchMove(self, currentState, depthLevel, parentNode = None):
        moves = listAllLegalMoves(currentState)
        initScore = self.evaluate(currentState)
        nodes = []

        for move in moves:
            #No ant is allowed to move into no mans land; considered bad strat
            if move.moveType == MOVE_ANT and move.coordList[len(move.coordList) - 1][1] >= 4:
                continue
            #As we are implementing a "FoodGatherer" heuristic, we will not build offense ants
            elif move.moveType == BUILD and move.buildType == SOLDIER:
                continue
            elif move.moveType == BUILD and move.buildType == R_SOLDIER:
                continue
            elif move.moveType == BUILD and move.buildType == DRONE:
                continue
            #If we just moved an ant, we will not want to move them again
            elif parentNode != None and parentNode["Move"].moveType == MOVE_ANT and move.moveType == MOVE_ANT and \
                    move.coordList[0] == parentNode["Move"].coordList[len(parentNode["Move"].coordList)-1]:
                continue
            #Don't get next state for end moves
            elif move.moveType == END:
                nodes.append({"Move" : move, "State" : currentState, "Score" : initScore})
                
            #Moves are good to look at and evaluate
            else:
                
                newState = getNextState(currentState, move)
                newScore = self.evaluate(newState)
                #in a "FoodGatherer" heuristic, there will not be a suboptmal move that has greater success later
                #As such, prune away and ignore any node that brings us to a less optimal state
                if newScore >= initScore:
                    nodes.append({"Move" : move, "State" : newState, "Score" : newScore})


        #Expand the existing nodes
        if depthLevel < self.depth:
            for node in nodes:
                if node["Move"].moveType != END: #This isn't minimax, don't expand END nodes
                    node["Score"] = self.searchMove(node["State"], depthLevel + 1, node)

        #Will return a value if depth over 1, move if depth = 0
        return self.bestScore(nodes, depthLevel)
        
    
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
        return enemyLocations[0]

    ##
    #unitTest
    #
    #Description:
    #   This method is called on init in order to test the functionality of the methods written
    ##
    def unitTest(self):
        print "Commencing Testing"
        
        #Testing bestScore
        nodes = []
        nodes.append({"Move" : Move(END, None, None), "Score" : 15})
        nodes.append({"Move" : Move(MOVE_ANT, [[0,2],[0,3]], None), "Score" : 11})
        nodes.append({"Move" : Move(BUILD, None, WORKER), "Score" : 4})

        if self.bestScore(nodes, 1) != 10: #Should return the average value of the list since depth > 0
            print "INCORRECT AVERAGING OF CHILD NODES IN bestScore METHOD"
    
        if not isinstance(self.bestScore(nodes, 0), Move): #Should return the highest value move
            print "bestScore METHOD DOES NOT RETURN MOVE TYPE IF DEPTH IS 0"
        elif self.bestScore(nodes, 0).moveType != END:
            print "bestScore METHOD DOES NOT RETURN CORRECT MOVE TYPE WHEN DEPTH IS 0"

        #Testing evaluate
        p1inv = Inventory(PLAYER_ONE, [], [], 5)
        p2inv = Inventory(PLAYER_TWO, [], [], 3)
        neutInv = Inventory(NEUTRAL, [], [], 0)

        neutInv.constrs.append(Building([3,0], FOOD, NEUTRAL))
        neutInv.constrs.append(Building([9,2], FOOD, NEUTRAL))
        neutInv.constrs.append(Building([0,9], FOOD, NEUTRAL))
        neutInv.constrs.append(Building([7,8], FOOD, NEUTRAL))

        p1inv.constrs.append(Building([2,0], TUNNEL, PLAYER_ONE))
        p1inv.constrs.append(Building([7, 1], ANTHILL, PLAYER_ONE))
        p1inv.ants.append(Ant([7,0], WORKER, PLAYER_ONE))
        p1inv.ants.append(Ant([2,2], WORKER, PLAYER_ONE))
        p1inv.ants.append(Ant([8,1], QUEEN, PLAYER_ONE))

        p2inv.constrs.append(Building([7,1], ANTHILL, PLAYER_TWO))
        p2inv.constrs.append(Building([8,4], TUNNEL, PLAYER_TWO))
        p2inv.ants.append(Ant([6,2], QUEEN, PLAYER_TWO))
        carryingAnt = Ant([8,5], WORKER, PLAYER_TWO)
        carryingAnt.carrying = True
        p2inv.ants.append(carryingAnt)

        testState = GameState(None, [p1inv, p2inv, neutInv], PLAY_PHASE, PLAYER_TWO)

        #Calculated by hand evaluation
        if self.evaluate(testState) != 16.9667:
            print "METHOD evaluate DOES NOT WORK PROPERLY"

        #Testing searchMove
        firstMove = self.getMove(testState)
        
        #Queen moves to be adjacent to the workerant on its side, kills it
        if firstMove.moveType != MOVE_ANT and firstMove.coordList != [[6,2],[7,2],[7,1]]:
            print "METHOD searchMove NOT WORKING CORRECTLY"
            
        print "Done Testing"

        
