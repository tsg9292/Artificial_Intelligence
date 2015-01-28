#! /usr/bin/env python

# DiseasePredictor.py
# Written by Taylor Graham
# taylor.s.graham@colorado.edu

import getopt, sys, re
from numpy import *
from pbnt.Graph import *
from pbnt.Distribution import *
from pbnt.Node import *
from pbnt.Inference import *

try:
    from IPython import embed
except:
    pass

# Initialize the well defined bayes network given in our assignment
def build_bayes_net():
	# initialize nodes
	numNodes = 5

	pNode = BayesNode(0, 2, name="pollution")
	sNode = BayesNode(1, 2, name="smoker")
	cNode = BayesNode(2, 2, name="cancer")
	xNode = BayesNode(3, 2, name="xray")
	dNode = BayesNode(4, 2, name="dyspnoea")

	pNode.add_child(cNode)
	sNode.add_child(cNode)

	cNode.add_parent(pNode)
	cNode.add_parent(sNode)
	cNode.add_child(xNode)
	cNode.add_child(dNode)

	xNode.add_parent(cNode)
	dNode.add_parent(cNode)

	nodes = [pNode, sNode, cNode, xNode, dNode]

	#set node distributions
	pDistribution = DiscreteDistribution(pNode)
	index = pDistribution.generate_index([],[])
	pDistribution[index] = 0.1, 0.9
	pNode.set_dist(pDistribution)

	sDistribution = DiscreteDistribution(sNode)
	index = sDistribution.generate_index([],[])
	sDistribution[index] = 0.7, 0.3
	sNode.set_dist(sDistribution)

	dist = zeros([pNode.size(), sNode.size(), cNode.size()], dtype=float32)
	dist[0,0,] = [0.98, 0.02] #P(C|P=h, S=f)
	dist[0,1,] = [0.95, 0.05] #P(C|P=h, S=t)
	dist[1,0,] = [0.999, 0.001] #P(C|P=l, S=f)
	dist[1,1,] = [0.97, 0.03] #P(C|P=l, S=t)
	cDistribution = ConditionalDiscreteDistribution(nodes=[pNode, sNode, cNode], table=dist)
	cNode.set_dist(cDistribution)

	dist = zeros([cNode.size(), xNode.size()], dtype=float32)
	dist[0,] = [0.8, 0.2] #P(X|C=f)
	dist[1,] = [0.1, 0.9] #P(X|C=t)
	xDistribution = ConditionalDiscreteDistribution(nodes=[cNode, xNode], table = dist)
	xNode.set_dist(xDistribution)

	dist = zeros([cNode.size(), dNode.size()], dtype=float32)
	dist[0,] = [0.7, 0.3] #P(D|C=f)
	dist[1,] = [0.35, 0.65] #P(D|C=t)
	dDistribution = ConditionalDiscreteDistribution(nodes=[cNode, dNode], table = dist)
	dNode.set_dist(dDistribution)

	return BayesNet(nodes)

# Computes the marginal probability of one node          
# engine : the current bayes network engine in use      
# input : the desired node to determine probability for 
# printable : used to control output to the terminal
# returnable : used to control what is returned    
def compute_marginal_probability(engine, input, printable=True, returnable=True):
	Q = engine.marginal(input)[0]

	if input.name == 'pollution':
		tResult = 'low'
		fResult = 'high'
	else:
		tResult = 'true'
		fResult = 'false'

	true = Q.generate_index([True], range(Q.nDims))
	if printable:
		print "The marginal probability of", input.name + " = " + tResult + ":", Q[true]
	false = Q.generate_index([False], range(Q.nDims))
	if printable:
		print "The marginal probability of", input.name + " = " + fResult + ":", Q[false]

	if returnable:
		return Q[true]
	else:
		return Q[false]

# builds a tuple for use in calculating joint probabilities
# network : the bayes network to be acted upon
# var : the input that is being used
# uppercase : used whenever the input is all uppercase letters -> prob distribution
def compute_joint_tuple(network, var, uppercase = False):
	for node in network.nodes:
		if node.id == 0:
			pollution = node
		if node.id == 1:
			smoker = node
		if node.id == 2:
			cancer = node
		if node.id == 3:
			xray = node
		if node.id == 4:
			dyspnoea = node

	if uppercase:
		if var == 'P':
			input = pollution
		elif var == 'S':
			input = smoker
		elif var == 'C':
			input = cancer
		elif var == 'X':
			input = xray
		elif var == 'D':
			input = dyspnoea
		else:
			print "Input is not a valid node, must be in the set {P,S,C,X,D}"
			usage()
	else:
		if var == 'p':
			input = (pollution, True)
		elif var == 's':
			input = (smoker, True)
		elif var == 'c':
			input = (cancer, True)
		elif var == 'x':
			input = (xray, True)
		elif var == 'd':
			input = (dyspnoea, True)
		elif var == '~p':
			input = (pollution, False)
		elif var == '~s':
			input = (smoker, False)
		elif var == '~c':
			input = (cancer, False)
		elif var == '~x':
			input = (xray, False)
		elif var == '~d':
			input = (dyspnoea, False)
		else:
			print "Input is not a valid node, must be in the set {p,s,c,x,d,~p,~s,~c,~x,~d}"
			usage()

	return input

# Computes the entire joint probability distribution
# used whenever only upper case letters are input for joint probability
# engine : the current bayes network engine in use
# jointVarArray: a list of all the different nodes in the joint probability
def compute_joint_probability_distribution(engine, jointVarArray):
	from itertools import product # had to import here, wouldnt work at module level

	n = len(jointVarArray)
	newArray = list([jointVarArray]*2**n)
	allorderings = list(product([False, True], repeat = n))
	
	permutationList = []
	for i in range(len(newArray)):
		temp = []
		for j in range(n):
			temp.append((newArray[i][j], allorderings[i][j]))
		permutationList.append(temp)

	for item in permutationList:
		prob = compute_joint_probability(engine, item)
		jointstr = ""
		for twople in item:
			if twople[0].name == 'pollution':
				if twople[1]:
					jointstr += "pollution = low, "
				else:
					jointstr += "pollution = high, "
			else:
				if twople[1]:
					jointstr += twople[0].name + " = true, "
				else:
					jointstr += twople[0].name + " = false, "
		print "The joint probability of " + jointstr + "is " + str(prob)		

# computes individual joint probabilities
# engine : the current bayes network engine in use
# item : the probability to be evaluated (2 to 5 nodes)
def compute_joint_probability(engine, item):
	# case 1, we only have two vars
	# we know P(X=x, Y=y) = P(Y=y|X=x)*P(X=x)
	itemCopy = copy.copy(item)
	if len(itemCopy) == 2:
		tupleA, tupleB = itemCopy
		return compute_conditional_probability(engine, tupleB, [tupleA], False) * compute_marginal_probability(engine, tupleA[0], False, tupleA[1])

	firstElement = itemCopy.pop(0)
	return compute_conditional_probability(engine, firstElement, itemCopy, False) * compute_joint_probability(engine, itemCopy)

# builds a tuple for use in calculating conditional probabilities
# network :  the bayes network currently in use
# var : the input node being used
def compute_conditional_tuple(network, var):
	for node in network.nodes:
		if node.id == 0:
			pollution = node
		if node.id == 1:
			smoker = node
		if node.id == 2:
			cancer = node
		if node.id == 3:
			xray = node
		if node.id == 4:
			dyspnoea = node
	if var == 'p':
		input = (pollution, True)
	elif var == 's':
		input = (smoker, True)
	elif var == 'c':
		input = (cancer, True)
	elif var == 'x':
		input = (xray, True)
	elif var == 'd':
		input = (dyspnoea, True)
	elif var == '~p':
		input = (pollution, False)
	elif var == '~s':
		input = (smoker, False)
	elif var == '~c':
		input = (cancer, False)
	elif var == '~x':
		input = (xray, False)
	elif var == '~d':
		input = (dyspnoea, False)
	else:
		print "Input is not a valid node, must be in the set {p,s,c,x,d,~p,~s,~c,~x,~d}"
		usage()

	return input
		
# computes individual conditional probabilities
# engine : the bayes network engine in use
# input : the node we want to solve for
# condVarArray = the list of given nodes used for calculating probabilities
# printable : used to control output to the terminal		
def compute_conditional_probability(engine, input, condVarArray, printable=True):
	# Dealing with given conditions
	for var, truefalse in condVarArray:
		engine.evidence[var] = truefalse
		if var.name == 'pollution':
			if truefalse == True:
				condStr = 'pollution = low '
			else:
				condStr = 'pollution = high '
		else:
			if truefalse:
				condStr = var.name + " = true "
			else:
				condStr = var.name + " = false "
	
	# Dealing with unknown variable
	uVar, truefalse = input
	Q = engine.marginal(uVar)[0]
	index = Q.generate_index([truefalse],range(Q.nDims))
	if uVar.name == 'pollution':
		if truefalse:
			desiredResult = 'low'
		else:
			desiredResult = 'high'
	else:
		if truefalse:
			desiredResult = "true"
		else:
			desiredResult = "false"

	if printable:
		print "The conditional probability of", uVar.name + " = " + desiredResult + " |", condStr + "is", Q[index]

	return Q[index]

# This is where the magic happens
def main():
	try:
		arglist,remainder = getopt.getopt(sys.argv[1:], 'j:g:m:')
		if len(arglist) == 0: usage()
	except getopt.GetoptError as e:
		print str(e)
		usage()

	diseaseNet = build_bayes_net()
	for node in diseaseNet.nodes:
		if node.id == 0:
			pollution = node
		if node.id == 1:
			smoker = node
		if node.id == 2:
			cancer = node
		if node.id == 3:
			xray = node
		if node.id == 4:
			dyspnoea = node

	engine = JunctionTreeEngine(diseaseNet)

	for action, arguments in arglist:
		
		##########################
		# Case Joint Probability #
		##########################
		if action == "-j":
			# separate out capitol letters first
			split = re.findall('[A-Z]', arguments)
			jointVarArray = []
			if len(split) > 0:
				if len(re.findall('~?[a-z]', arguments)) > 0:
					usage()
				for var in split:
					jointVarArray.append(compute_joint_tuple(diseaseNet, var, True))
				compute_joint_probability_distribution(engine, jointVarArray)
			else: # implies that only lower case letters were used as args.	
				split = re.findall('~?[a-z]', arguments)
				for var in split:
					jointVarArray.append(compute_joint_tuple(diseaseNet, var))
					outputstr = ""
				for item in jointVarArray:
					if item[0].name == 'pollution':
						if item[1]:
							outputstr += "pollution = low, "
						else:
							outputstr += "pollution = high, "
					else:
						if item[1]:
							outputstr += item[0].name + " = true, "
						else:
							outputstr += item[0].name + " = false, "
				print "The joint probability of " + outputstr + "is", compute_joint_probability(engine, jointVarArray)
		
		############################
		# Case Marginal Probablity #
		############################
		elif action == "-m":
			if len(arguments) > 1:
				print "Marginal probabilities only apply to one node."
				usage()
			if arguments == 'P':
				input = pollution
			elif arguments == 'S':
				input = smoker
			elif arguments == 'C':
				input = cancer
			elif arguments == 'X':
				input = xray
			elif arguments == 'D':
				input = dyspnoea
			elif arguments == 'p' or arguments == 's' or arguments == 'c' or arguments == 'x' or arguments == 'd':
				print "Marginal probabilities require a upper case argument"
				usage()
			else:
				print "Input is not a valid node, must be in the set {P,S,C,X,D}"
				usage()

			compute_marginal_probability(engine,input)

		################################
		# Case Conditional Probability #
		################################
		elif action == "-g":
			split = arguments.split('|')
			unknownVar, givenVars = split
			input = compute_conditional_tuple(diseaseNet, unknownVar)

			conditionalVarArray = []
			conditionalGivenVars = re.findall('~?[a-z]', givenVars)
			for var in conditionalGivenVars:
				conditionalVarArray.append(compute_conditional_tuple(diseaseNet, var))

			compute_conditional_probability(engine, input, conditionalVarArray)

# prints help information
# used whenever someone messes up
def usage():
	print """
	Usage:
    	Flags:
    	-g  conditional probablity
    	-j  joint probability
    	-m  marginal probability

    	Input:
    	P  pollution   (p = low,  ~p = high)
    	S  Smoker     (s = true, ~s = false)
    	C  Cancer     (c = true, ~c = false)
    	D  Dyspnoea   (d = true, ~d = false)
    	X  X-Ray      (x = true, ~x = false)

    	Example
    	python bayesnet.py -jPSC
    	(joint probabilities for Pollution, Smoker, and Cancer)
    	python bayesnet.py -j~p~s~c
    	(joint probability for pollution = h, smoker = f, cancer = f)
    	python bayesnet.py -gc|s
    	(conditional probability for cancer given that someone is a smoker)
	"""
	sys.exit(2)

if __name__ == "__main__":
    main()
