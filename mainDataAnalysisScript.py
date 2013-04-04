#!/usr/bin/python

#imports
import helperFunctions as hFunc
import matplotlib.pyplot as plt
import numpy


#script control variables
FILENAME = "reducedData.csv"
PATTERN = '(\d+),(.*),(\d+),(\d+):(\d\d):(\d\d),(.*),?(\d*)'


keepHistory = True
keepGeneratedScore = True 
keepIntermediateScore = True
#note: keeping the generated or intermediate score counts as a "real race" result

initType = 'normal' #normal or constant
initMean = 1000
initStd = 200

cropType = 'slowestPercent' # slowestPercent or normal
cropLimit = 1.0 #setting this to 1 and using slowestPercent means no cutoff
givePointsToCropped = False
minSP = 0 #lower limit on SP

minRaceCount = 7 #number of races needed to be included in calculations of overall mean etc.

totalRuns = 2 #number of runs through data
shuffleRaces = False
dropIntermediateHistory = True #start each run fresh with a new rank estimate




#begin data analysis script

out = hFunc.processFile(FILENAME, PATTERN)
races, participants = out

totalScore = []
people = hFunc.initializeScores(initType, keepHistory, keepGeneratedScore, initMean, initStd, participants)
totalScore.append(sum([v[0] for k,v in people.iteritems()]))

print "number of people registered: ", len(people)

means = []
stds = []

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
                hFunc.updateRunnerScores(results, meansAndStds, people, keepHistory)
 
                                
        scoreMeanAndStd = hFunc.getMeanAndStdOfScores(people, keepHistory, minRaceCount, dropIntermediateHistory, run+1)
        m, s = scoreMeanAndStd
        means.append(m)
        stds.append(s)
        
        if dropIntermediateHistory and run < totalRuns-1:
                hFunc.dropIntermediateHistory (people, keepHistory, keepIntermediateScore)




temp = hFunc.getIndividualMeansAndStds(people, keepHistory, minRaceCount, dropIntermediateHistory, totalRuns)
finalRanks, finalStds = temp
print "number of people that participated in " + str(minRaceCount) + " or more races:", len(finalRanks)
print "number of races with 10 or more runners: ", raceCounter

scoreMeanAndStd = hFunc.getMeanAndStdOfScores(people, keepHistory, minRaceCount, dropIntermediateHistory, totalRuns)
mean, sdDiv = scoreMeanAndStd

plt.hist(finalRanks, bins=100, normed=False, histtype='stepfilled', color='r', label='final', alpha = 0.5)
plt.axvline(x=mean, color='black')
plt.xlabel("Rank")
plt.ylabel("Frequency")
#plt.figtext(0.15, 0.85, str(round(mean, 3)) + '(' + str(round(sdDiv, 3)) + ')')
#plt.legend()
plt.show()
