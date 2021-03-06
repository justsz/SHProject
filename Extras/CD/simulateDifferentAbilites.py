#!/usr/bin/python
import random
import numpy
import matplotlib.pyplot as plt

N = 10000
n = 100 #max number of participants in a single race
races = 10000

reruns = 10

MT = 1000
ST = MT / 10
mistakeWeight =  MT / 1000

means = []
stds = []
spS = []
individuals = []


people = {}
initialRanks = []
abilities = []
mistakesList = []
initRand = random.Random(819239) 
    #initialize scores
for i in range(1, N+1):
    rank = 1000
##    rank = initRand.gauss(1000, 200)
    ###Higher "ability" actually means slower runner
    ability = initRand.gauss(MT, ST)
##    rank = 2*MT - ability
##    if rank < 0:
##        rank = 0
##    mistakes = initRand.randint(5,15)
    mistakes = 1
    mistakesList.append(mistakes)
    people[i] = [rank, 0, ability, mistakes, []] #ID, initial rank, number of races participated in
    initialRanks.append(rank)
    abilities.append(ability)


for run in range (0, reruns):
    rand1 = random.Random(456)

    rand2 = random.Random(456)
    rand2.jumpahead(999)

    numpy.random.seed(678900)


    print "beginning calculations"
    for i in range(1, races):
        if i % 5000 == 0:
            means.append(numpy.mean([v[0] for k,v in people.iteritems()]))
            stds.append(numpy.std([v[0] for k,v in people.iteritems()]))
            print "race", i

        #choose participants for race
        noOfParticipants = rand1.randint(10, n)
        participants = rand1.sample(xrange(1, N+1), noOfParticipants)


        #generate run times
        results = []
        for j in participants:
            #save participant ID together with rank and RunTime
##            results.append([j, people[j][0], people[j][2]]) 
            results.append([j, people[j][0], people[j][2] + rand1.gauss(0, people[j][3] * mistakeWeight)]) 
##            results.append([j, people[j][0], people[j][2] + numpy.random.poisson(people[j][3]) * mistakeWeight]) #people[j][2]*2/MT
            
            
##        results = sorted(results, key=lambda x: x[2]) #sort by run times: quicke -> slow
        

        top90 = int(noOfParticipants*1.0)
        #results = results[0: top90]
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
##        if SP < 50:
##            SP = 50

        spS.append(SP)
        #calculate scores and update mean scores of runners
        for res in results:
            ID = res[0]
            RP = MP + SP * (MT - res[2]) / ST
            
            if RP < 0:
                RP = 0

            currRaceCount = people[ID][1]
            people[ID][4].append(RP)
            people[ID][0] = (currRaceCount * people[ID][0] + RP) / (currRaceCount + 1)
            people[ID][1] += 1


##    means.append(numpy.mean([v[0] for k,v in people.iteritems()]))
##    stds.append(numpy.std([v[0] for k,v in people.iteritems()]))
    #individuals.append(max([numpy.std(v[4]) for k,v in people.iteritems()]))
    individuals.append(numpy.mean([numpy.std(v[4]) for k,v in people.iteritems()]))

    #rebase
##    if (run >= 0):
##        allScoresStd = numpy.std([v[0] for k,v in people.iteritems()])
##        allScoresMean = numpy.mean([v[0] for k,v in people.iteritems()])
##        for k,v in people.iteritems():
##            v[0] = (v[0] - allScoresMean) * 200 / allScoresStd + 1000
    
    if (run < reruns - 1):
        for k,v in people.iteritems():
            v[1] = 1
            v[4] = [v[0]]

        

    #rebase scores to mean=1000, std=200
    ##allScoresStd = numpy.std([v[0] for k,v in people.iteritems()])
    ##allScoresMean = numpy.mean([v[0] for k,v in people.iteritems()])
    ##for k,v in people.iteritems():
    ##    v[0] = (v[0] - allScoresMean) * 200 / allScoresStd + 1000


print "finished calculations. Final scores:"

finalRanks = [v[0] for k,v in people.iteritems() if v[1] > 0]
mean = numpy.mean(finalRanks)
sdDiv = numpy.std(finalRanks)

print "races", races
print "initMean", numpy.mean(initialRanks)
print "initSTD", numpy.std(initialRanks)
print "final ranks mean", mean
print "final ranks sdDiv", sdDiv

abM = numpy.mean(abilities)
abSd = numpy.std(abilities)

#rebase abilities to the same mean and sdDiv of the ranks
#abilities = [((ab - abM) * sdDiv / abSd + mean) for ab in abilities]
#invert abilities about the mean to match the shape of the scores
#abilities = [(2*mean - ab) for ab in abilities]


#plot rank distribution

##    plt.hist(abilities, bins=100, normed=False, histtype='stepfilled', color='b', label='abilities')
##    plt.hist(finalRanks, bins=50, normed=False, histtype='stepfilled', color='r', label='finalRanks', alpha = 0.5)
##    plt.axvline(x=mean, color='black')
##    plt.title("Rank Histogram")
##    plt.xlabel("Rank")
##    plt.ylabel("Frequency")
##    plt.figtext(0.15, 0.85, str(round(mean, 3)) + '(' + str(round(sdDiv, 3)) + ')')
##    plt.legend()
##    plt.show()


#plot score vs ability

r = []
ab = []
sc = []
ystds = []
yerrors = []
sc_over_ab = []
for k,v in people.iteritems():
    r.append(k)
    ab.append(v[2])
    sc.append(v[0])
    ystds.append(numpy.std(v[4]))
    yerrors.append(numpy.std(v[4]) / v[1])
    sc_over_ab.append(v[0] / v[2])
##plt.plot(ab, ab, 'r--', sc, 'bs')
plt.figure()
plt.errorbar(ab, sc, yerr=ystds, fmt='ro')
plt.xlabel("Mean run time (seconds)")
plt.ylabel("Mean of scores")
plt.show()
plt.close()


