import csv
import glob
import os
import random

curr = os.getcwd()
os.chdir(curr+"/week12/")
csvList = glob.glob('*.csv')

players = []

for playerPage in csvList:
	with open(playerPage,'rb') as csvfile:
		reader = csv.reader(csvfile,delimiter=',',quotechar='|',quoting=csv.QUOTE_MINIMAL)
		rowCount = 0
		for row in reader:
			if rowCount < 2:
				rowCount+=1
				continue

			if playerPage == "dsts-Table 1.csv":
				#[name,CI,numberFire FP, DK FP, Salary]
				if float(row[11])<2:
					continue
				playerData=[row[0],row[10],row[11],row[12],row[13]]
				players.append(playerData)

			if playerPage == "qbs-Table 1.csv":
				#[name,CI,numberFire FP, DK FP, Salary]
				if float(row[14])<3:
					continue
				playerData=[row[0],row[13],row[14],row[15],row[16]]
				players.append(playerData)

			if playerPage == "rbs-Table 1.csv":
				#[name,CI,numberFire FP, DK FP, Salary]
				if float(row[13])<4:
					continue
				playerData=[row[0],row[12],row[13],row[14],row[15]]
				players.append(playerData)

			if playerPage == "wrs-Table 1.csv":
				#[name,CI,numberFire FP, DK FP, Salary]
				if float(row[13])<4:
					continue
				playerData=[row[0],row[12],row[13],row[14],row[15]]
				players.append(playerData)

			if playerPage == "tes-Table 1.csv":
				#[name,CI,numberFire FP, DK FP, Salary]
				if float(row[13])<3:
					continue
				playerData=[row[0],row[12],row[13],row[14],row[15]]
				players.append(playerData)

			rowCount+=1

qbs = []
rbs = []
wrs = []
tes = []
dsts = []

for player in players:
	if "(QB" in player[0]:
		qbs.append(player)
	elif "(RB" in player[0]:
		rbs.append(player)
	elif "(WR" in player[0]:
		wrs.append(player)
	elif "(TE" in player[0]:
		tes.append(player)
	elif "D/ST" in player[0]:
		dsts.append(player)

print len(qbs),len(rbs),len(wrs),len(tes),len(dsts)
print len(qbs)*len(rbs)*(len(rbs)-1)*len(wrs)*(len(wrs)-1)*(len(wrs)-2)*(len(wrs)+len(rbs)+len(tes)-6)*len(tes)*len(dsts)






print random.choice(qbs)