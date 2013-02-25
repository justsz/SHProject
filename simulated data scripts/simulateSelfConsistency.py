#!/usr/bin/python
import random
import numpy
import matplotlib.pyplot as plt

N = 1000 #total number of people competing
races = 10000

MT = 100000
ST = MT / 10

people = {}
initialRanks = []
abilities = []
rand1 = random.Random(456)

rand2 = random.Random(456)
rand2.jumpahead(999)

numpy.random.seed(678900)

#initialize scores
for i in range(1, N+1):
    rank = rand1.randint(1000, 1000)
##    rank = rand1.gauss(1000, 200)
    ability = rand1.gauss(MT, ST)
    people[i] = [rank, 0, ability] #ID, initial rank, number of races participated in
    initialRanks.append(rank)
    abilities.append(ability)

noOfParticipants = N
participants = range(1, noOfParticipants+1)
differences = []
maxDifferences = []


#generate run times
results = []
for j in participants:
    #save participant ID together with rank and RunTime
##        results.append([j, people[j][0], people[j][2]]) 
        results.append([j, people[j][0], people[j][2] + abs(rand1.gauss(0, people[j][2] * 0.1))]) 
##        results.append([j, people[j][0], people[j][2] + numpy.random.poisson(5) * MT / 100])

results = sorted(results, key=lambda x: x[2]) #rank by run times: quicke -> slow


#pre-calculate MT and ST as they will stay the same
top90 = int(noOfParticipants*1.0)
MT = 0.0
for j in range(0, top90):
    MT = MT + results[j][2]
MT = MT / top90

divMT = 0.0
for j in range(0, top90):
    divMT = divMT + (results[j][2] - MT)**2
ST = (divMT / top90)**(0.5)


print "beginning calculations"
print "iteration, maxDif, difMean"
for i in range(1, races):
    #calculate mean rank its standard deviations
    MP = 0.0
    for j in range(0, top90):
        MP = MP + results[j][1]
    MP = MP / top90
    
    divMP = 0.0
    for j in range(0, top90):
        divMP = divMP + (results[j][1] - MP)**2
    SP = (divMP / top90)**(0.5)

    #needed if all start from the same score
    if SP == 0:
        SP = 200

    differences[:] = []
    #calculate scores and update mean scores of runners
    for res in results:
        ID = res[0]
        RP = MP + SP * (MT - res[2]) / ST
        
        if RP < 0:
            RP = 0

        newScore = (i * people[ID][0] + RP) / (i + 1)
        differences.append(abs(newScore - people[ID][0]))
        people[ID][0] = newScore
        
    maxDif = max(differences)
    maxDifferences.append(maxDif)
    
    if i<100 or i%100==0:
        print i, maxDif, numpy.mean(differences)
    if maxDif < 0.001:
        print "races", i
        break
    

    

#rebase scores to mean=1000, std=200
##allScoresStd = numpy.std([v[0] for k,v in people.iteritems()])
##allScoresMean = numpy.mean([v[0] for k,v in people.iteritems()])
##for k,v in people.iteritems():
##    v[0] = (v[0] - allScoresMean) * 200 / allScoresStd + 1000


print "finished calculations. Final scores:"

finalRanks = [v[0] for k,v in people.iteritems()]
mean = numpy.mean(finalRanks)
sdDiv = numpy.std(finalRanks)


print "initMean", numpy.mean(initialRanks)
print "initSTD", numpy.std(initialRanks)
print "final ranks mean", mean
print "final ranks sdDiv", sdDiv

abM = numpy.mean(abilities)
abSd = numpy.std(abilities)

abilities = [((ab - abM) * sdDiv / abSd + mean) for ab in abilities]


#plot graphs


##r = []
##ab = []
##sc = []
##for k,v in people.iteritems():
##    r.append(k)
##    ab.append(v[2])
##    sc.append(v[0])
####plt.plot(ab, ab, 'r--', sc, 'bs')
##plt.plot(ab, sc, 'ro')
##plt.show()

plt.plot(maxDifferences[0:100], 'ro')
plt.show()
