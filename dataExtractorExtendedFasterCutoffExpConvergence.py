#!/usr/bin/python

import fileinput
import re
import matplotlib.pyplot as plt
import numpy
import random
rand = random.Random(456)
CURRENT_YEAR = 2013


#sample data
#res_eday,res_course_num,res_bof_num,res_time, course_name, res_yob
#60575,5,113948,00:12:00, White, 1990


races = {}
participants = []

filename = "reducedData.csv"
pattern = '(\d+),(.*),(\d+),(\d+):(\d\d):(\d\d),(.*),?(\d*)'
counter = 0

means = []
divs = []
maxDifferences = []
differences = []

stdCutoff = 2



print 'beginning to read file'
for line in fileinput.input([filename]):
        counter += 1
        if (counter % 10000) == 0:
                print counter

        if counter != 1:
                m = re.search(pattern, line)

                courseName = m.group(7).lower()
                yearOfBirth = 0
                try:
                        yearOfBirth = int(m.group(8))
                except ValueError:
                        yearOfBirth = 0
                
                        
                #exclude courses named white or yellow.
                #exclude young runners if year of birth date is CLEAR. 0 etc. will be accepted
                if not (courseName == 'white' or courseName == 'yellow' or CURRENT_YEAR - yearOfBirth < 16):
                        race = (m.group(1), m.group(2))
                        person = int(m.group(3))
                        time = 3600 * int(m.group(4)) + 60 * int(m.group(5)) + int(m.group(6))
                        
                        participants.append(person)

                        #store races as a dictionary with
                        #key=(eday, course_num) tuple
                        #value=[(person, that person's time in this race)] list of tuples
                        if not race in races:
                                races[race] = [(person, time)]
                        else:
                                races[race].append((person,time))
                
	
print 'processing done. Total number of entries: ', counter


participantsSet = set(participants)
people = {}

for p in participantsSet:
        if not p in people: #duplicates won't be added, this is just for paranoia of mis-sampling the gaussian
##                rank = 1000
                rank = rand.gauss(1000, 200)
                people[p] = [rank, 0]

print "number of people registered: ", len(people)

raceCounter = 0

print "processing race results..."
for repeat in range(1, 20):
        print repeat
        for race,times in races.iteritems():
                results = []
                for runner in times:
                        if (runner[1] > 0): #ignore RT that are zero
                                person = people[runner[0]]
                                results.append([runner[0], person[0], runner[1]]) #id, prevRank, RT

                if len(results) > 10: #ignore events where less than 10 people participated
                        raceCounter += 1
                        if (raceCounter % 1000 == 0):
                                print raceCounter

                        initMean = numpy.mean([x[2] for x in results])
                        initStd = numpy.std([x[2] for x in results])


                #recalculate mean based only on reasonable scores

                        
##                        MP = 0.0
##                        MT = 0.0
##                        total = 0
##                        for j in results:
##                                if abs(j[2] - initMean) < stdCutoff*initStd:
##                                        MP = MP + j[1]
##                                        MT = MT + j[2]
##                                        total += 1
##                                #else:
##                                        #print "racer and time", j[0], j[2]
##
##                        MP = MP / total
##                        MT = MT / total
##
##                        divMP = 0.0
##                        divMT = 0.0
##
##                        for j in results:
##                                if abs(j[2] - initMean) < stdCutoff*initStd:
##                                        divMP = divMP + (j[1] - MP)**2
##                                        divMT = divMT + (j[2] - MT)**2
##
##                        SP = (divMP / total)**(0.5)
##                        ST = (divMT / total)**(0.5)


                #throw out unreasonable results completely

                        results = [r for r in results if abs(r[2] - initMean) < stdCutoff*initStd]
                        MP = 0.0
                        MT = 0.0
                        total = 0
                        for j in results:
                                MP = MP + j[1]
                                MT = MT + j[2]
                                total += 1
                                #else:
                                        #print "racer and time", j[0], j[2]

                        MP = MP / total
                        MT = MT / total

                        divMP = 0.0
                        divMT = 0.0

                        for j in results:
                                divMP = divMP + (j[1] - MP)**2
                                divMT = divMT + (j[2] - MT)**2

                        SP = (divMP / total)**(0.5)
                        ST = (divMT / total)**(0.5)
                        
                        
                                        

                        #needed if all start from the same score (not so nice)
                        if SP == 0:
                                SP = 200

                        differences[:] = []
                        #calculate scores and update mean scores of runners
                        for res in results:
                                ID = res[0]
                                currRaceCount = people[ID][1]

                                RP = MP + SP * (MT - res[2]) / ST
                        
                                if RP < 0:
                                        RP = 0

                                #the first "real" score overrides the generated one
                                if (currRaceCount == 0): #CHECK for correctness
                                        newScore = RP
                                else:
                                        newScore = (currRaceCount * people[ID][0] + RP) / (currRaceCount + 1)

                                differences.append(abs(newScore - people[ID][0]))
                                people[ID][0] = newScore
                                people[ID][1] += 1

                        maxDif = max(differences)
                        maxDifferences.append(maxDif)
                        
                        if maxDif < 0.001:
                                break
                                
                                
        means.append(numpy.mean([v[0] for k,v in people.iteritems() if v[1] > 0]))
        divs.append(numpy.std([v[0] for k,v in people.iteritems() if v[1] > 0]))



finalRanks = [v[0] for k,v in people.iteritems() if v[1] > 0] #if v[1] > 5
print "final number of people that participated in 1 or more races: ", len(finalRanks)
print "number of races with more than 10 runners: ", raceCounter

mean = numpy.mean([v[0] for k,v in people.iteritems() if v[1] > 0])
sdDiv = numpy.std([v[0] for k,v in people.iteritems() if v[1] > 0])

plt.hist(finalRanks, bins=100, normed=False, histtype='stepfilled', color='r', label='final', alpha = 0.5)
plt.axvline(x=mean, color='black')
plt.title("Rank Histogram")
plt.xlabel("Rank")
plt.ylabel("Frequency")
plt.figtext(0.15, 0.85, str(round(mean, 3)) + '(' + str(round(sdDiv, 3)) + ')')
plt.legend()
plt.show()

