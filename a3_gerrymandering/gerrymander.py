# gerrymander.py
# Author: Taylor Graham
# taylor.s.graham@colorado.edu
# Date: 10/4/2014

import sys
import math
import os.path
import random
import time
from Queue import Queue

# used to create a tree
queue = Queue()
State = []

class voter():
	''' voter()
	A voter object represents one node on our inputted graph.
	Eventually, this node will be assigned to a district, which is
	tracked using the District[] list, and each node has a value, 
	which is what is input in the files.
	'''

	def __init__(self, vote):
		''' __init__(vote)
		initializes the specified node with a specific value 'vote'
		'''
		self.district = None
		self.vote = vote

class Node():
	''' Node()
	used to build a tree for the minimax search
	a node is simple one single element of the tree.
	in this program, a Node contains a list of the nodes children,
	a value, which is actually the state of the graph
	and a District list, which tracks all the allocated districts
	'''
	def __init__(self, value):
		'''
		initializes a Node of a tree with three default values:
		children: a list of children for this node
		value: this is actually the graph at whatever state this node is at
		District: a list that tracks all of the districts
		'''
		self.children = []
		self.value = value
		self.District = []

	def spawn(self, value, District):
		'''
		spawn a new child to the current node
		and fill in the new District that is spawned
		'''
		self.children.append(Node(value))
		self.District = District

def build_graph():
	''' build_graph()
	Builds a graph using the filename given in argv[1]
	Returns a nxn matrix of voter()'s where n is the number of lines in the file
	We have to assume that each graph is to be square
	'''
	# check to make sure we have enough arguments	
	if (len(sys.argv) < 2):
		print "ERROR: not enough arguments. usage: \n$ python gerrymander.py filename.txt"
		exit()
	# check to make sure the file to be read actually exists
	filename = sys.argv[1]
	if not (os.path.isfile(filename)):
		print "ERROR: file does not exist: '%s'  Exiting..." % filename
		exit()

	# building a nxn matrix from the input file.
	print 'Reading from %s' % filename
	if filename == 'largeNeighborhood.txt':
		print 'Warning: Gerrymandering does not go so well on larger neighborhoods...'
	f = open(filename, 'r')
	lines = f.readlines()
	f.close()
	size = len(lines)
	graph = []
	for i in range(len(lines)):
		temp = []
		for j in lines[i].split():
			temp.append(voter(j))
		graph.append(temp)
	# necessary for ignoring the trailing blank line in largeNeighborhood.txt
	if graph[size-1]==[]:
		graph.pop(size-1)
	return graph

def congruent(x,y,move):
	'''
	Returns True if a move starting at node x,y is congruent
	ie all four of the parts of the move are touching eachother.
	NOTE: I could not figure out how to make this scalable to the 8x8 case...
	so its somewhat hardcoded for district sizes of 4.
	'''
	num_congruent_nodes = 1 # starting node at x,y
	congruent_nodes = [(x,y)]
	# check the immidately ajacent nodes
	for i,j in move:
		if (x+1,y) == (i,j):
			num_congruent_nodes = num_congruent_nodes + 1
			congruent_nodes.append((i,j))
		if (x-1,y) == (i,j):
			num_congruent_nodes = num_congruent_nodes + 1
			congruent_nodes.append((i,j))
		if (x,y+1) == (i,j):
			num_congruent_nodes = num_congruent_nodes + 1
			congruent_nodes.append((i,j))		
		if (x,y-1) == (i,j):
			num_congruent_nodes = num_congruent_nodes + 1
			congruent_nodes.append((i,j))	
	
	# four immediately adjacent nodes, congruent
	if num_congruent_nodes == 4:
		return True
	
	# two immediately adjacent nodes
	if num_congruent_nodes == 3:
		xt,yt = congruent_nodes[1]
		xr,yr = congruent_nodes[2]
		for i,j in move:
			if (xt+1,yt) == (i,j):
				if not (i,j) in congruent_nodes:
					num_congruent_nodes = num_congruent_nodes + 1
					congruent_nodes.append((i,j))
			if (xt-1,yt) == (i,j):
				if not (i,j) in congruent_nodes:
					num_congruent_nodes = num_congruent_nodes + 1
					congruent_nodes.append((i,j))
			if (xt,yt+1) == (i,j):
				if not (i,j) in congruent_nodes:
					num_congruent_nodes = num_congruent_nodes + 1
					congruent_nodes.append((i,j))
			if (xt,yt-1) == (i,j):
				if not (i,j) in congruent_nodes:
					num_congruent_nodes = num_congruent_nodes + 1
					congruent_nodes.append((i,j))
			if (xr+1,yr) == (i,j):
				if not (i,j) in congruent_nodes:
					num_congruent_nodes = num_congruent_nodes + 1
					congruent_nodes.append((i,j))
			if (xr-1,yr) == (i,j):
				if not (i,j) in congruent_nodes:
					num_congruent_nodes = num_congruent_nodes + 1
					congruent_nodes.append((i,j))
			if (xr,yr+1) == (i,j):
				if not (i,j) in congruent_nodes:
					num_congruent_nodes = num_congruent_nodes + 1
					congruent_nodes.append((i,j))
			if (xr,yr-1) == (i,j):
				if not (i,j) in congruent_nodes:
					num_congruent_nodes = num_congruent_nodes + 1
					congruent_nodes.append((i,j))		
	
	# only one immediately adjacent node, start checking from that node
	if num_congruent_nodes == 2:
		xt,yt = congruent_nodes[1]
		for i,j in move:
			if (xt+1,yt) == (i,j):
				if not (i,j) in congruent_nodes:
					num_congruent_nodes = num_congruent_nodes + 1
					congruent_nodes.append((i,j))
			if (xt-1,yt) == (i,j):
				if not (i,j) in congruent_nodes:
					num_congruent_nodes = num_congruent_nodes + 1
					congruent_nodes.append((i,j))
			if (xt,yt+1) == (i,j):
				if not (i,j) in congruent_nodes:
					num_congruent_nodes = num_congruent_nodes + 1
					congruent_nodes.append((i,j))
			if (xt,yt-1) == (i,j):		
				if not (i,j) in congruent_nodes:
					num_congruent_nodes = num_congruent_nodes + 1
					congruent_nodes.append((i,j))	

	if num_congruent_nodes == 3:
		xt,yt = congruent_nodes[2]
		for i,j, in move:
			if (xt+1,yt) == (i,j):
				if not (i,j) in congruent_nodes:
					num_congruent_nodes = num_congruent_nodes + 1
					congruent_nodes.append((i,j))
			if (xt-1,yt) == (i,j):
				if not (i,j) in congruent_nodes:
					num_congruent_nodes = num_congruent_nodes + 1
					congruent_nodes.append((i,j))
			if (xt,yt+1) == (i,j):
				if not (i,j) in congruent_nodes:
					num_congruent_nodes = num_congruent_nodes + 1
					congruent_nodes.append((i,j))
			if (xt,yt-1) == (i,j):		
				if not (i,j) in congruent_nodes:
					num_congruent_nodes = num_congruent_nodes + 1
					congruent_nodes.append((i,j))

	if num_congruent_nodes == 4:
		return True

	return False

def is_valid_move(move, graph):
	''' is_valid_move(move[], graph[])
	returns True is the passed in move contains all
	empty nodes, and the move makes a valid shape.
	else, returns False

	A move is valid if all of the nodes in a district 
	are touching another node in the district.
	Also, all nodes in the district must not already be
	a part of another district.
	'''
	x,y = move[0]
	if not congruent(x,y,move):
		return False
	for x,y in move:
		if graph[x][y].district != None:
			return False
	return True

def heuristic(move, graph):
	'''
	returns the heuristic value for making move 'move'
	on a graph in state 'graph'
	values range from -1 to 3, depending on quality of the move
	'''
	r = d = 0
	for x,y in move:
		if graph[x][y].vote == 'R':
			r = r+1
		elif graph[x][y].vote == 'D':
			d = d+1
	if r==4:
		return 1
	if r==3 and d==1:
		return 2
	if r==d==2:
		return 0
	if r==1 and d==3:
		return -1
	if d==4:
		return 3

def heuristic_state(node):
	'''
	returns the overall value of the board once the game is finished
	return value is the number of districts that are won by the 'R' party
	ranging from -4 to 4
	'''
	r=d=R=D=T=0
	graph = node.value
	District = node.District
	for district in District:
		for x,y in district:
			if graph[x][y].vote == 'R':
				r=r+1
			elif graph[x][y].vote == 'D':
				d=d+1
		if r == d:
			T=T+1
		elif r>d:
			R=R+1
		elif r<d:
			D=D+1
	return R-D

#TODO: implement minimax search in here:
# involves building a tree of valid moves, and searching through to find the best one.
def minimax(node, depth, maxplayer):
	''' performs a minimax search
	node: the root node to search from
	depth: the max amount of iterations to do
	maxplayer: true if its MAX's turn

	NOTE: this method is not well tested because I was not able to successfully
	generate a tree of graph states to search through...
	However, I tested the algorithm with simple numbers instead of graph's, and the
	algorithm returned expected values.
	'''
	# if we've reached the max number of moves, or node is a leaf
	# evaluate the state of the board (should be complete)
	if (depth == 0 or node.children == []):
		return heuristic_state(node)
	# pick the maximum valued node out of the children
	if maxplayer:
		bestValue = -sys.maxsize
		for child in node.children:
			val = minimax(child, depth-1, False)
			bestValue = max(bestValue,val)
		return bestValue
	# pick the minimum valued node out of the children
	else:
		bestValue = sys.maxsize
		for child in node.children:
			val = minimax(child, depth-1, True)
			bestValue = min(bestValue, val)
		return bestValue

def find_move(graph):
	'''
	generates n random nodes in a nxn matrix
	returns a list of n (x,y) tuples,
	representing a single potential move for the board.
	Note that the returned move may not be valid, 
	just possible for the board.
	Move still needs to be checked after the fact to ensure validity
	'''
	move = []
	length = len(graph)
	while len(move) < length:
		x = random.randint(0,length-1)
		y = random.randint(0,length-1)
		move.append((x,y))
	return move

def make_move(graph,max):
	'''
	This is used more for simulating four turns of the game
	You'll find that the 'R' team is able to win! (ideal)
	'''
	if max: value = -2
	else: value = 4
	best_move = []
	iterator = 0
	# evaluate 1000000 potential moves and select the best one
	while(iterator < 1000000):
		move = find_move(graph)
		if is_valid_move(move, graph):
			if max: # if its MAX players turn
				if heuristic(move, graph) > value:
					value = heuristic(move, graph)
					best_move = move
			else: # if its MIN players turn
				if heuristic(move,graph) < value:
					value = heuristic(move, graph)
					best_move = move
		iterator = iterator+1
	
	State.append(move)
	district_num = len(State)
	for x,y in best_move:
		graph[x][y].district = district_num

	return graph

def build_tree(graph):
	'''
	this method is supposed to build a tree of potential games
	unfortunately, I was not able to get it working correctly, much to 
	the dismay of, well, this entire project...

	The idea was to start with an initial node and an empty graph,
	and spawn possible moves as children.  As I spawn children, I add them
	to the queue.  Once I spawn a reasonable amount of children for the first node,
	then I pop the next child off the queue, and start spawning children for that node,
	which includes enqueueing those children as well.   I would continue this process until
	I get 4 levels deep of children, ie 4 different moves were simulated on one game board.

	I think I fell short in the queueing process...

	Note: it creates a tree, just no where near as deep or large as I needed...
	'''
	depth = 0
	tree = Node(graph)
	queue.put(tree)
	while not queue.empty():
		node = queue.get()
		for i in range(100000):
			District = []
			graph = node.value
			move = find_move(node.value)
			if is_valid_move(move, graph) and not move in node.children:
				District.append(move)
				district_num = len(District)
				for x,y in move:
					graph[x][y].district = district_num
				node.spawn(graph, District)
				length = len(node.children)
				queue.put(node.children[length-1])

	return tree

def print_results(graph):
	print 'Printing results...'
	print
	print '*********************************************'
	print     
	print 'MAX=R'
	print 'MIN=D'
	print
	print '*********************************************'
	print
	for i in range(len(State)):
		tmp = []
		for x,y in State[i]:
			tmp.append(graph[x][y].vote)
	 	print 'District ' + str(i+1) + ': ' + str(tmp)
	print
	print '*********************************************'
	print
	R=D=0
	for i in range(len(State)):
		d = r = 0
		for x,y in State[i]:
			vote = graph[x][y].vote
			if vote == 'R':
				r = r+1
			elif vote == 'D':
				d = d+1	
		if r>d:
			result = 'R'
			R = R+1
		elif d>r:
			result = 'D'
			D=D+1
		else: #r==d
			result = 'T'
		print 'District ' + str(i+1) + ': ' + result
	print
	print '*********************************************'
	print
	if D>R:
		print 'Election outcome: D wins %i,%i,%i' % (R,D,len(graph)-R-D)
	elif R>D:
		print 'Election outcome: R wins %i:%i:%i' % (R,D,len(graph)-R-D)
	elif D==R:
		print 'Election outcome: Tied game'
	print
	print '*********************************************'

def gerrymander():
	beginning_time = time.time()
	graph = build_graph()
	print
	print 'Gerrymandering.....'
	tree = build_tree(graph)
	minimax(tree,4,True)

	i = 1
	while len(State) < len(graph):
		print 'move %i' % i
		graph = make_move(graph,True)
		i = i+1
	print
	print_results(graph)
	final_time = time.time()-beginning_time
	print "Runtime: %f seconds"%final_time

if __name__ == "__main__":
	gerrymander()
