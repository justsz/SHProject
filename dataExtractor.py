#!/usr/bin/python

import fileinput
import re
import matplotlib.pyplot as plt
import numpy
import random
rand = random.Random(456)


#sample data
#res_eday,res_course_num,res_bof_num,res_time
#60575,5,113948,00:12:00

races = {}
participants = []

filename = "reducedData.csv"
pattern = '(\d+),(.*),(\d+),(\d+):(\d\d):(\d\d)'
counter = 0

target = 0
take = True

print 'beginning to read file'
for line in fileinput.input([filename]):
        counter += 1
        if (counter % 10000) == 0:
                print counter

        if counter != 1:
                m = re.search(pattern, line)
                race = (m.group(1), m.group(2))
                person = int(m.group(3))
                time = 3600 * int(m.group(4)) + 60 * int(m.group(5)) + int(m.group(6))
                
                participants.append(person)

                if not race in races:
                        races[race] = [(person, time)]
                else:
                        races[race].append((person,time))
                
	
print 'processing done. Total number of entries: ', counter


participantsSet = set(participants)
people = {}

for p in participantsSet:
##        rank = 1000
        rank = rand.gauss(1000, 200)
        people[p] = [rank, 0]

print "number of people registered: ", len(people)

raceCounter = 0

for repeat in range(0, 1):
        print repeat
        for k,v in races.iteritems():
                results = []
                for r in v:
                        if (r[1] > 0): #ignore RT that are zero
                                person = people[r[0]]
                                results.append([r[0], person[0], r[1]]) #id, prevScore, RT
                                person[1] += 1

                if len(results) > 10:
                        raceCounter += 1
                        results = sorted(results, key=lambda x: x[2]) #rank by run times: quick -> slow

                        top90 = int(len(results)*1.0)
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

                        #needed if all start from the same score (not so nice)
                        if SP == 0:
                                SP = 200

                        #calculate scores and update mean scores of runners
                        for res in results:
                                

                                
                                ID = res[0]
                                if take:
                                        target = ID
                                        take = False
                                        print people[target][0]
                                RP = MP + SP * (MT - res[2]) / ST
                        
                                if RP < 0:
                                        RP = 0

                                currRaceCount = people[ID][1]

                                if (currRaceCount == 1): #CHECK for correctness
                                        people[ID][0] = RP
                                        people[ID][1] += -1
                                else:
                                        people[ID][0] = (currRaceCount * people[ID][0] + RP) / (currRaceCount + 1)
                                if ID == target:
                                        print people[ID][0]
                                



finalRanks = [v[0] for k,v in people.iteritems()] #if v[1] > 5
print "final number of people that participated in 6 or more races: ", len(finalRanks)
print "number of races with more than 10 runners: ", raceCounter

mean = numpy.mean([v[0] for k,v in people.iteritems()])
sdDiv = numpy.std([v[0] for k,v in people.iteritems()])

plt.hist(finalRanks, bins=100, normed=True, histtype='stepfilled', color='r', label='final', alpha = 0.5)
plt.axvline(x=mean, color='black')
plt.title("Rank Histogram")
plt.xlabel("Rank")
plt.ylabel("Frequency")
plt.figtext(0.15, 0.85, str(round(mean, 3)) + '(' + str(round(sdDiv, 3)) + ')')
plt.legend()
plt.show()

