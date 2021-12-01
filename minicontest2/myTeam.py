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
import game
from util import nearestPoint
from distanceCalculator import Distancer
#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'OffensiveAgent', second = 'DefensiveAgent'):
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
  return [eval(first)(firstIndex), eval(second)(secondIndex)]

##########
# Agents #
##########

class ReflexCaptureAgent(CaptureAgent):
 
  def registerInitialState(self, gameState):
    self.start = gameState.getAgentPosition(self.index)
    CaptureAgent.registerInitialState(self, gameState)

  def chooseAction(self, gameState):
    actions = gameState.getLegalActions(self.index)
    values = [self.evaluate(gameState, act) for act in actions]
  
    maxValue = max(values)
    bestActions = [act for act, v in zip(actions, values) if v == maxValue]
    foodLeft = len(self.getFood(gameState).asList())

    if foodLeft <= 2:
      bestDistance = 9999
      for action in actions:
        successor = self.getSuccessor(gameState, action)
        pos2 = successor.getAgentPosition(self.index)
        distance = self.getMazeDistance(self.start,pos2)
        if distance < bestDistance:
          bestAction = action
          bestDistance = distance
      return bestAction

    return random.choice(bestActions)

  def getSuccessor(self, gameState, action):
    successor = gameState.generateSuccessor(self.index, action)
    position = successor.getAgentState(self.index).getPosition()
    if position != nearestPoint(position):
      
      return successor.generateSuccessor(self.index, action)
    else:
      return successor

  def evaluate(self, gameState, action):
    features = self.getFeatures(gameState, action)
    weights = self.getWeights(gameState, action)
    return features * weights

  def getFeatures(self, gameState, action):
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    features['successorScore'] = self.getScore(successor)
    return features

  def getWeights(self, gameState, action):
    return {'successorScore': 1.0}

class OffensiveAgent(ReflexCaptureAgent):
  def getFeatures(self, gameState, action):
    distancer = Distancer(gameState.data.layout)
    distancer.getMazeDistances()
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    foodList = self.getFood(successor).asList()
    features['foodLeft'] = len(foodList)
    enemyIndices = self.getOpponents(successor)
    enemyPositions = [successor.getAgentPosition(index) for index in enemyIndices if not successor.getAgentState(index).isPacman] 
    enemyDistances = []
    for enemyposition in enemyPositions:
        enemyDistances.append(distancer.getDistance(successor.getAgentPosition(self.index), enemyposition))
    ghostClose = 10
    if len(enemyDistances) > 0 and min(enemyDistances) < 3 and successor.getAgentState(self.index).isPacman:
        ghostClose = min(enemyDistances)
    features['ghostClose'] = ghostClose

    numOfFoodEaten = gameState.getAgentState(self.index).numCarrying
    targetX = gameState.data.layout.width // 2
    if gameState.isOnRedTeam(self.index):
        targetX = targetX - 1

    targetPositions = [(targetX, y) for y in range(0, gameState.data.layout.height)]
    distancer = Distancer(gameState.data.layout)
    distancer.getMazeDistances()
    targetDistances = []

    for targetPosition in targetPositions:
        try:
            targetDistances.append(distancer.getDistance(targetPosition, successor.getAgentPosition(self.index)))
        except:
            doNothing = 0
    
    minDist = min(targetDistances)
    features['homeUrgent'] = 30
    if numOfFoodEaten > 0:
        features['homeUrgent'] = minDist

    enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
    invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
    features['numInvaders'] = len(invaders)

    targetX = gameState.data.layout.width // 2
    if not gameState.isOnRedTeam(self.index):
        targetX = targetX - 1

    targetPositions = [(targetX, y) for y in range(0, gameState.data.layout.height)]
    distancer = Distancer(gameState.data.layout)
    distancer.getMazeDistances()

    targetsFarEnoughAway = []
    for position in targetPositions:
        try:
            minDistance = min([distancer.getDistance(position, enemy.getPosition()) for enemy in enemies])
            if minDistance > 7:
                targetsFarEnoughAway.append(position)
        except:
            doNothing = 0

    myPosition = successor.getAgentState(self.index).getPosition()
    distanceToClosestGhost = min([distancer.getDistance(myPosition, enemy.getPosition()) for enemy in enemies])
    distanceToTPs = [distancer.getDistance(myPosition, position) for position in targetsFarEnoughAway]

    if(gameState.getAgentState(self.index).isPacman):
        features['distanceToTargetCrossings'] = 0
        features['ghostClose'] = 0 if distanceToClosestGhost > 4 else distanceToClosestGhost
    else:
        features['ghostClose'] = 0
        features['distanceToTargetCrossings'] = min(distanceToTPs) if len(distanceToTPs) > 0 else 0

    if len(foodList) > 0: 
      myPos = successor.getAgentState(self.index).getPosition()
      minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
      features['distanceToFood'] = minDistance
    return features

  def getWeights(self, gameState, action):
    return {'foodLeft': -100, 'distanceToFood': -1, 'ghostClose': 100, 'homeUrgent': -100, 'distanceToTargetCrossings': -100, "numInvaders": -20}

class DefensiveAgent(ReflexCaptureAgent):

  attack = False
  def getFeatures(self, gameState, action):
    if self.attack:
        return self.getAttackFeatures(gameState, action, defIndex)
    else:
        return self.getDefenseFeatures(gameState, action)


  def getDefenseFeatures(self, gameState, action):
    distancer = Distancer(gameState.data.layout)
    distancer.getMazeDistances()
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    myState = successor.getAgentState(self.index)
    myPosition = myState.getPosition()
    features['onDefense'] = 1
    if myState.isPacman: features['onDefense'] = 0

    enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
    invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
    features['numInvaders'] = len(invaders)
    if len(invaders) > 0:
        dists = [self.getMazeDistance( myPosition, a.getPosition()) for a in invaders]
        features['invaderDistance'] = min(dists)
    if len(invaders) == 0:
        midl = (gameState.data.layout.width/2, gameState.data.layout.height/2)
        middist = self.getMazeDistance( myPosition, midl)
        features['waitmiddle'] = middist
    if action == Directions.STOP: features['stop'] = 1
    rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
    if action == rev: features['reverse'] = 1

    return features

  def getAttackFeatures(self, gameState, action):
    defIndex = 1
    distancer = Distancer(gameState.data.layout)
    distancer.getMazeDistances()
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    myState = successor.getAgentState(self.index)
    # myPos = myState.getPosition()
    
    features['onDefense'] = 1
    if myState.isPacman: features['onDefense'] = 0
    enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
    invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
    features['numInvaders'] = len(invaders)
    # dist = enemies[defIndex]

    return features

  def getWeights(self, gameState, action):
    if self.attack:
        return self.getAttackWeights(gameState, action)
    else:
        return self.getDefenseWeights(gameState, action)

  def getAttackWeights(self, gameState, action):
      return {'numInvaders': -1000, 'onDefense': 100, 'invaderDistance': -10 }

  def getDefenseWeights(self, gameState, action):
      return {'numInvaders': -1000, 'onDefense': 100, 'invaderDistance': -10, 'stop': -100, 'reverse': -2, 'waitmiddle': -100}



