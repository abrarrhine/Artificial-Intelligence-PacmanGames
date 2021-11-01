# myAgents.py
# ---------------
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

from game import Agent, Directions
from searchProblems import PositionSearchProblem

import util
import time
import search

"""
IMPORTANT
`agent` defines which agent you will use. By default, it is set to ClosestDotAgent,
but when you're ready to test your own agent, replace it with MyAgent
"""
def createAgents(num_pacmen, agent='MyAgent'):
    return [eval(agent)(index=i) for i in range(num_pacmen)]

class MyAgent(Agent):
    """
    Implementation of your agent.
    """

    def getAction(self, state):
        """
        Returns the next action the agent will take
        """

        "*** YOUR CODE HERE ***"

        global pocetak
        global kraj
        global ukupnoHrana

        if not pocetak:
            ukupnoHrana = state.getNumFood()
            #print(ukupnoHrana)
            pocetak = True

        if len(self.akcije) > 0:
            sledecaAkcija = self.akcije[0]
            del self.akcije[0]
            return sledecaAkcija
        else: # ako se zavrsila pronadjena putanja nadji novu
            if kraj == False:
                problem = AnyFoodSearchProblem(state, self.index)
                self.akcije = search.bfs(problem)
                sledecaAkcija = self.akcije[0]
                del self.akcije[0]
                return sledecaAkcija
            else:
                return Directions.STOP
            
        #raise NotImplementedError()

    def initialize(self):
        """
        Intialize anything you want to here. This function is called
        when the agent is first created. If you don't need to use it, then
        leave it blank
        """

        "*** YOUR CODE HERE"

        self.akcije = []

        global pocetak
        pocetak = False

        global kraj
        kraj = False

        global pojedenaHrana
        pojedenaHrana = []

        #raise NotImplementedError()

"""
Put any other SearchProblems or search methods below. You may also import classes/methods in
search.py and searchProblems.py. (ClosestDotAgent as an example below)
"""
class Node():
    def __init__(self,stanje,prethodno):
        self.pozicija = stanje[0]
        self.akcija = stanje[1]
        if prethodno is not None:
            self.g = 0.579 + prethodno.g
        else:
            self.g = 0
        self.prethodno = prethodno
        
class ClosestDotAgent(Agent):

    def findPathToClosestDot(self, gameState):
        """
        Returns a path (a list of actions) to the closest dot, starting from
        gameState.
        """
        # Here are some useful elements of the startState
        startPosition = gameState.getPacmanPosition(self.index)
        food = gameState.getFood()
        walls = gameState.getWalls()
        problem = AnyFoodSearchProblem(gameState, self.index)
        "*** YOUR CODE HERE ***"
        #print("Start:", problem.getStartState())

        pq = util.PriorityQueue()

        food = food.asList()
        min = 1000
        najbliza = food[0]
        for hrana in food:
            if abs(startPosition[0] - hrana[0]) + abs(startPosition[1] - hrana[1]) < min:
                min = abs(startPosition[0] - hrana[0]) + abs(startPosition[1] - hrana[1])
                najbliza = hrana
        #print(najbliza)



        pq.push(Node(((startPosition,najbliza), "STOP", 0), None), 0)
        visited = set()
        while not (pq.isEmpty()):

            trenutni = pq.pop()
            #print(trenutni.pozicija)
            if trenutni.pozicija in visited:
                continue
            visited.add(trenutni.pozicija)

            if problem.isGoalStateClosestDot(trenutni.pozicija):
                lista = [trenutni.akcija]
                temp = trenutni.prethodno
                while (temp != None):
                    lista.append(temp.akcija)
                    temp = temp.prethodno
                #print("nasaaaaaaaaaaaaaaaaaao")
                #print(lista[::-1][1:])
                return lista[::-1][1:]
            #print(trenutni.pozicija[0])
            for sukcesor in problem.getSuccessors(trenutni.pozicija[0]):
                #print("aaaaaaaaaaaaaa")

                n = Node(((sukcesor[0],najbliza),sukcesor[1],sukcesor[2]), trenutni)
                #print(n.pozicija)
                #print(n.akcija)
                #print(n.g)
                #print(dotsHeuristic(n.pozicija, problem))
                pq.push(n, n.g + dotsHeuristic(n.pozicija, problem))
        #print("prazzananan")
        return []
        util.raiseNotDefined()


        "*** YOUR CODE HERE ***"
        util.raiseNotDefined()

    def getAction(self, state):
        return self.findPathToClosestDot(state)[0]
    
def dotsHeuristic(state, problem):
    """
    Heuristika za CornersProblem koji ste vi definisali iznad.
      state:   Trenutno stanje pretrage
               (struktura podataka koju izaberete u problemu pretrage)
      problem: Instanca CornersProblem-a instance za ovu tablu.
    Ova funkcija treba da uvek vrati cenu najkrace putanje od nekog stanja do cilja:
    treba da bude dopustiva
    """
    #corners = problem.corners # These are the corner coordinates
    walls = problem.walls # These are the walls of the maze, as a Grid (game.py)
    #print("HHHHHHeuristika")
    #TODO 2: Implementirati heuristicku funkciju
    #state je koordinate pacmana
    #print(abs(state[0][0] - state[1][0]) + abs(state[0][1] - state[1][1]))
    return abs(state[0][0] - state[1][0]) + abs(state[0][1] - state[1][1])

class AnyFoodSearchProblem(PositionSearchProblem):
    """
    A search problem for finding a path to any food.
    This search problem is just like the PositionSearchProblem, but has a
    different goal test, which you need to fill in below.  The state space and
    successor function do not need to be changed.
    The class definition above, AnyFoodSearchProblem(PositionSearchProblem),
    inherits the methods of the PositionSearchProblem.
    You can use this search problem to help you fill in the findPathToClosestDot
    method.
    """

    def __init__(self, gameState, agentIndex):
        "Stores information from the gameState.  You don't need to change this."
        # Store the food for later reference
        self.food = gameState.getFood()

        # Store info for the PositionSearchProblem (no need to change this)
        self.walls = gameState.getWalls()
        self.startState = gameState.getPacmanPosition(agentIndex)
        self.costFn = lambda x: 1
        self._visited, self._visitedlist, self._expanded = {}, [], 0 # DO NOT CHANGE
    
    def isGoalStateClosestDot(self, state):
        """
        The state is Pacman's position. Fill this in with a goal test that will
        complete the problem definition.
        """

        return self.food[state[0][0]][state[0][1]]

    def isGoalState(self, state):
        """
        The state is Pacman's position. Fill this in with a goal test that will
        complete the problem definition.
        """

        #return self.food[state[0][0]][state[0][1]]
        global pojedenaHrana
        global ukupnoHrana
        global kraj

        x, y = state

        if self.food[x][y]  and state not in pojedenaHrana : #naisao na hranu koja nije pojedena
            pojedenaHrana.append((x, y)) #pojedi
            #print(pojedenaHrana)
            if len(pojedenaHrana) == ukupnoHrana:
                #print("kraj")
                kraj = True #pojedena sva hrana
            return True
        else:
            return False
        "*** YOUR CODE HERE ***"
        #util.raiseNotDefined()

