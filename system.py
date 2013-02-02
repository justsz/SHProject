#!/usr/bin/python
import random

N = 1000
n = 100
races = 100000

people = []
rand1 = random.Random(456)
rand2 = random.Random(456)

rand2.jumpahead(999)

#initialize scores
for i in range(0, N):
    people.append([i, rand1.randint(500, 1500)])

print "beginning calculations"
for i in range(1, races):
    if i % 100 == 0:
        print i
    noOfParticipants = rand1.randint(10, n)
    participants = random.sample(xrange(1, N), noOfParticipants)
    MT = rand1.uniform(600, 360000)
    ST = MT / 10

    MP = 0
    for j in range(0, noOfParticipants):
        MP = MP + people[participants[j]][1]

    MP = MP / noOfParticipants

    subSum = 0
    for j in range(0, noOfParticipants):
        subSum = subSum + (people[participants[j]][1] - MP)**2

##    SP = 100
##    if i != 1:
    SP = (subSum / noOfParticipants)**(0.5)

    #generate run times
    for j in range(0, noOfParticipants):
        RT = rand2.gauss(MT, ST)
        RP = MP + SP * (MT - RT) / ST
        
        #print SP * (MT - RT) / ST
        if RP < 0:
            RP = 0
        people[participants[j]][1] = (i * people[participants[j]][1] + RP) / (i + 1)
    
    
print "finished calculations. Final scores:"
##for i in range(0, N):
##    print people[i][1]
    
mean = 0
for j in range(0, N):
    mean = mean + people[j][1]

mean = mean / N

subSum = 0
for j in range(0, N):
    subSum = subSum + (people[j][1] - mean)**2

sdDiv = (subSum / N)**(0.5)

print "races", races
print "mean", mean
print "sdDiv", sdDiv
