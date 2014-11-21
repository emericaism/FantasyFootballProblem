import csv
import glob
import os
import itertools
import random
import datetime


def randomTeam(qbs,rbs,wrs,tes,dsts):
	isLegal = False
	while not isLegal:
		team = [random.choice(qbs)]
		team.extend(random.sample(rbs,2))
		team.extend(random.sample(wrs,3))
		team.append(random.choice(tes))
		flexes = rbs+wrs+tes
		while True:
			flexChoice = random.choice(flexes)
			if not flexChoice in team:
				break
		team.append(flexChoice)
		team.append(random.choice(dsts))
		teamSalary = 0
		teamSalary = computeTeamSalary(team)
		if teamSalary<=50000:
			isLegal=True

	return team


def importCSVsToBigList():
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
					playerData=[row[0],row[10],float(row[11]),float(row[12]),int(row[13][1:])]
					players.append(playerData)

				if playerPage == "qbs-Table 1.csv":
					#[name,CI,numberFire FP, DK FP, Salary]
					if float(row[14])<3:
						continue
					playerData=[row[0],row[13],float(row[14]),float(row[15]),int(row[16][1:])]
					players.append(playerData)

				if playerPage == "rbs-Table 1.csv":
					#[name,CI,numberFire FP, DK FP, Salary]
					if float(row[13])<4:
						continue
					playerData=[row[0],row[12],float(row[13]),float(row[14]),int(row[15][1:])]
					players.append(playerData)

				if playerPage == "wrs-Table 1.csv":
					#[name,CI,numberFire FP, DK FP, Salary]
					if float(row[13])<4:
						continue
					playerData=[row[0],row[12],float(row[13]),float(row[14]),int(row[15][1:])]
					players.append(playerData)

				if playerPage == "tes-Table 1.csv":
					#[name,CI,numberFire FP, DK FP, Salary]
					if float(row[13])<3:
						continue
					playerData=[row[0],row[12],float(row[13]),float(row[14]),int(row[15][1:])]
					#print playerData
					#print playerData[4]
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

	return qbs,rbs,wrs,tes,dsts


#[QB,RB,RB,WR,WR,WR,TE,FLEX,DST]

def computeTeamPoints(team):
	fpp = 0
	for player in team:
		fpp += player[3]
	return fpp

def computeTeamSalary(team):
	teamSalary = 0
	for player in team:
		teamSalary+=player[4]
	return teamSalary

def evaluateNtimes(qbs,rbs,wrs,tes,dsts):
	bestTeam = randomTeam(qbs,rbs,wrs,tes,dsts)
	bestPoints = computeTeamPoints(bestTeam)
	betterExists = True
	for i in xrange(10000000):
		newTeam = randomTeam(qbs,rbs,wrs,tes,dsts)
		newTeamPoints = computeTeamPoints(newTeam)
		if newTeamPoints > bestPoints:
			bestTeam = newTeam
			bestPoints = newTeamPoints
	return bestTeam,computeTeamSalary(bestTeam),computeTeamPoints(bestTeam)

def greedy(qbs,rbs,wrs,tes,dsts):
	bestTeam = randomTeam(qbs,rbs,wrs,tes,dsts)
	bestPoints = computeTeamPoints(bestTeam)
	betterExists = True
	for i in xrange(10000000):
		newTeam = randomTeam(qbs,rbs,wrs,tes,dsts)
		newTeamPoints = computeTeamPoints(newTeam)
		if newTeamPoints > bestPoints:
			bestTeam = newTeam
			bestPoints = newTeamPoints
	return bestTeam,computeTeamSalary(bestTeam),computeTeamPoints(bestTeam)



def main():
	qbs,rbs,wrs,tes,dsts = importCSVsToBigList()
	#print len(qbs),len(rbs),len(wrs),len(tes),len(dsts)
	#print len(qbs)*len(rbs)*(len(rbs)-1)*len(wrs)*(len(wrs)-1)*(len(wrs)-2)*(len(wrs)+len(rbs)+len(tes)-6)*len(tes)*len(dsts)
	print evaluateNtimes(qbs,rbs,wrs,tes,dsts)

print datetime.datetime.utcnow()
main()
print datetime.datetime.utcnow()





