#!/usr/bin/python

#imports
import helperFunctions as hFunc
import matplotlib.pyplot as plt
import numpy


#script control variables
FILENAME = "reducedData.csv"
PATTERN = '(\d+),(.*),(\d+),(\d+):(\d\d):(\d\d),(.*),?(\d*)'


keepHistory = True
keepGeneratedScore = True #note: if True, every racer has at least 1 "real race"
                        #might need to separate the cases...


initType = 'constant' #normal or constant
initMean = 1000
initStd = 200


cropType = 'slowestPercent' # slowestPercent or normal
cropLimit = 1
givePointsToCropped = True
minSP = 50

minRaceCount = 6

totalRuns = 20
shuffleRaces = False
dropIntermediateScores = True




#begin data analysis script

out = hFunc.processFile(FILENAME, PATTERN)
races, participants = out

totalScore = []
people = hFunc.initializeScores(initType, keepHistory, keepGeneratedScore, initMean, initStd, participants)
totalScore.append(sum([v[0] for k,v in people.iteritems()]))

print "number of people registered: ", len(people)

means = []
stds = []
sps = []

print "processing race results..."
raceCounter = 0
for run in range(0, totalRuns):
        print "Run through data number", run + 1
        if shuffleRaces:
                hFunc.shuffle(races)
                
        for race in races:
                raceCounter += 1
                if (raceCounter % 1000 == 0):
                        print "race", raceCounter
                
                results = hFunc.getResults(race, people)
                meansAndStds = hFunc.cropResultsAndCalcMeansAndStds(results, cropType, cropLimit, givePointsToCropped, minSP)
                sps.append(meansAndStds[1])
                hFunc.updateRunnerScores(results, meansAndStds, people, keepHistory)
                                
        scoreMeanAndStd = hFunc.getMeanAndStdOfScores(people, keepHistory, minRaceCount, dropIntermediateScores, run+1)
        m, s = scoreMeanAndStd
        means.append(m)
        stds.append(s)
        totalScore.append(sum([v[0] for k,v in people.iteritems()]))

        if dropIntermediateScores and run < totalRuns-1:
                hFunc.dropIntermediateScores (people, keepHistory, keepGeneratedScore)



#hFunc.rebaseScores(people, 1000, 200, minRaceCount)

temp = hFunc.getIndividualMeansAndStds(people, keepHistory, minRaceCount, dropIntermediateScores, totalRuns)
finalRanks, finalStds = temp
print "number of people that participated in " + str(minRaceCount) + " or more races:", len(finalRanks)
print "number of races with 10 or more runners: ", raceCounter

scoreMeanAndStd = hFunc.getMeanAndStdOfScores(people, keepHistory, minRaceCount, dropIntermediateScores, totalRuns)
mean, sdDiv = scoreMeanAndStd

plt.hist(finalRanks, bins=100, normed=False, histtype='stepfilled', color='r', label='final', alpha = 0.5)
plt.axvline(x=mean, color='black')
plt.title("Rank Histogram")
plt.xlabel("Rank")
plt.ylabel("Frequency")
plt.figtext(0.15, 0.85, str(round(mean, 3)) + '(' + str(round(sdDiv, 3)) + ')')
plt.legend()
plt.show()
