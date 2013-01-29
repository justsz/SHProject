#!/usr/bin/python

import fileinput
import re


filename = "orienteering.csv"
pattern = '"\d+","\d+",("\d+")?,("-?\d+")?,".*",(".*")?,("\d+:\d+:\d+")?,".*",(".*")?,("\d+\.?\d*")?,("\d+\.?\d*")?,("\d+")?,"\d+",".*",("\d+")?,(".?")?,("\d+")?'
#pattern = '(".*",)+".*"'
counter = 0

print 'beginning to read file'
for line in fileinput.input([filename]):
	counter += 1
	if (counter % 10000) == 0:
		print counter
		
	if not re.match(pattern, line) and counter != 1:
		print("Error at line " + str(counter) + ": " + line), 
		exit()
	

print 'processing done. Total number of lines: ', counter