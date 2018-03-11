  # -*- coding: latin-1 -*-
import random
from random import shuffle
import sys
sys.path.append("..")  #so other modules can be found in parent dir
from Player import *
from Constants import *
from Construction import CONSTR_STATS
from Ant import UNIT_STATS
from Move import Move
from GameState import addCoords
from AIPlayerUtils import *


##
#
# HW4 - Genetic Algorithms
# Abhinav Mulagada and Reece Teramoto
#
##

##
#Gene
#Description: Defines a gene
#
#Variables:
#   newAnthill, newTunnel - tuples of the anthill and tunnel
#   newGrass - a list of tuples where the grass will be placed
#   newFood - a list of tuples of the two enemy food locations
#   newFitness - the fitness of the gene
##
class Gene():

    def __init__(self, newAnthill, newTunnel, newGrass, newFood, newFitness = 0):
        self.anthill = newAnthill
        self.tunnel = newTunnel
        self.grass = newGrass
        self.food = newFood
        self.fitness = newFitness

        self.state = None

        # the number of games the gene has played
        self.numGames = 0


##
#getRandPointOnMySide()
#Description: returns an x-y tuple of a point on my side of the board
# (x is between 0 and 9, y is between 0 and 3, inclusive)
#
# Param:
#   x1, x2 - the range of random x coordinates
#   y1, y2 - the range of random y coordinates
#
# Return: (x,y), the random point
def getRandPoint(x1, x2, y1, y2):
    # shuffle the list, replace the first element with an element
    # on my side of the board
    # random.shuffle(anthillTunnelPool)

    newLocationX = random.randint(x1,x2)
    newLocationY = random.randint(y1,y2)
    return (newLocationX, newLocationY)

##
#AIPlayer
#Description: The responsbility of this class is to interact with the game by
#deciding a valid move based on a given game state. This class has methods that
#will be implemented by students in Dr. Nuxoll's AI course.
#
#Variables:
#   playerId - The id of the player.
##
class AIPlayer(Player):

    #__init__
    #Description: Creates a new Player
    #
    #Parameters:
    #   inputPlayerId - The id to give the new player (int)
    ##
    def __init__(self, inputPlayerId):
        super(AIPlayer,self).__init__(inputPlayerId, "Teramoto17_Mulagada18 AI")

        # A list of lists to store the current population of genes
        self.genePopulation = []

        # An index to track which gene in the population is next to be evaluated
        self.nextGeneIdx = 0

        # the number of genes in a population
        self.populationSize = 20

        # A second list to store the fitness of each gene in the current population
        # self.geneFitnesses = []

        # the number of games each gene will play for its fitness to be fully evaluated
        self.gamesPerGene = 20

        self.initGenes()



    ##
    #getPlacement
    #
    #Description: The getPlacement method corresponds to the
    #action taken on setup phase 1 and setup phase 2 of the game.
    #In setup phase 1, the AI player will be passed a copy of the
    #state as currentState which contains the board, accessed via
    #currentState.board. The player will then return a list of 11 tuple
    #coordinates (from their side of the board) that represent Locations
    #to place the anthill and 9 grass pieces. In setup phase 2, the player
    #will again be passed the state and needs to return a list of 2 tuple
    #coordinates (on their opponent's side of the board) which represent
    #Locations to place the food sources. This is all that is necessary to
    #complete the setup phases.
    #
    #Parameters:
    #   currentState - The current state of the game at the time the Game is
    #       requesting a placement from the player.(GameState)
    #
    #Return: If setup phase 1: list of eleven 2-tuples of ints -> [(x1,y1), (x2,y2),�,(x10,y10)]
    #       If setup phase 2: list of two 2-tuples of ints -> [(x1,y1), (x2,y2)]
    ##
    def getPlacement(self, currentState):

        # should contain the code that uses the current to-be-evaluated gene to
        # define the layout it returns to the game

        # nextGeneIdx will track which gene in the population is next to be evaluated
        # print "population size: " + str(len(self.genePopulation))
        # print "nextGeneIdx: " + str(self.nextGeneIdx)
        currentGene = self.genePopulation[self.nextGeneIdx]

        # if setup phase 1, list of eleven 2-tuples of ints (anthill, tunnel, all grass)
        if currentState.phase == SETUP_PHASE_1:
            rtn = []

            # get anthill coord
            rtn.append(currentGene.anthill)

            # get tunnel coord
            rtn.append(currentGene.tunnel)

            # get all grass coords
            for grassCoord in currentGene.grass:
                rtn.append(grassCoord)

            return rtn

        # if setup phase 2, list of two 2-tuples of ints (for food)
        if currentState.phase == SETUP_PHASE_2:
            # get both foods

            # print "PRINTING FOOD COORDS"
            # print str(currentGene.food[0])
            # print str(currentGene.food[1])

            # save the state to the current gene
            stateCopy = currentState.clone()


            # add in the food we are about to return
            stateCopy.inventories[2].constrs.append(Construction(currentGene.food[0], FOOD))
            stateCopy.inventories[2].constrs.append(Construction(currentGene.food[1], FOOD))

            self.genePopulation[self.nextGeneIdx].state = stateCopy.clone()

            return currentGene.food

        return None

    ##
    #getMove
    #Description: The getMove method corresponds to the play phase of the game
    #and requests from the player a Move object. All types are symbolic
    #constants which can be referred to in Constants.py. The move object has a
    #field for type (moveType) as well as field for relevant coordinate
    #information (coordList). If for instance the player wishes to move an ant,
    #they simply return a Move object where the type field is the MOVE_ANT constant
    #and the coordList contains a listing of valid locations starting with an Ant
    #and containing only unoccupied spaces thereafter. A build is similar to a move
    #except the type is set as BUILD, a buildType is given, and a single coordinate
    #is in the list representing the build location. For an end turn, no coordinates
    #are necessary, just set the type as END and return.
    #
    #Parameters:
    #   currentState - The current state of the game at the time the Game is
    #       requesting a move from the player.(GameState)
    #
    #Return: Move(moveType [int], coordList [list of 2-tuples of ints], buildType [int]
    ##
    def getMove(self, currentState):

        # do a random move
        try:
            moves = listAllLegalMoves(currentState)
        except:
            return Move(END, None, None)
        selectedMove = moves[random.randint(0,len(moves) - 1)];

        #don't do a build move if there are already 3+ ants
        numAnts = len(currentState.inventories[currentState.whoseTurn].ants)
        while (selectedMove.moveType == BUILD and numAnts >= 3):
            selectedMove = moves[random.randint(0,len(moves) - 1)];

        return selectedMove

    ##
    #getAttack
    #Description: The getAttack method is called on the player whenever an ant completes
    #a move and has a valid attack. It is assumed that an attack will always be made
    #because there is no strategic advantage from withholding an attack. The AIPlayer
    #is passed a copy of the state which again contains the board and also a clone of
    #the attacking ant. The player is also passed a list of coordinate tuples which
    #represent valid locations for attack. Hint: a random AI can simply return one of
    #these coordinates for a valid attack.
    #
    #Parameters:
    #   currentState - The current state of the game at the time the Game is requesting
    #       a move from the player. (GameState)
    #   attackingAnt - A clone of the ant currently making the attack. (Ant)
    #   enemyLocation - A list of coordinate locations for valid attacks (i.e.
    #       enemies within range) ([list of 2-tuples of ints])
    #
    #Return: A coordinate that matches one of the entries of enemyLocations. ((int,int))
    ##
    def getAttack(self, currentState, attackingAnt, enemyLocations):
        #Attack a random enemy.
        return enemyLocations[random.randint(0, len(enemyLocations) - 1)]

    ##
    #registerWin
    #Description: The last method, registerWin, is called when the game ends and simply
    #indicates to the AI whether it has won or lost the game. This is to help with
    #learning algorithms to develop more successful strategies.
    #
    #Parameters:
    #   hasWon - True if the player has won the game, False if the player lost. (Boolean)
    #
    def registerWin(self, hasWon):
        # using registerWin to manage the population

        # Each time a game ends, the following actions should be performed:
        #   - Update the fitness score of the current gene depending on whether the agent won or lost
        #   - Judge whether the current gene's fitness has been fully evaluated.
        #       - If so, advance to the next gene.
        #   - If all the genes have been fully evaluated, create a new population using the fittest
        #       ones and reset the current index to the beginning.

        # I'm assuming python is assigning this by reference, not making a copy
        currentGene = self.genePopulation[self.nextGeneIdx]

        # Update the fitness score of the current gene depending on whether the
        # agent has won or lost.
        if hasWon:
            currentGene.fitness += 10
        else:
            currentGene.fitness -= 10

        # Judge whether the current gene's fitness has been fully evaluated.
        # A gene's fitness has been fully evaluated if the gene has played (gamesPerGene) games
        currentGene.numGames += 1
        if currentGene.numGames >= self.gamesPerGene:
            # the gene's fitness has been fully evaluated, so go to the next game
            self.nextGeneIdx += 1

            # if all genes have been fully evaluated,
            if self.nextGeneIdx == len(self.genePopulation):

                # print the gene layout of the gene with the highest fitness
                # sort reverse by fitness
                self.genePopulation.sort(key=lambda x:x.fitness, reverse=True)
                # get the gene with the highest fitness
                highestFitnessGene = self.genePopulation[0]

                asciiPrintState(highestFitnessGene.state)

                # create a new population using the fittest ones and reset the
                # current index to the beginning
                self.generateNextGen(self.genePopulation)
                self.nextGeneIdx = 0


    ##
    #initGenes
    #Description: initialize the population of genes with random values and reset the
    # fitness list to default values (set the fitness variable to 0).
    #
    def initGenes(self):


        for count in range(self.populationSize):

            moves = []
            initGrass = []
            initFood = []
            initAnthill = None
            initTunnel = None
            initFitness = 0
            booger = [(9,9), (8,9), \
                    (7,9), (6,9), (9,8), (9,7), \
                    (9,6), (8,8), (8,7), \
                    (7,8), (4,8)]

            for i in range(0,12):
                move = None
                while move == None:
                    xcoord = random.randint(0,9)
                    ycoord = random.randint(0,3)
                    if(xcoord, ycoord) not in moves:
                        if(i == 1):
                            initAnthill = (xcoord, ycoord)
                        elif(i == 2):
                            initTunnel = (xcoord, ycoord)
                        else:
                            initGrass.append((xcoord, ycoord))
                        move = (xcoord, ycoord)
                        # print str(move)
                        moves.append(move)
                        # print "MOVES LIST"
                        # print str(moves)
            for i in range(0,2):
                move = None
                while move == None:
                    xcoord = random.randint(0,9)
                    ycoord = random.randint(6,9)
                    if (xcoord, ycoord) not in booger:
                        initFood.append((xcoord, ycoord))
                        move = (xcoord, ycoord)
                        # print "FOOD COORDS FROM INITGENES FUNCTION"
                        # print str(move1)
                        booger.append(move)
                        # print "BOOGER LIST"
                        # print str(booger)

            newGene = Gene(initAnthill, initTunnel, initGrass, initFood, initFitness)
            self.genePopulation.append(newGene)

    ##
    #mateGenes
    #Description: take two parent genes and generate two child genes that result from
    # the pairing. This mating should include a chance of mutation.
    #
    #Parameters:
    #   gene1 - the first parent gene
    #   gene2 - the second parent gene
    #   desiredChildren - the number of children that will be produced
    def mateGenes(self, gene1, gene2, desiredChildren):

        mutationProbability = 0.01 # 1 in 100

        numChildren = desiredChildren

        # get the unique anthill and tunnel locations of the two parents
        anthillTunnelPool = [gene1.anthill, gene1.tunnel, gene2.anthill, gene2.tunnel]
        anthillTunnelPool = list(set(anthillTunnelPool))

        # get the unique grass of both parents
        grassPool = gene1.grass + gene2.grass
        grassPool = list(set(grassPool))

        # get the unique enemy food of both parents
        enemyFood = gene1.food + gene2.food
        enemyFood = list(set(enemyFood))

        # possible mutation to anthillTunnelPool
        if random.random() < mutationProbability:
            newCoord = getRandPoint(0, 9, 0, 3)
            # make sure new coordinate isn't already in the setup
            if newCoord not in anthillTunnelPool and newCoord not in grassPool:
                anthillTunnelPool[0] = newCoord

        # possible mutation on grass
        if random.random() < mutationProbability:
            newCoord = getRandPoint(0, 9, 0, 3)
            # make sure new coordinate isn't already in the setup
            if newCoord not in anthillTunnelPool and newCoord not in grassPool:
                grassPool[0] = newCoord

        boogerCoords = [(9,9), (8,9), \
                (7,9), (6,9), (9,8), (9,7), \
                (9,6), (8,8), (8,7), \
                (7,8), (4,8)]

        # possible mutation on enemy food
        if random.random() < mutationProbability:
            newCoord = getRandPoint(0, 9, 6, 9)
            # make sure new coordinate isn't already in the setup
            if newCoord not in boogerCoords:
                enemyFood[0] = newCoord


        myChildren = []


        # create each child gene
        for i in range(numChildren):
            # get anthill and tunnel positions for child
            shuffle(anthillTunnelPool)
            newAnthillPos = anthillTunnelPool[0]
            newTunnelPos = anthillTunnelPool[1]

            # get grass positions for child
            shuffle(grassPool)
            newGrass = grassPool[:9]

            # get enemy food positions for child
            shuffle(enemyFood)
            newEnemyFood = enemyFood[:2]

            myChildren.append(Gene(newAnthillPos, newTunnelPos, newGrass, newEnemyFood))


        # return 2 child genes
        return myChildren

    ##
    #generateNextGen
    #Description: Generate the next generation of genes from the old one
    #
    #Parameters:
    #   oldGen - a list of genes representing the old generation
    #
    # Return:
    # a list of genes representing the new generation
    def generateNextGen(self, oldGen):

        # sort old generation in order of highest->lowest fitness
        oldGen.sort(key=lambda x:x.fitness, reverse=True)

        # get the 2 genes with the highest fitness
        parent1 = oldGen[0]
        parent2 = None

        # handle the case where the generation only has one gene (base case testing)
        if len(oldGen) > 1:
            parent2 = oldGen[1]
        else:
            parent2 = oldGen[0]

        # return a list of genes representing the new generation
        newGen = self.mateGenes(parent1, parent2, self.populationSize)
        self.genePopulation = newGen
        return newGen


newPlayer = AIPlayer(0)

# # testing mateGenes() function
# print "\n- - - - - - - - - - - - - - - - - - - -"
# print "\nTesting Gene Mating:\n"
# print "Creating parent1: \n\tnewAnthill = (0,0) \n\tnewTunnel = (0,1) \n\t" + \
#                               "newGrass = [(0,2),(0,3),(0,4),(0,5),(0,6),(0,7),(0,8),(0,9),(1,0)] \n\t" + \
#                               "newFood = [(9,9),(9,8)]"
# parent1Anthill = (0,0)
# parent1Tunnel = (0,1)
# parent1Grass = [(0,2),(0,3),(0,4),(0,5),(0,6),(0,7),(0,8),(0,9),(1,0)]
# parent1Food = [(9,9),(9,8)]
# parent1 = Gene(parent1Anthill, parent1Tunnel, parent1Grass, parent1Food)
#
# print "\nCreating parent2: \n\tnewAnthill = (1,1) \n\tnewTunnel = (1,2) \n\t" + \
#                               "newGrass = [(1,3),(1,4),(1,5),(1,6),(1,7),(1,8),(1,9),(2,0),(2,1)] \n\t" + \
#                               "newFood = [(9,7),(9,6)]"
#
# parent2Anthill = (1,1)
# parent2Tunnel = (1,2)
# parent2Grass = [(1,3),(1,4),(1,5),(1,6),(1,7),(1,8),(1,9),(2,0),(2,1)]
# parent2Food = [(9,7),(9,6)]
# parent2 = Gene(parent2Anthill, parent2Tunnel, parent2Grass, parent2Food)
#
# print "\nMating two parents to get two children."
#
# children = newPlayer.mateGenes(parent1, parent2, 2)
#
# print "\nChild 1:"
# print "\tAnthill: " + str(children[0].anthill)
# print "\tTunnel: " + str(children[0].tunnel)
# print "\tGrass: " + str(children[0].grass)
# print "\tFood: " + str(children[0].food)
#
# print "\nChild 2:"
# print "\tAnthill: " + str(children[1].anthill)
# print "\tTunnel: " + str(children[1].tunnel)
# print "\tGrass: " + str(children[1].grass)
# print "\tFood: " + str(children[1].food)
# # end of testing mateGenes() function
#
#
# # testing generateNextGen() function
# print "\n- - - - - - - - - - - - - - - - - - - -"
# print "\nTesting generateNextGen() function"
# print "\nCreating gene1: \n\tnewAnthill = (0,0) \n\tnewTunnel = (0,1) \n\t" + \
#                               "newGrass = [(0,2),(0,3),(0,4),(0,5),(0,6),(0,7),(0,8),(0,9),(1,0)] \n\t" + \
#                               "newFood = [(9,9),(9,8)] \n\t" + \
#                               "newFitness = 70"
# gene1Anthill = (0,0)
# gene1Tunnel = (0,1)
# gene1Grass = [(0,2),(0,3),(0,4),(0,5),(0,6),(0,7),(0,8),(0,9),(1,0)]
# gene1Food = [(9,9),(9,8)]
# gene1Fitness = 70
# gene1 = Gene(gene1Anthill, gene1Tunnel, gene1Grass, gene1Food, gene1Fitness)
#
# print "\nCreating gene2: \n\tnewAnthill = (1,1) \n\tnewTunnel = (1,2) \n\t" + \
#                               "newGrass = [(1,3),(1,4),(1,5),(1,6),(1,7),(1,8),(1,9),(2,0),(2,1)] \n\t" + \
#                               "newFood = [(9,7),(9,6)] \n\t" + \
#                               "newFitness = 50"
#
# gene2Anthill = (1,1)
# gene2Tunnel = (1,2)
# gene2Grass = [(1,3),(1,4),(1,5),(1,6),(1,7),(1,8),(1,9),(2,0),(2,1)]
# gene2Food = [(9,7),(9,6)]
# gene2Fitness = 50
# gene2 = Gene(gene2Anthill, gene2Tunnel, gene2Grass, gene2Food, gene2Fitness)
#
# print "\nCreating gene3: \n\tnewAnthill = (2,2) \n\tnewTunnel = (2,3) \n\t" + \
#                               "newGrass = [(2,4),(2,5),(2,6),(2,7),(2,8),(2,9),(3,1),(3,2),(3,3)] \n\t" + \
#                               "newFood = [(9,5),(9,4)] \n\t" + \
#                               "newFitness = 100"
# gene3Anthill = (2,2)
# gene3Tunnel = (2,3)
# gene3Grass = [(2,4),(2,5),(2,6),(2,7),(2,8),(2,9),(3,1),(3,2),(3,3)]
# gene3Food = [(9,5),(9,4)]
# gene3Fitness = 100
# gene3 = Gene(gene3Anthill, gene3Tunnel, gene3Grass, gene3Food, gene3Fitness)
#
# currentGen = [gene1, gene2, gene3]
#
# print "\nGenerating next generation: \n"
#
# nextGen = newPlayer.generateNextGen(currentGen)
#
# for idx,gene in enumerate(nextGen):
#     print "\nNextGen Gene " + str(idx) + ":"
#     print "\tAnthill: " + str(gene.anthill)
#     print "\tTunnel: " + str(gene.tunnel)
#     print "\tGrass: " + str(gene.grass)
#     print "\tFood: " + str(gene.food)
# # end of testing generateNextGen() function
#
# print "TESTING INITGENES"
# newPlayer.initGenes()
# for i in newPlayer.genePopulation:
#     print "\tAnthill: " + str(i.anthill)
#     print "\tTunnel: " + str(i.tunnel)
#     print "\tGrass: " + str(i.grass)
#     print "\tFood: " + str(i.food)
