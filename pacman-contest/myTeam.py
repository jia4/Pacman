# myTeam.py
# ---------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
#
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from captureAgents import CaptureAgent
import distanceCalculator
import random, time, util, sys
from game import Directions
from game import Actions
import time
import game
from util import nearestPoint

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first='OffensiveReflexAgent', second='DefensiveReflexAgent'):
  """
  This function should return a list of two agents that will form the
  team, initialized using firstIndex and secondIndex as their agent
  index numbers.  isRed is True if the red team is being created, and
  will be False if the blue team is being created.

  As a potentially helpful development aid, this function can take
  additional string-valued keyword arguments ("first" and "second" are
  such arguments in the case of this function), which will come from
  the --redOpts and --blueOpts command-line arguments to capture.py.
  For the nightly contest, however, your team will be created without
  any extra arguments, so you should make sure that the default
  behavior is what you want for the nightly contest.
  """

  # The following line is an example only; feel free to change it.
  return [eval(first)(firstIndex), eval(second)(secondIndex)]

##########
# Agents #
##########

class ReflexCaptureAgent(CaptureAgent):
  """
  A Dummy agent to serve as an example of the necessary agent structure.
  You should look at baselineTeam.py for more details about how to
  create an agent as this is the bare minimum.
  """

  def registerInitialState(self, gameState):
    """
    This method handles the initial setup of the
    agent to populate useful fields (such as what team
    we're on).

    A distanceCalculator instance caches the maze distances
    between each pair of positions, so your agents can use:
    self.distancer.getDistance(p1, p2)

    IMPORTANT: This method may run for at most 15 seconds.
    """

    '''
    Make sure you do not delete the following line. If you would like to
    use Manhattan distances instead of maze distances in order to save
    on initialization time, please take a look at
    CaptureAgent.registerInitialState in captureAgents.py.
    '''
    self.start = gameState.getAgentPosition(self.index)
    CaptureAgent.registerInitialState(self, gameState)
    self.location = None
    capsuleList = self.getCapsules(gameState)
    if capsuleList != []:
        self.check = 2
    else:
        self.check = 1

    '''
    Your initialization code goes here, if you need any.
    '''

  def getSuccessor(self, gameState, action):
    """
    Finds the next successor which is a grid position (location tuple).
    """
    successor = gameState.generateSuccessor(self.index, action)
    pos = successor.getAgentState(self.index).getPosition()
    return pos

  def chooseAction(self, gameState):
    """
    Picks among actions randomly.
    """
    #start_time = time.time()
    actions = gameState.getLegalActions(self.index)

    '''
    You should change this in your own agent.
    '''
    bestAction = self.aStarSearch(gameState)[0]
    for action in actions:
        x1,y1 = bestAction
        x2,y2 = self.getSuccessor(gameState, action)
        if x1 == x2 and y1 == y2:
            #print("--- %s seconds ---" % (time.time() - start_time))
            return action
    #print("--- %s seconds ---" % (time.time() - start_time))
    return Directions.STOP

  def aStarSearch(self,gameState):
    actions = gameState.getLegalActions(self.index)
    astar_priorityqueue = util.PriorityQueue()
    closed_list = []
    closed_list.append(gameState.getAgentState(self.index).getPosition())
    beginnings = Actions.getLegalNeighbors(gameState.getAgentState(self.index).getPosition(), gameState.getWalls())
    for beginning in beginnings:
        if self.isGoalState(beginning,gameState) == False:
            astar_priorityqueue.push([beginning], self.getCostofAction([beginning]) + self.heuristic(beginning,gameState))
            closed_list.append(beginning)
        else:
            return [beginning]
    while astar_priorityqueue.isEmpty() == False:
        source = astar_priorityqueue.pop()
        if self.isGoalState(source[-1], gameState):
            return source
        else:
            successors = Actions.getLegalNeighbors(source[-1], gameState.getWalls())
            for successor in successors:
                if successor not in closed_list:
                    closed_list.append(successor)
                    astar_priorityqueue.push(source + [successor], self.getCostofAction(source + [successor]) + self.heuristic(successor,gameState))
    util.raiseNotDefined()

  def isGoalState(self, position, gameState):
      return True

  def heruistic(self, position, gameState):
      return 0

  def getCostofAction(self, list):
      return len(list)





class OffensiveReflexAgent(ReflexCaptureAgent):
    def isGoalState(self, position, gameState):
        foodList = self.getFood(gameState).asList()
        capsuleList = self.getCapsules(gameState)
        x,y = position
        if self.state(gameState,foodList):
            if (x,y) == self.start:
                return True
            else:
                return False
        else:
            for agent in self.getOpponents(gameState):
                agentPos = gameState.getAgentPosition(agent)
                if agentPos != None and self.getMazeDistance(gameState.getAgentState(self.index).getPosition(), agentPos) < 6:
                    if gameState.getAgentState(agent).isPacman == False and gameState.getAgentState(
                            agent).scaredTimer < 5:
                        if (x,y) in capsuleList or (x,y) == self.start:
                            self.location = agentPos
                            return True
                        else:
                            return False

            if self.getFood(gameState)[x][y] == True or (x,y) in capsuleList:
                return True
            else:
                return False
    def heuristic(self, position, gameState):
        minPacmanDistance = 5
        for agent in self.getOpponents(gameState):
            agentPos = gameState.getAgentPosition(agent)
            if agentPos != None and self.getMazeDistance(gameState.getAgentState(self.index).getPosition(), agentPos) < 6:
                if gameState.getAgentState(agent).isPacman == False and gameState.getAgentState(
                        agent).scaredTimer < 5:
                    PacmanDistance = self.getMazeDistance(position, agentPos)
                    if PacmanDistance < minPacmanDistance:
                        minPacmanDistance = PacmanDistance
        if self.location != None:
            PacmanDistance = self.getMazeDistance(position, self.location)
            if PacmanDistance < minPacmanDistance:
                minPacmanDistance = PacmanDistance
        return (5 - minPacmanDistance)*10

    def state(self, gameState, foodList):
        if gameState.getAgentState(self.index).numCarrying > (
            gameState.getAgentState(self.index).numCarrying + len(foodList) + gameState.getAgentState(
            self.index).numReturned) / 3 or len(foodList) <= 2:
            return True
        return False


class DefensiveReflexAgent(ReflexCaptureAgent):
    def isGoalState(self, position, gameState):
        if self.check == 1:
            capsuleList = self.getCapsulesYouAreDefending(gameState)
            x,y = position
            for agent in self.getOpponents(gameState):
                agentPos = gameState.getAgentPosition(agent)
                if agentPos != None:
                    if gameState.getAgentState(agent).isPacman:
                        self.location = agentPos
                        if gameState.getAgentState(self.index).scaredTimer == 0:
                            if agentPos == position:
                                return True
                            else:
                                return False
                        else:
                            if self.getMazeDistance(gameState.getAgentState(self.index).getPosition(), agentPos) > 3:
                                if agentPos == position:
                                    return True
                                else:
                                    return False
                            else:
                                if position == self.start:
                                    return True
                                else:
                                    return False

            currentFood = self.getFoodYouAreDefending(self.getCurrentObservation())
            width = currentFood.width
            height = currentFood.height
            if self.getPreviousObservation() != None:
                previousFood = self.getFoodYouAreDefending(self.getPreviousObservation())

                for i in range(0, width):
                    for j in range(0, height):
                        if previousFood[i][j] != currentFood[i][j]:
                            self.location = (i,j)

            if self.location != None:
                if gameState.getAgentState(self.index).getPosition() != self.location:
                    if self.location == position:
                        return True
                    else:
                        return False
                else:
                    self.location = None
                    if self.getFoodYouAreDefending(gameState)[x][y] == True:
                        return True
                    else:
                        return False
            else:
                if self.getFoodYouAreDefending(gameState)[x][y] == True:
                    return True
                else:
                    return False
        else:
            foodList = self.getFood(gameState).asList()
            capsuleList = self.getCapsules(gameState)
            x, y = position
            if self.state(gameState, foodList):
                if (x, y) == self.start:
                    return True
                else:
                    return False
            else:
                for agent in self.getOpponents(gameState):
                    agentPos = gameState.getAgentPosition(agent)
                    if agentPos != None and self.getMazeDistance(gameState.getAgentState(self.index).getPosition(),
                                                                 agentPos) < 6:
                        if gameState.getAgentState(agent).isPacman == False and gameState.getAgentState(
                                agent).scaredTimer < 5:
                            if (x, y) in capsuleList or (x, y) == self.start:
                                self.location = agentPos
                                return True
                            else:
                                return False

                if self.getFood(gameState)[x][y] == True or (x, y) in capsuleList:
                    return True
                else:
                    return False





    def heuristic(self, position, gameState):
        if self.check == 1:
            minPacmanDistance = 5
            if gameState.getAgentState(self.index).scaredTimer != 0:
                for agent in self.getOpponents(gameState):
                    agentPos = gameState.getAgentPosition(agent)
                    if agentPos != None and self.getMazeDistance(gameState.getAgentState(self.index).getPosition(), agentPos) < 4:
                        PacmanDistance = self.getMazeDistance(position, agentPos)
                        if PacmanDistance < minPacmanDistance:
                            minPacmanDistance = PacmanDistance
            return (5 - minPacmanDistance)*1000

        else:
            minPacmanDistance = 5
            for agent in self.getOpponents(gameState):
                agentPos = gameState.getAgentPosition(agent)
                if agentPos != None and self.getMazeDistance(gameState.getAgentState(self.index).getPosition(),
                                                             agentPos) < 6:
                    if gameState.getAgentState(agent).isPacman == False and gameState.getAgentState(
                            agent).scaredTimer < 5:
                        PacmanDistance = self.getMazeDistance(position, agentPos)
                        if PacmanDistance < minPacmanDistance:
                            minPacmanDistance = PacmanDistance
            if self.location != None:
                PacmanDistance = self.getMazeDistance(position, self.location)
                if PacmanDistance < minPacmanDistance:
                    minPacmanDistance = PacmanDistance
            return (5 - minPacmanDistance) * 10

    def state(self, gameState, foodList):
        if gameState.getAgentState(self.index).numCarrying > (
            gameState.getAgentState(self.index).numCarrying + len(foodList) + gameState.getAgentState(
            self.index).numReturned) / 3 or len(foodList) <= 2:
            return True
        return False