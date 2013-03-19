"""Useful functions for the orienteering data analysis scripts."""
import fileinput
import re
import numpy
import random


CURRENT_YEAR = 2013
MIN_RACE_COUNT = 10
RAND = random.Random(456)


def processFile (filename, pattern):
    """Reads file and processes data into a usable form."""
    #sample data
    #res_eday,res_course_num,res_bof_num,res_time, course_name, res_yob
    #60575,5,113948,00:12:00, White, 1990
    
    racesDict = {}
    participants = []
    
    print 'beginning to read file'
    counter = 0
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
                            if time > 0:
                                    if not race in racesDict:
                                            racesDict[race] = [(person, time)]
                                    else:
                                            racesDict[race].append((person,time))
    print 'processing done. Total number of entries: ', counter

    #convert the dictionary of races into a list for easier manipulation
    #also, sort each race's (participant, time) tuple list in order quickes -> slowest
    races = [sorted(v, key=lambda x: x[1]) for k,v in racesDict.iteritems() if len(v) >= MIN_RACE_COUNT]

    #remove duplicate participants
    participantList = set(participants)

    return (races, participantList)



def initializeScores (initType, keepHistory, keepGeneratedScore, mean, std, participants):
    """General functin for score initialization."""
    people = {}
    
    for p in participants:
        rank = -1
        if initType == 'constant':
            rank = mean
        elif initType == 'normal':
            rank = RAND.gauss(mean, std)
        else:
            print "Undefined initialization type. Exiting."
            exit()

        if keepHistory:
            if keepGeneratedScore:
                people[p] = [rank, 1, [rank]]
            else:
                people[p] = [rank, 0, []]
        else:
            if keepGeneratedScore:
                people[p] = [rank, 1]
            else:
                people[p] = [rank, 0]

    return people



def getResults (race, people):
    results = []
    for runner in race:
        results.append([people[runner[0]], runner[1]]) #id, prevRank, RT
    return results



def shuffle (races):
    RAND.shuffle(races)



def cropResultsAndCalcMeansAndStds (results, cropType, cropLimit, givePointsToCropped, minSP):
    MP = 0.0
    MT = 0.0
    SP = 0.0
    ST = 0.0
    divMP = 0.0
    divMT = 0.0
    
    if (cropType == 'normal'):
        initMean = numpy.mean([x[1] for x in results])
        initStd = numpy.std([x[1] for x in results])
        maxDeviation = cropLimit*initStd

        if givePointsToCropped:
            total = 0
            for j in results:
                if abs(j[1] - initMean) < maxDeviation:
                    MP = MP + j[0][0]
                    MT = MT + j[1]
                    total += 1

            MP = MP / total
            MT = MT / total

            for j in results:
                if abs(j[1] - initMean) < maxDeviation:
                    divMP = divMP + (j[0][0] - MP)**2
                    divMT = divMT + (j[1] - MT)**2

            SP = (divMP / total)**(0.5)
            ST = (divMT / total)**(0.5)
                
        else:
            results[:] = [r for r in results if abs(r[1] - initMean) < maxDeviation]
            
            total = 0
            for j in results:
                MP = MP + j[0][0]
                MT = MT + j[1]
                total += 1

            MP = MP / total
            MT = MT / total

            for j in results:
                divMP = divMP + (j[0][0] - MP)**2
                divMT = divMT + (j[1] - MT)**2

            SP = (divMP / total)**(0.5)
            ST = (divMT / total)**(0.5)

    elif (cropType == 'slowestPercent'):
        top = int(len(results)*cropLimit)
        if not givePointsToCropped:
            results[:] = results[:top]

        for j in range(0, top):
                MP = MP + results[j][0][0]
                MT = MT + results[j][1]

        MP = MP / top
        MT = MT / top

        for j in range(0, top):
                divMP = divMP + (results[j][0][0] - MP)**2
                divMT = divMT + (results[j][1] - MT)**2

        SP = (divMP / top)**(0.5)
        ST = (divMT / top)**(0.5)



    #if SP == 0:
    #    SP = 200
    if SP < minSP:
        SP = minSP
        
    return [MP, SP, MT, ST]



def updateRunnerScores (results, meansAndStds, people, keepHistory):
    for res in results:
        #RP = MP + SP * (MT - runnerTime) / ST
        RP = meansAndStds[0] + meansAndStds[1] * (meansAndStds[2] - res[1]) / meansAndStds[3]

        if RP < 0:
            RP = 0


        currRaceCount = res[0][1]
        res[0][0] = (currRaceCount * res[0][0] + RP) / (currRaceCount + 1)
        res[0][1] += 1

        if keepHistory:
            res[0][2].append(RP)



def dropIntermediateScores (people, keepHistory, keepGeneratedScore):
    if keepHistory:
        for k,v in people.iteritems():
            if keepGeneratedScore:
                v[1] = 1
                v[2] = [v[0]]
            else:
                v[1] = 0
                v[2] = []
    else:
        for k,v in people.iteritems():
            if keepGeneratedScore:
                v[1] = 1
            else:
                v[1] = 0



def getMeanAndStdOfScores (people, keepHistory, minRaceCount, dropIntermediateScores, run):
    minRC = minRaceCount
    if not dropIntermediateScores:
        minRC *= run
    
    mean = -1
    std = -1
    if keepHistory:
        mean = numpy.mean([v[0] for k,v in people.iteritems() if v[1] >= minRC])
        std = numpy.std([v[0] for k,v in people.iteritems() if v[1] >= minRC])
    else:
        mean = numpy.mean([v[0] for k,v in people.iteritems() if v[1] >= minRC])
        std = numpy.std([v[0] for k,v in people.iteritems() if v[1] >= minRC])

    print "mean of scores", mean
    print "std of scores", std

    return mean, std



def getIndividualMeansAndStds (people, keepHistory, minRaceCount, dropIntermediateScores, run):
    minRC = minRaceCount
    if not dropIntermediateScores:
        minRC *= run
        
    if keepHistory:
        means = [numpy.mean(v[2]) for k,v in people.iteritems() if v[1] >= minRC]
        stds = [numpy.std(v[2]) for k,v in people.iteritems() if v[1] >= minRC]
        return means, stds
    else:
        means = [v[0] for k,v in people.iteritems() if v[1] >= minRC]
        return means, [-1]



def rebaseScores (people, newMean, newStd, minRaceCount): 
    allScoresStd = numpy.std([v[0] for k,v in people.iteritems() if v[1] > minRaceCount])
    allScoresMean = numpy.mean([v[0] for k,v in people.iteritems() if v[1] > minRaceCount])
    for k,v in people.iteritems():
        v[0] = (v[0] - allScoresMean) * newStd / allScoresStd + newMean
    

      



























        
