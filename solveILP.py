import csv
import glob
import os
import itertools
import random
import datetime
import cPickle as pickle


class FantasyFootball:
	def __init__(self):
		self.qbs = []
		self.rbs = []
		self.wrs = []
		self.tes = []
		self.dsts = []
		self.flexes = []
		self.bestTeam = []
		self.bestPoints = 0
		self.top5 = []
		self.top5Pts = []

		self.salaryBound = 49700
		self.objective=3 #3 maximizes DK Points, 2 maximizes NF Points

		self.ThursdayTeams = ['CHI','DET','PHI','DAL','SEA','SF']
		self.MondayTeams = ['MIA','NYJ']


		if self.objective==3:
			self.objectiveName = "DK"
		elif self.objective==2:
			self.objectiveName="NF"

		self.importCSVsToBigList()

		#self.useCurtailedPlayerLists()
		#self.importTeam()
		self.ThursdayOnly()
		self.createTop5()
		self.evaluateNtimesTop5(1000000)
		#self.greedy()
		#self.makeCombinations()
		#print len(self.qbs),len(self.rbs),len(self.wrs),len(self.tes),len(self.dsts)
		#print len(self.qbs)*len(self.rbs)**2*len(self.wrs)**3*len(self.tes)*len(self.flexes)*len(self.dsts)

	def ThursdayOnly(self):
		self.qbs = [x for x in self.qbs if (x[5] in self.ThursdayTeams)]
		self.rbs = [x for x in self.rbs if (x[5] in self.ThursdayTeams)]
		self.wrs = [x for x in self.wrs if (x[5] in self.ThursdayTeams)]
		self.tes = [x for x in self.tes if (x[5] in self.ThursdayTeams)]
		self.dsts = [x for x in self.dsts if (x[5] in self.ThursdayTeams)]
		self.flexes = self.rbs+self.wrs+self.tes

	def SundayOnly(self):
		self.qbs = [x for x in self.qbs if not (x[5] in self.ThursdayTeams or x[5] in self.MondayTeams)]
		self.rbs = [x for x in self.rbs if not (x[5] in self.ThursdayTeams or x[5] in self.MondayTeams)]
		self.wrs = [x for x in self.wrs if not (x[5] in self.ThursdayTeams or x[5] in self.MondayTeams)]
		self.tes = [x for x in self.tes if not (x[5] in self.ThursdayTeams or x[5] in self.MondayTeams)]
		self.dsts = [x for x in self.dsts if not (x[5] in self.ThursdayTeams or x[5] in self.MondayTeams)]
		self.flexes = self.rbs+self.wrs+self.tes

	def MondayOnly(self):
		self.qbs = [x for x in self.qbs if (x[5] in self.MondayTeams)]
		self.rbs = [x for x in self.rbs if (x[5] in self.MondayTeams)]
		self.wrs = [x for x in self.wrs if (x[5] in self.MondayTeams)]
		self.tes = [x for x in self.tes if (x[5] in self.MondayTeams)]
		self.dsts = [x for x in self.dsts if (x[5] in self.MondayTeams)]
		self.flexes = self.rbs+self.wrs+self.tes

	def SundayMondayOnly(self):
		self.qbs = [x for x in self.qbs if not (x[5] in self.ThursdayTeams)]
		self.rbs = [x for x in self.rbs if not (x[5] in self.ThursdayTeams)]
		self.wrs = [x for x in self.wrs if not (x[5] in self.ThursdayTeams)]
		self.tes = [x for x in self.tes if not (x[5] in self.ThursdayTeams)]
		self.dsts = [x for x in self.dsts if not (x[5] in self.ThursdayTeams)]
		self.flexes = self.rbs+self.wrs+self.tes


	def createTop5(self):
		for i in xrange(5):
			self.top5.append(self.randomTeam())
		for team in self.top5:
			self.top5Pts.append(self.computeTeamPoints(team))

		X = self.top5
		Y = self.top5Pts

		self.top5 = [x for (y,x) in sorted(zip(Y,X))]

		del self.top5Pts[:]

		for team in self.top5:
			self.top5Pts.append(self.computeTeamPoints(team))

	def compareWithTop5andUpdate(self,team):
		betterThanIndex = -1
		tp = self.computeTeamPoints(team)
		for i in range(len(self.top5)):
			if tp>self.top5Pts[i]:
				betterThanIndex = i
		if not betterThanIndex==-1:
			self.top5.insert(betterThanIndex+1,team)
			self.top5.pop(0)
			self.top5Pts[i] = tp


	def importTeam(self):
		os.chdir("..")
		self.bestTeam = pickle.load(open("best"+self.objectiveName+".p","rb"))

	def useCurtailedPlayerLists(self):
		self.qbs = self.qbs[10:15]
		self.rbs = self.rbs[10:16]
		self.wrs = self.wrs[10:16]
		self.tes = self.tes[10:15]
		self.dsts = self.dsts[10:15]
		self.flexes = self.rbs+self.rbs+self.tes


	def randomTeam(self):
		isLegal = False
		while not isLegal:
			team = [random.choice(self.qbs)]
			team.extend(random.sample(self.rbs,2))
			team.extend(random.sample(self.wrs,3))
			team.append(random.choice(self.tes))
			flexes = self.rbs+self.wrs+self.tes
			while True:
				flexChoice = random.choice(self.flexes)
				if not flexChoice in team:
					break
			team.append(flexChoice)
			team.append(random.choice(self.dsts))
			teamSalary = self.computeTeamSalary(team)
			if teamSalary<=50000 and teamSalary>=self.salaryBound:
				isLegal=True


		#print team,self.computeTeamPoints(team),self.computeTeamSalary(team)
		return team


	def importCSVsToBigList(self):
		curr = os.getcwd()
		os.chdir(curr+"/week13/")
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
						if float(row[11])<7:
							continue
						playerData=[row[0],row[10],float(row[11]),float(row[12]),int(row[13][1:]),row[2]]
						players.append(playerData)

					if playerPage == "qbs-Table 1.csv":
						#[name,CI,numberFire FP, DK FP, Salary]
						if float(row[14])<12:
							continue
						playerData=[row[0],row[13],float(row[14]),float(row[15]),int(row[16][1:]),row[2]]
						players.append(playerData)

					if playerPage == "rbs-Table 1.csv":
						#[name,CI,numberFire FP, DK FP, Salary]
						if float(row[13])<8:
							continue
						playerData=[row[0],row[12],float(row[13]),float(row[14]),int(row[15][1:]),row[2]]
						players.append(playerData)

					if playerPage == "wrs-Table 1.csv":
						#[name,CI,numberFire FP, DK FP, Salary]
						if float(row[13])<8:
							continue
						playerData=[row[0],row[12],float(row[13]),float(row[14]),int(row[15][1:]),row[2]]
						players.append(playerData)

					if playerPage == "tes-Table 1.csv":
						#[name,CI,numberFire FP, DK FP, Salary]
						if float(row[13])<5:
							continue
						playerData=[row[0],row[12],float(row[13]),float(row[14]),int(row[15][1:]),row[2]]
						#print playerData
						#print playerData[4]
						players.append(playerData)

					rowCount+=1

		for player in players:
			if "(QB" in player[0]:
				self.qbs.append(player)
			elif "(RB" in player[0]:
				self.rbs.append(player)
			elif "(WR" in player[0]:
				self.wrs.append(player)
			elif "(TE" in player[0]:
				self.tes.append(player)
			elif "D/ST" in player[0]:
				self.dsts.append(player)
		self.flexes = self.rbs+self.wrs+self.tes

		for playerList in [self.qbs,self.rbs,self.wrs,self.tes]:
			for p in playerList:
				p[0] = p[0][1:-4]
				if p[1][0]=='-':
					p[1]=p[1][1:]
				ciList = [float(x) for x in p[1].split('-')]
				p[1] = ciList

		for dst in self.dsts:
			dst[0] = dst[0][1:-8]
			if not dst[1][0] == '-':
				ciList = [float(x) for x in dst[1].split('-')]
			else:
				ciList = [float(x) for x in dst[1][1:].split('-')]
				ciList[0] = -1*ciList[0]
			dst[1] = ciList


		return None

	def makeCombinations(self):
		lengths = [len(self.qbs),len(self.rbs),len(self.wrs),len(self.tes),len(self.dsts)]
		#some_list = [xrange(len(self.qbs)),xrange(len(self.rbs)),xrange(len(self.rbs)),
		#	xrange(len(self.wrs)),xrange(len(self.wrs)),xrange(len(self.wrs)),
		#	xrange(len(self.tes)),xrange(len(self.flexes)),xrange(len(self.dsts))]
		some_list = [self.qbs[:5],self.rbs[:5],self.rbs[:5],self.wrs[:5],self.wrs[:5],self.wrs[:5],self.tes[:5],self.flexes[:5],self.dsts[:5]]
		bigfcking = itertools.product(*some_list)
		bigfckinglist = []
		for e in bigfcking:
			bigfckinglist.append(e)
		#print bigfuckinglist
		print len(bigfckinglist)
		pickle.dump(bigfckinglist,open("combos.p","wb"))

	#[QB,RB,RB,WR,WR,WR,TE,FLEX,DST]

	def computeTeamPoints(self,team):
		fpp = 0
		for player in team:
			fpp += player[self.objective]
		return fpp

	def computeDKPoints(self,team):
		fpp = 0
		for player in team:
			fpp+=player[3]
		return fpp
	
	def computeNFPoints(self,team):
		fpp = 0
		for player in team:
			fpp+=player[2]
		return fpp


	def computeTeamSalary(self,team):
		teamSalary = 0
		for player in team:
			teamSalary+=player[4]
		return teamSalary

	def computeTeamVariance(self,team):
		teamVar = 0
		for player in team:
			ci = player[1]
			midpt = sum(ci) / float(len(ci))
			var = ci[1]-midpt/1.96
			teamVar+=var

		return teamVar

	def evaluateNtimes(self,N):
		self.bestTeam = self.randomTeam()
		self.bestPoints = self.computeTeamPoints(self.bestTeam)
		betterExists = True
		for i in xrange(N):
			if i%100000==0:
				print "Iteration: ",i
				print "Maximize ", self.objectiveName
				print "Team",self.bestTeam
				print "NFPoints",self.computeNFPoints(self.bestTeam)
				print "DKPoints",self.computeDKPoints(self.bestTeam)
				print "TeamVar",self.computeTeamVariance(self.bestTeam)
				print "$",self.computeTeamSalary(self.bestTeam)
			newTeam = self.randomTeam()
			newTeamPoints = self.computeTeamPoints(newTeam)
			if newTeamPoints > self.bestPoints:
				self.bestTeam = newTeam
				self.bestPoints = newTeamPoints
		print "Maximize ", self.objectiveName
		print "Team",self.bestTeam
		print "NFPoints",self.computeNFPoints(self.bestTeam)
		print "DKPoints",self.computeDKPoints(self.bestTeam)
		print "TeamVar",self.computeTeamVariance(self.bestTeam)
		print "$",self.computeTeamSalary(self.bestTeam)
		pickle.dump(self.bestTeam,open("best"+self.objectiveName+".p","wb"))
		return self.bestTeam,self.computeTeamSalary(self.bestTeam),self.computeTeamPoints(self.bestTeam)

	def evaluateNtimesTop5(self,N):
		#self.bestTeam = self.randomTeam()
		#self.bestPoints = self.computeTeamPoints(self.bestTeam)
		#betterExists = True
		for i in xrange(N):
			if i%100000==0:
				for topTeam in self.top5:
					print "Iteration: ",i
					print "Maximize ", self.objectiveName
					print "Team",topTeam
					print "NFPoints",self.computeNFPoints(topTeam)
					print "DKPoints",self.computeDKPoints(topTeam)
					print "TeamVar",self.computeTeamVariance(topTeam)
					print "$",self.computeTeamSalary(topTeam)
			newTeam = self.randomTeam()
			self.compareWithTop5andUpdate(newTeam)
		for topTeam in self.top5:
			print "Iteration: ",i
			print "Maximize ", self.objectiveName
			print "Team",topTeam
			print "NFPoints",self.computeNFPoints(topTeam)
			print "DKPoints",self.computeDKPoints(topTeam)
			print "TeamVar",self.computeTeamVariance(topTeam)
			print "$",self.computeTeamSalary(topTeam)
		pickle.dump(self.top5,open("best"+self.objectiveName+".p","wb"))

	def searchParetoImprovement(self,team):
		while True:
			qb = team[0]
			ts = self.computeTeamSalary(team)
			for qbnew in self.qbs:
				if qbnew!=qb:
					if qbnew[self.objective]>=qb[self.objective]:
						if qbnew[4]<=qb[4]+(50000-ts):
							team[0] = qbnew
							continue
		return team
	def greedy(self):
		self.bestTeam = self.randomTeam()
		print self.bestTeam
		self.bestPoints = self.computeTeamPoints(self.bestTeam)
		betterExists = True

		while betterExists:
			print "iter"

			couldntFindAnything = True

			for qb in self.qbs:
				if qb==self.bestTeam[0]:
					continue
				else:
					newTeam = self.bestTeam
					newTeam[0]=qb
					ts = self.computeTeamSalary(newTeam)
					if ts<=50000:
						if self.computeTeamPoints(newTeam)>self.bestPoints:
							self.bestTeam=newTeam
							self.bestPoints = self.computeTeamPoints(newTeam)
							couldntFindAnything=False
							print "new qb",qb
							continue

			for rb in self.rbs:
				if rb in [self.bestTeam[1],self.bestTeam[2]]:
					continue
				else:
					newTeam = self.bestTeam
					newTeam[1]=rb
					ts = self.computeTeamSalary(newTeam)
					if ts<=50000:
						if self.computeTeamPoints(newTeam)>self.bestPoints:
							self.bestTeam=newTeam
							self.bestPoints = self.computeTeamPoints(newTeam)
							couldntFindAnything=False
							print "new rb",rb
							continue

			for rb in self.rbs:
				if rb in [self.bestTeam[1],self.bestTeam[2]]:
					continue
				else:
					newTeam = self.bestTeam
					newTeam[2]=rb
					ts = self.computeTeamSalary(newTeam)
					if ts<=50000:
						if self.computeTeamPoints(newTeam)>self.bestPoints:
							self.bestTeam=newTeam
							self.bestPoints = self.computeTeamPoints(newTeam)
							couldntFindAnything=False
							print "new rb",rb
							continue

			for wr in self.wrs:
				if wr in [self.bestTeam[3],self.bestTeam[4],self.bestTeam[5]]:
					continue
				else:
					newTeam = self.bestTeam
					newTeam[3]=wr
					ts = self.computeTeamSalary(newTeam)
					if ts<=50000:
						if self.computeTeamPoints(newTeam)>self.bestPoints:
							self.bestTeam=newTeam
							self.bestPoints = self.computeTeamPoints(newTeam)
							couldntFindAnything=False
							print "new wr",wr
							continue

			for wr in self.wrs:
				if wr in [self.bestTeam[3],self.bestTeam[4],self.bestTeam[5]]:
					continue
				else:
					newTeam = self.bestTeam
					newTeam[4]=wr
					ts = self.computeTeamSalary(newTeam)
					if ts<=50000:
						if self.computeTeamPoints(newTeam)>self.bestPoints:
							self.bestTeam=newTeam
							self.bestPoints = self.computeTeamPoints(newTeam)
							couldntFindAnything=False
							print "new wr",wr
							continue

			for wr in self.wrs:
				if wr in [self.bestTeam[3],self.bestTeam[4],self.bestTeam[5]]:
					continue
				else:
					newTeam = self.bestTeam
					newTeam[5]=wr
					ts = self.computeTeamSalary(newTeam)
					if ts<=50000:
						if self.computeTeamPoints(newTeam)>self.bestPoints:
							self.bestTeam=newTeam
							self.bestPoints = self.computeTeamPoints(newTeam)
							couldntFindAnything=False
							print "new wr",wr
							continue

			for te in self.tes:
				if te==self.bestTeam[6]:
					continue
				else:
					newTeam = self.bestTeam
					newTeam[6]=te
					ts = self.computeTeamSalary(newTeam)
					if ts<=50000:
						if self.computeTeamPoints(newTeam)>self.bestPoints:
							self.bestTeam=newTeam
							self.bestPoints = self.computeTeamPoints(newTeam)
							couldntFindAnything=False
							print "new te",te
							continue

			for flex in self.flexes:
				if flex in [self.bestTeam[1],self.bestTeam[2],self.bestTeam[3],self.bestTeam[4],self.bestTeam[5],self.bestTeam[6]]:
					continue
				else:
					newTeam = self.bestTeam
					newTeam[7]=flex
					ts = self.computeTeamSalary(newTeam)
					if ts<=50000:
						if self.computeTeamPoints(newTeam)>self.bestPoints:
							self.bestTeam=newTeam
							self.bestPoints = self.computeTeamPoints(newTeam)
							couldntFindAnything=False
							print "new flex",flex
							continue

			for dst in self.dsts:
				if dst==self.bestTeam[8]:
					continue
				else:
					newTeam = self.bestTeam
					newTeam[8]=dst
					ts = self.computeTeamSalary(newTeam)
					if ts<=50000:
						if self.computeTeamPoints(newTeam)>self.bestPoints:
							self.bestTeam=newTeam
							self.bestPoints = self.computeTeamPoints(newTeam)
							couldntFindAnything=False
							print "new dst",dst
							continue

			if couldntFindAnything:
				betterExists=False

		print "team",self.bestTeam
		print "salary",self.computeTeamSalary(self.bestTeam)
		print "points",self.computeTeamPoints(self.bestTeam)
		return self.bestTeam,self.computeTeamSalary(self.bestTeam),self.computeTeamPoints(self.bestTeam)



	def main(self):
		self.qbs,self.rbs,self.wrs,self.tes,self.dsts = self.importCSVsToBigList()
		#print len(qbs),len(rbs),len(wrs),len(tes),len(dsts)
		#print len(qbs)*len(rbs)*(len(rbs)-1)*len(wrs)*(len(wrs)-1)*(len(wrs)-2)*(len(wrs)+len(rbs)+len(tes)-6)*len(tes)*len(dsts)
		print self.evaluateNtimes(qbs,rbs,wrs,tes,dsts)

print datetime.datetime.utcnow()
x = FantasyFootball()
print datetime.datetime.utcnow()





