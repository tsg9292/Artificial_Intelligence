#!/usr/bin/python3

#NLP HMM / Viterbi
#Heather Dykstra and Tatyana and Scot and Erik and Phil and YOU!

#1-define states -> not including _
#
#have initial probs
#   1-  a row for each letter
#       start w/ 1 to over-est.
#       array for 26 vector
#   2-  26X26 matrix for state
#   3-  26X26 matric for outputs

#if letter is at the start of a word
#add to init prob

#if letter follows a letter - 2rd array
#add to prob

#add to 3 no matter what at input, output (a,b) ?

#create probs -> as logs
#   normalize 1 on whole collumn
#   normalize 2 and 3 on each row

#viterbi...
#t=0
#find p(s0)p(o0|s0)
#matrix 1 + matrix 3
#save these for all letters
#t>0
#find p(sn-1)p(sn|sn-1)p(on|sn)
#matrix + matrix 2+ matrix 3
#save these for all

import sys
import pdb
import math
import string
import copy

def parse(filename):
    f = open(filename, "r")
    testing = False
    tcorrect=[[]]
    tincorrect=[[]]
    fcorrect=[[]]
    fincorrect=[[]]
    
    i=0
    for line in f:
        l = line.split()
        if  l[0] == ".." :
            testing = True
            i=0
            continue
        if l[0] == '.':
        	i = i+1
        	if not testing:
        		tcorrect.append([])
        		tincorrect.append([])
        	else:
        		fcorrect.append([])
        		fincorrect.append([])        		
        	continue
        if not testing:
        	tcorrect[i].append(l[0]) 
        	tincorrect[i].append(l[1])
        else:
            fcorrect[i].append(l[0]) 
            fincorrect[i].append(l[1])
            
    f.close()
    return tcorrect, tincorrect, fcorrect, fincorrect

mapping = {char: value for value, char in enumerate(string.ascii_lowercase) }

def hmm(tcorrect, tincorrect):
    #states = list("abcdefghijklmnopqrstuvwxyz"[0:26:1])
    #outputs = list("abcdefghijklmnopqrstuvwxyz"[0:26:1])
    initial_counts = [1]*26 #[1 for s in states] #26x1
    transition_counts = [[1 for i in range(26)] for j in range (26)]
    output_counts= [[1 for i in range(26)] for j in range (26)]

    k =0
    first_letter = True
    while k < len(tincorrect):
        if tcorrect[k] == '_':
            first_letter = True
            k = k + 1
            continue
        if first_letter:
            myInt = mapping[tcorrect[k]]
            myInt2 = mapping[tincorrect[k]]
            initial_counts[myInt]+= 1
            output_counts[myInt][myInt2] +=1
            first_letter = False
        else:
            myInt = mapping[tcorrect[k]]
            myInt1 = mapping[tcorrect[k-1]]
            myInt2 = mapping[tincorrect[k]]
            transition_counts[myInt1][myInt] +=1
            output_counts[myInt][myInt2] +=1
        k = k + 1
    #print("Original Initial Counts \n", initial_counts)
    #print("Original Transition Counts \n", transition_counts)
    #print("Original Output Counts \n", output_counts)

    

    # NOW FOR PROBABILITIES!
    
    line_sum_initial = 0.0
    IntSum = sum(initial_counts)
    for i in range(0,26):
        initial_counts[i] /= float(IntSum)
        initial_counts[i] = math.log(initial_counts[i])
    #print ("Initial Probabilities \n", initial_counts)
    
        
    #transition_counts
    for i in range(0,26):
        TranSum = sum(transition_counts[i])
        for j in range(0,26):
            transition_counts[i][j] /= float(TranSum)
            transition_counts[i][j] = math.log(transition_counts[i][j])
    #print ("Transition Probabilities \n", transition_counts)

    #output_counts!
    for i in range(0,26):
        OutSum = sum(output_counts[i])
        for j in range(0,26):
            output_counts[i][j] /= float(OutSum)
            output_counts[i][j] = math.log(output_counts[i][j])
    #print ("Output Probabilities \n", output_counts)
    
    return initial_counts , transition_counts, output_counts

def verterbi(initial_prob, transition_prob, output_prob, test_output):
    corrected_output = copy.deepcopy(test_output) #so I dont overwrite my test output
    states = list("abcdefghijklmnopqrstuvwxyz"[0:26:1])
    
    line_count = 0
    word_count = 0
    first_letter = True
    for k in test_output:
        if k == '_':
            first_letter = True
            line_count += 1
            word_count = 0
            pass
        elif first_letter:
            #basic Vit algor here
            matrix = [[0 for i in range(26)] for j in range (26)]
            i = mapping[k]
            for x in range(0,26):
                prob = initial_prob[x] + output_prob[x][i]
                matrix[word_count][x] = prob
            maxProb = max(matrix[word_count])
            for y in range(0,26):
                if matrix[word_count][y] == maxProb:
                    corrected_output[line_count] = states[y]
            first_letter = False
            line_count += 1
            word_count += 1
        else:
            #complicated Vit algor here
            i = mapping[k]
            for x in range(0,26):
                #Erik did this math for me.... THANKS MAN
                (prob, state) = max((matrix[word_count-1][y0] + transition_prob[y0][x] + output_prob[x][i],y0) for y0 in range(0,26)) #state -> dont know what this is?
                matrix[word_count][x] = prob
            maxProb = max(matrix[word_count])
            for y in range(0,26):
                if matrix[word_count][y] == maxProb:
                    corrected_output[line_count] = states[y]
            line_count += 1
            word_count += 1
            
    return corrected_output

def main():
    filename = sys.argv[1]
    
    tcorrect, tincorrect, fcorrect, fincorrect = parse(filename)
    #print these
    initial_prob , transition_prob, output_prob = hmm(tcorrect, tincorrect)

    corrected = verterbi(initial_prob, transition_prob, output_prob, fincorrect)

    print("Orignial Correct Spellings \n", fcorrect)
    print("Orignial Incorrect Spellings \n", fincorrect)
    print("Corrected Spellings \n", corrected) #print this
    #some random vars to generate some stats
    a = 0
    b = 0
    c = 0
    totalLetters = 0
    for i in range (len(fcorrect)):
        if fcorrect[i] != fincorrect[i]:
            a += 1
        if fcorrect[i] != corrected[i]:
            b += 1
        if fincorrect[i] != corrected[i]:
            c += 1
        totalLetters +=1
    
    print("Sum of all the letters that should have been corrected:",a)
    print("Sum of all the letters that are wrong (miscorrected or not corrected):",b)
    print("Sum of all the letters that I changed:",c)
            
    
if __name__ == '__main__':
   main()
    
