#!/usr/bin/python
import random
import numpy

N = 10000 #total number of people competing
n = 100 #max number of participants in a single race
races = 30000

people = {}
initialRanks = []
rand1 = random.Random(456)
rand2 = random.Random(456)
rand2.jumpahead(999)

means = []
stds = []

#initialize scores
for i in range(1, N+1):
    #rank = rand1.randint(1000, 1000)
    rank = rand1.gauss(1000, 200)
    people[i] = [rank, 0] #ID, initial rank, number of races participated in
    initialRanks.append(rank)
    

print "beginning calculations"
for i in range(0, races):
    if i % 1000 == 0:
        means.append(numpy.mean([v[0] for k,v in people.iteritems()]))
        stds.append(numpy.std([v[0] for k,v in people.iteritems()]))
        print "race", i

    #choose participants for
    noOfParticipants = rand1.randint(10, n)
    participants = rand1.sample(xrange(1, N+1), noOfParticipants)

    #arbitrarily choose mean race time and standard deviation
    MT = rand1.uniform(600, 360000)
    ST = MT / 10

    #generate run times
    results = []
    for j in participants:
        results.append([j, people[j][0], rand2.gauss(MT, ST)]) #save participant ID together with RT and score
        
        
    results = sorted(results, key=lambda x: x[2]) #rank by run times: quicke -> slow
    

    top90 = int(noOfParticipants*0.9)
    #uncomment following line to exclude the runners from receiving points at all
    #results = results[:top90] 
    #calculate mean rank and time and their standard deviations
    MP = 0.0
    MT = 0.0
    for j in range(0, top90):
        MP = MP + results[j][1]
        MT = MT + results[j][2]

    MP = MP / top90
    MT = MT / top90

    divMP = 0.0
    divMT = 0.0
    for j in range(0, top90):
        divMP = divMP + (results[j][1] - MP)**2
        divMT = divMT + (results[j][2] - MT)**2

    
    SP = (divMP / top90)**(0.5)
    ST = (divMT / top90)**(0.5)

    #needed if all start from the same score
    if SP == 0:
        SP = 200
##    if SP < 100:
##        SP = 100

    #calculate scores and update mean scores of runners
    for res in results:
        ID = res[0]
        RP = MP + SP * (MT - res[2]) / ST
        
        if RP < 0:
            RP = 0

        currRaceCount = people[ID][1]
        people[ID][0] = (currRaceCount * people[ID][0] + RP) / (currRaceCount + 1)
        people[ID][1] += 1

    

#rebase scores to mean=1000, std=200
##allScoresStd = numpy.std([v[0] for k,v in people.iteritems()])
##allScoresMean = numpy.mean([v[0] for k,v in people.iteritems()])
##for k,v in people.iteritems():
##    v[0] = (v[0] - allScoresMean) * 200 / allScoresStd + 1000


print "finished calculations. Final scores:"
    
mean = numpy.mean([v[0] for k,v in people.iteritems()])
finalRanks = [v[0] for k,v in people.iteritems()]
sdDiv = numpy.std([v[0] for k,v in people.iteritems()])

print "races", races
print "initMean", numpy.mean(initialRanks)
print "initSTD", numpy.std(initialRanks)
print "mean", mean
print "sdDiv", sdDiv


#plot graphs
import matplotlib.pyplot as plt
plt.hist(initialRanks, bins=100, normed=False, histtype='stepfilled', color='b', label='initial')
plt.hist(finalRanks, bins=100, normed=False, histtype='stepfilled', color='r', label='final')                        
#plt.title("Rank Histogram")
plt.xlabel("Rank")
plt.ylabel("Frequency")
#plt.figtext(0.15, 0.85, str(round(mean, 3)) + '(' + str(round(sdDiv, 3)) + ')')
plt.legend()
plt.show()
