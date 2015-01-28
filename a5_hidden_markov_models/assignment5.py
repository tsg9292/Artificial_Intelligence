#assignment5.py
#Taylor Graham
#taylor.s.graham@colorado.edu

import getopt, sys, pdb, math, string, copy

def parse(filename):
    f = open(filename, "r")
    testing = False
    test_states=[]
    test_obs=[]
    final_states=[]
    final_obs=[]
    
    for line in f:
        l = line.split()
        if  l[0] == ".." :
            testing = True
            continue
        if l[0] == '.':
            if not testing:
                test_states.append(l[0])
                test_obs.append('')
                continue
            else:
                final_states.append(l[0])
                final_obs.append('')
                continue
        if not testing:
            test_states.append(l[0])
            test_obs.append(l[1])
        else:
            final_states.append(l[0])
            final_obs.append(l[1])            
    f.close()
    return test_states, test_obs, final_states, final_obs

def runHmm(problemNumber, hmmOrder):
    #######################
    ## toy robot problem ##
    #######################
    if problemNumber == 1:
    	print 'Beginning the toy robot problem...'
        filename = 'robot_no_momemtum.data'
        if hmmOrder == 1:
            test_states, test_obs, final_states, final_obs = parse(filename)

            start_prob, transition_prob, emission_prob = hmm(test_states, test_obs)

            corrected = verterbi(final_obs, start_prob, transition_prob, emission_prob)

            print_results(final_states, final_obs, corrected)
        elif hmmOrder == 2:
            #call first order hmm
            print("Second order Marcov Model functionality not implemented")
        else:
            print "No HMM with order", hmmOrder
    
    #############################
    ## typo correction problem ##
    #############################
    elif problemNumber == 2:
        print 'Beginning the typo corection problem...'
        filename = 'typos10.data'
        if hmmOrder == 1:
            test_states, test_obs, final_states, final_obs = parse(filename)

            start_prob, transition_prob, emission_prob = hmm(test_states, test_obs)

            corrected = verterbi(final_obs, start_prob, transition_prob, emission_prob)

            print_results(final_states, final_obs, corrected)
        elif hmmOrder == 2:
            #call first order hmm
            print("Second order Marcov Model functionality not implemented")
        else:
            print "No HMM with order", hmmOrder
    
    ##############################
    ## topic correction problem ##
    ##############################
    elif problemNumber == 3:
        print 'Beginning the topic correction problem...'
        if hmmOrder == 1:
            test_states, test_obs, final_states, final_obs = parse('topics.data')
            start_prob, transition_prob, emission_prob = hmm(test_states, test_obs)
            print('Unfortunately, I couldnt manage to get problem 3 to work with verterbi. Exiting...')
            sys.exit(2)
            corrected = verterbi(final_obs, start_prob, transition_prob, emission_prob)
            print_results(final_obs, final_states, corrected)
        elif hmmOrder == 2:
            #call first order hmm
            print("Second order Marcov Model functionality not implemented")
        else:
            print "No HMM with order", hmmOrder
    else:
        print "No problem associated with number", problemNumber

def hmm(test_states, test_obs):
    print 'Building Hidden Markov Model...'
    start_count = {}
    trans_count = {}
    emit_count = {}

    #initialize with laplace smoothing
    states = []
    observations = []
    for x in test_states:
        if x not in states and not x == '.':
        	states.append(x)
    for x in test_obs:
    	if x not in observations and not x == '':
    		observations.append(x)

    for s in states:
    	start_count.update({s:1})
    	for t in states:
    		trans_count.update({(s,t):1})
    	for o in observations:
    		emit_count.update({(s,o):1})

    starting_pos = True
    for i in range(len(test_states)):
        state = test_states[i]
        obs = test_obs[i]
        if state == '_':
            starting_pos = True
            continue
        if state == '.':
        	starting_pos = True
        	continue
        if starting_pos:
            if start_count.has_key(state):    
                start_count.update({state:start_count[state]+1})
            else:
                start_count.update({state:1})
            starting_pos = False
        else:
            prev_state = test_states[i-1]
            if trans_count.has_key((prev_state, state)):
                trans_count.update({(prev_state, state):trans_count[(prev_state, state)]+1})
            else:
                trans_count.update({(prev_state, state):1})
        if emit_count.has_key((state, obs)):
            emit_count.update({(state, obs):emit_count[(state, obs)]+1})
        else:
            emit_count.update({(state, obs):1})

    # Counts are done, now for probabilities!
    startSum = sum(start_count.values())
    transSum = sum(trans_count.values())/len(states)
    emitSum = sum(emit_count.values())/len(observations)

    for key in start_count.keys():
        start_count.update({key:start_count[key]/float(startSum)})
        start_count.update({key:math.log(start_count[key])})
    for key in trans_count.keys():
        trans_count.update({key:trans_count[key]/float(transSum)})
        trans_count.update({key:math.log(trans_count[key])})
    for key in emit_count.keys():
        emit_count.update({key:emit_count[key]/float(emitSum)})
        emit_count.update({key:math.log(emit_count[key])})

    return start_count, trans_count, emit_count

def verterbi(obs, start_p, trans_p, emit_p):
	print 'Beginning verterbi algorithm...'

	for x in obs:
		if x == '' or x == '_':
			obs.remove(x)

	states = []
	for x in emit_p.keys():
		if x[0] not in states and not x[0] == '.':
			states.append(x[0])
	V = [{}]
	path = {}
	# initialize base cases (t == 0)
	for y in states:
		V[0][y] = start_p[y] * emit_p[(y,obs[0])]
		path[y] = [y]

	# now for (t > 0)
	for t in range(1, len(obs)):
		V.append({})
		newpath = {}

		for y in states:
			if not emit_p.has_key((y, obs[t])):
				continue
			(prob, state) = max((V[t-1][y0] + trans_p[(y0, y)] + emit_p[(y, obs[t])], y0) for y0 in states)
			V[t][y] = prob
			newpath[y] = path[state] + [y]
		path = newpath
	n = 0
	if len(obs) != 1:
		n = t

	(prob, state) = max((V[n][y], y) for y in states)
	return (prob, path[state])

def print_results(final_states, original_states, corrected):
    #some random vars to generate some stats
    robot = False
    for x in final_states:
    	if x == '.' or x == '_':
    	    final_states.remove(x)
    for x in original_states:
	if x == '.' or x == '_':
	    original_states.remove(x)
    if "2:1" in final_states:
	robot = True
    a = 0
    b = 0
    c = 0
    if not robot:
        for j in range(len(final_states)):
            if final_states[j] != original_states[j]:
                a = a + 1
            if final_states[j] != corrected[1][j]:
                b = b + 1
            if original_states[j] != corrected[1][j]:
                c = c + 1
    
        print("Sum of all the states that should have been corrected:",a)
        print("Sum of all the states that are wrong (miscorrected or not corrected):",b)
        print("Sum of all the states that I changed:",c)
        print("Percentage of states that were correctly fixed:",float(a)/float(b))
        print("Percentage of states that are correct now:",float(b)/float(len(final_states)))
    else:
	for j in range(len(final_states)):
	    if final_states[j] != corrected[1][j]:
                a = a+1
	print("Percentage of correct states:",1-(float(a)/float(len(final_states))))

def usage():
    print """
    Usage:
        Flags:
        -p problem number
        -o hmm order

        Input:
        Problem Number:
            1 (run Toy Robot problem)
            2 (run Typo Correction problem)
            3 (run Topic Correction problem)

        HMM Order:
            1 (1st order HMM)
            2 (2nd order HMM)*not supported yet

    Example:
    python assignment5.py -p 1 -o 1
    (run the toy robot problem with a 1st order hmm)
    python assignment5.py -p 2 -o 2
    (run the typo correction algorithm with a 2st order hmm)
    python assignemnt5.py -p 3 -o 1
    (run the topic correction problem with a 1st order hmm)
    """
    sys.exit(2)

def main():
    try:
        optlist, remainder = getopt.getopt(sys.argv[1:],'p:o:')
        if len(optlist) <= 1:
            usage()
    except getopt.GetoptError as err:
        print str(err)
        usage()

    for o, a in optlist:
        if o == "-p":
            problemNumber = int(a)
        elif o == "-o":
            hmmOrder = int(a)
    
    runHmm(problemNumber,hmmOrder)

if __name__ == "__main__":
    main()
