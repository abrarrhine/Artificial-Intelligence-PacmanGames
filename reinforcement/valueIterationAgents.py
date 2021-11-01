# valueIterationAgents.py
# -----------------------
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


# valueIterationAgents.py
# -----------------------
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


import mdp, util

from learningAgents import ValueEstimationAgent
import collections

class ValueIterationAgent(ValueEstimationAgent):
    """
        * Please read learningAgents.py before reading this.*

        A ValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs value iteration
        for a given number of iterations using the supplied
        discount factor.
    """
    def __init__(self, mdp, discount = 0.9, iterations = 100):
        """
          Your value iteration agent should take an mdp on
          construction, run the indicated number of iterations
          and then act according to the resulting policy.

          Some useful mdp methods you will use:
              mdp.getStates()
              mdp.getPossibleActions(state)
              mdp.getTransitionStatesAndProbs(state, action)
              mdp.getReward(state, action, nextState)
              mdp.isTerminal(state)
        """
        self.mdp = mdp
        self.discount = discount
        self.iterations = iterations
        self.values = util.Counter() 
        self.runValueIteration()

    def runValueIteration(self):
        # Write value iteration code here
        "*** YOUR CODE HERE ***"
        while self.iterations > 0:
            tempValue = self.values.copy()  
            states = self.mdp.getStates() 
            for i in states: 
                pAction = self.mdp.getPossibleActions(i)
                possibleVals = []
                for action in pAction:
                    endStates = self.mdp.getTransitionStatesAndProbs(i, action)
                    weighted = 0
                    for s in endStates: 
                        nextState = s[0]
                        probability = s[1]
                        reward = self.mdp.getReward(i, action, nextState)
                        weighted += (probability * (reward + (self.discount * tempValue[nextState]))) 
                    possibleVals.append(weighted)
                if len(possibleVals) != 0:
                    self.values[i] = max(possibleVals)
            self.iterations -= 1 


    def getValue(self, state):
        """
          Return the value of the state (computed in __init__).
        """
        return self.values[state]


    def computeQValueFromValues(self, state, action):
        """
          Compute the Q-value of action in state from the
          value function stored in self.values.
        """
        "*** YOUR CODE HERE ***"
        endStates = self.mdp.getTransitionStatesAndProbs(state, action)
        weighted = 0
        for s in endStates:
            nextState = s[0]
            probability = s[1]
            result = self.mdp.getReward(state, action, nextState)
            weighted += (probability * (result  + (self.discount * self.values[nextState])))

        return weighted

    def computeActionFromValues(self, state):
        """
          The policy is the best action in the given state
          according to the values currently stored in self.values.

          You may break ties any way you see fit.  Note that if
          there are no legal actions, which is the case at the
          terminal state, you should return None.
        """
        "*** YOUR CODE HERE ***"
        if self.mdp.isTerminal(state): #edge case
            return None
        actions = self.mdp.getPossibleActions(state)
        endAction = ""
        max = float("-inf") 
        for action in actions:
            weighted = self.computeQValueFromValues(state, action)
            if (max == float("-inf") and action == "") or weighted >= max:
                endAction = action
                max = weighted
        return endAction
        

    def getPolicy(self, state):
        return self.computeActionFromValues(state)

    def getAction(self, state):
        "Returns the policy at the state (no exploration)."
        return self.computeActionFromValues(state)

    def getQValue(self, state, action):
        return self.computeQValueFromValues(state, action)

class AsynchronousValueIterationAgent(ValueIterationAgent):
    """
        * Please read learningAgents.py before reading this.*

        An AsynchronousValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs cyclic value iteration
        for a given number of iterations using the supplied
        discount factor.
    """
    def __init__(self, mdp, discount = 0.9, iterations = 1000):
        """
          Your cyclic value iteration agent should take an mdp on
          construction, run the indicated number of iterations,
          and then act according to the resulting policy. Each iteration
          updates the value of only one state, which cycles through
          the states list. If the chosen state is terminal, nothing
          happens in that iteration.

          Some useful mdp methods you will use:
              mdp.getStates()
              mdp.getPossibleActions(state)
              mdp.getTransitionStatesAndProbs(state, action)
              mdp.getReward(state)
              mdp.isTerminal(state)
        """
        ValueIterationAgent.__init__(self, mdp, discount, iterations)

    def runValueIteration(self):
        "*** YOUR CODE HERE ***"
        for i in range(self.iterations):
            index = i %  len(self.mdp.getStates())
            allState = self.mdp.getStates()[index]
            top = self.computeActionFromValues(allState)
            if not top:
                qval = 0
            else:
                qval = self.computeQValueFromValues(allState, top)
            self.values[allState] = qval

class PrioritizedSweepingValueIterationAgent(AsynchronousValueIterationAgent):
    """
        * Please read learningAgents.py before reading this.*

        A PrioritizedSweepingValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs prioritized sweeping value iteration
        for a given number of iterations using the supplied parameters.
    """
    def __init__(self, mdp, discount = 0.9, iterations = 100, theta = 1e-5):
        """
          Your prioritized sweeping value iteration agent should take an mdp on
          construction, run the indicated number of iterations,
          and then act according to the resulting policy.
        """
        self.theta = theta
        ValueIterationAgent.__init__(self, mdp, discount, iterations)

    def getQVals(self, state):
        possibleActions = self.mdp.getPossibleActions(state)  
        countQVals = util.Counter()  

        for action in possibleActions:
            countQVals[action] = self.computeQValueFromValues(state, action)
        return countQVals

    def runValueIteration(self):
        pq = util.PriorityQueue()
        allStates = self.mdp.getStates()
        predeccessors = {} 
        for state in allStates:
            predeccessors[state]=set()
        for state in allStates:
            allActions=self.mdp.getPossibleActions(state)
            for action in allActions:
                possibleNextStates = self.mdp.getTransitionStatesAndProbs(state, action)
                for posState in possibleNextStates:
                    if posState[1]>0:
                        predeccessors[posState[0]].add(state)
        for state in allStates: 
            allQValues = self.getQVals(state)
            if len(allQValues) > 0:
                maxQ = allQValues[allQValues.argMax()]
                diff = abs(self.values[state] - maxQ)
                pq.push(state, -diff)
        for i in range(self.iterations):
            if pq.isEmpty():
                return None
            state = pq.pop()
            allQValues = self.getQVals(state)
            maxQ = allQValues[allQValues.argMax()]
            self.values[state] = maxQ
            for p in predeccessors[state]:

                vals = self.getQVals(p)
                maxQ = vals[vals.argMax()]
                diff = abs(self.values[p] - maxQ)
                if diff > self.theta:
                    pq.update(p, -diff)
