from algorithms.problems import SearchProblem
import algorithms.utils as utils
from world.game import Directions
from algorithms.heuristics import nullHeuristic


def tinyDiagnosticSearch(problem: SearchProblem):
    """
    Returns a hard-coded sequence of moves for the tinyDiagnostic layout.
    For any other station layout, the sequence of moves will be incorrect.
    """
    s = Directions.SOUTH
    e = Directions.EAST
    return [s, e, s, e, e, e, e, s, e, e, s, s, e, s, s, e, s, e, e, e, e, e, e, e]


def depthFirstSearch(problem: SearchProblem):
    visited = set()
    lifo = utils.Stack()
    lifo.push([problem.getStartState(), []])
    
    while not lifo.isEmpty():
        tupla = lifo.pop()
        state = tupla[0]
        action_seq = tupla[1]
        
        if problem.isGoalState(state):
            return action_seq
            
        if state not in visited:
            visited.add(state)
            
        for tripla in problem.getSuccessors(state):
            next_state = tripla[0]
            action = tripla[1]
            if next_state not in visited:
                lifo.push([next_state, action_seq + [action]])
    return []

    

def breadthFirstSearch(problem: SearchProblem):
    visited = set()
    queue = utils.Queue()
    queue.push([problem.getStartState(), []])
    
    while not queue.isEmpty():
        tupla = queue.pop()
        state = tupla[0]
        action_seq = tupla[1]
        
        if problem.isGoalState(state):
            return action_seq
            
        if state not in visited:
            visited.add(state)
            
        for tripla in problem.getSuccessors(state):
            next_state = tripla[0]
            action = tripla[1]
            if next_state not in visited:
                queue.push([next_state, action_seq + [action]])
    return []


def uniformCostSearch(problem: SearchProblem):
    visited = set()
    queue = utils.PriorityQueue()
    queue.push([problem.getStartState(),[],0],0)
    
    while not queue.isEmpty():
        tupla = queue.pop()
        state = tupla[0]
        action_seq = tupla[1]
        cost = tupla[2]
        
        if problem.isGoalState(state):
            return action_seq
            
        if state not in visited:
            visited.add(state)
            
        for tripla in problem.getSuccessors(state):
            next_state = tripla[0]
            action = tripla[1]
            next_cost = tripla[2]
            if next_state not in visited:
                queue.push([next_state, action_seq + [action], cost + next_cost], cost + next_cost)
    return []


def aStarSearch(problem: SearchProblem, heuristic=nullHeuristic):
    visited = set()
    queue = utils.PriorityQueue()
    queue.push([problem.getStartState(),[],0],0)
    
    while not queue.isEmpty():
        tupla = queue.pop()
        state = tupla[0]
        action_seq = tupla[1]
        cost = tupla[2]
        
        if problem.isGoalState(state):
            return action_seq
            
        if state not in visited:
            visited.add(state)
            
        for tripla in problem.getSuccessors(state):
            next_state = tripla[0]
            action = tripla[1]
            next_cost = tripla[2]
            if next_state not in visited:
                queue.push([next_state, action_seq + [action], cost + next_cost], cost + next_cost)
    return []


# Abbreviations (you can use them for the -f option in main.py)
bfs = breadthFirstSearch
dfs = depthFirstSearch
astar = aStarSearch
ucs = uniformCostSearch
