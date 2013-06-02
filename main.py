import pygame, random, Effects, sys, Units, Globals, Battle, Abilities
from pygame.locals import *
from Effects import effects
from Globals import *
#Created and Developed by Jeremy Prevoe
pygame.init()
surface = pygame.display.set_mode(CONST["SCREENSIZE"], pygame.FULLSCREEN)
surface.fill([0] * 3)
pygame.display.update()

class BoxedMon:
	def __init__(self, unit, xp, nature, selectedAbils = [0, 1, 2, 3]):
		self.pos = [CONST["BOXLOCATION"][0], CONST["BOXLOCATION"][1]]
		a = random.uniform(0, math.pi * 2)
		d = random.uniform(20, CONST["BOXSIZE"])
		self.pos = [self.pos[0] + math.cos(a) * d, self.pos[1] + math.sin(a) * d]
		self.target = self.pos
		self.speed = 2
		self.frame = 0
		
		self.xp = xp
		self.level = 0
		self.levCounter = 0
		self.calcLevel()
		self.lastLevel = self.level
				
		self.nature = nature

		self.unit = unit
		self.immobilized = False
		self.selectedAbils = selectedAbils
		
	def randomizeNature(self):
		if type(self.nature) != [] or len(self.nature) != 2:
			if type(self.nature) != []:
				self.nature = ["-", "-"]
			elif len(self.nature) != 2:
				self.nature = ["-", "-"]
				
		list = ["OFF", "DEF", "CON", "STA", "SPE"]
		if self.nature[0] not in list:
			if self.nature[1] in list:
				list.remove(self.nature[1])
			self.nature[0] = randFromList(list)
		list = ["OFF", "DEF", "CON", "STA", "SPE"].remove(self.nature[0])
		if self.nature[1] not in list:
			self.nature[1] = randFromList(list)
		
	def calcLevel(self):
		self.xp = max(self.xp, 0)
		self.level = int(math.sqrt(self.xp * 2 / 2.0))
		
	def isEgg(self):
		if self.unit:
			return self.unit[len(self.unit) - 1] == "0"
		return False
		
	def giveXP(self, amt):
		self.xp += amt
		self.calcLevel()
		
	def getXP(self):
		return self.xp
	
	def immobilize(self):
		self.immobilized = True
		
	def loadFromFileLine(self, line):
		print "Loading from File In Line"
		
	def setTarget(self, tPos):
		self.target = [tPos[0], tPos[1]]
		
	def getSelectedAbils(self):
		return self.selectedAbils
		
	def getSaveString(self):
		toRet = " ".join([self.unit, str(int(self.xp)), self.nature[0], self.nature[1]])
		for i in self.selectedAbils:
			toRet += " " + str(i)
		toRet += "\n"
		return toRet
	
	def update(self):
		if self.lastLevel < self.level:
			self.lastLevel = self.level
			self.levCounter = 100
		if self.levCounter > 0:
			self.levCounter -= 1
			
		if self.immobilized:
			self.immobilized = False
			return
			
		d = dist(self.pos, self.target)
		if d <= self.speed:
			self.pos = self.target
			if random.randint(0, 70) <= 1:
				a = random.uniform(0, math.pi * 2)
				d = random.uniform(20, CONST["BOXSIZE"])
				self.target = [CONST["BOXLOCATION"][0] + math.cos(a) * d, 
											 CONST["BOXLOCATION"][1] + math.sin(a) * d]
		else:
			a = math.atan2(self.target[1] - self.pos[1], self.target[0] - self.pos[0])
			self.pos = [self.pos[0] + math.cos(a) * self.speed,
									self.pos[1] + math.sin(a) * self.speed]
		self.frame = (self.frame + 1) % (4 * 5)
									
	def didClickHit(self, clickPos):
		d = dist(clickPos, self.pos)
		if d <= 29 / 2:
			return True
		return False
		
	def getUnit(self):
		return self.unit
		
	def getLevel(self):
		return self.level
	
	def getNature(self):
		if self.nature:
			return [self.nature[0], self.nature[1]]
		return self.nature
		
	def levelledUp(self):
		return self.levCounter > 0
									
	def drawMe(self, surface, drawLevUp = False):
		pygame.draw.circle(surface, [100, 100, 200], intOf(self.pos), 29 / 2, 1)
		cvrt = [0, 1, 2, 1]
		drawUnit(surface, self.pos, self.unit, 1, cvrt[self.frame / 5], drawLevUp = drawLevUp and self.levelledUp())
		
	def modSelectedAbil(self, abilNum):
		abList = UNITABILITIES[self.getUnit()]
		if abilNum in self.selectedAbils:
			self.selectedAbils.remove(abilNum)
		elif abilNum < len(abList) and abList[abilNum][0] <= self.getLevel() and len(self.selectedAbils) <= 3:
			self.selectedAbils += [abilNum]
	
	def drawAbils(self, surface, pos):
		if self.getUnit() not in UNITABILITIES:
			return
		abList = UNITABILITIES[self.getUnit()]
		
		pos = [pos[0], pos[1]]
		i = 0
		while i < len(abList):
			if abList[i][0] <= self.getLevel():
				if abList[i][1] in Abilities.abilList:
					if abList[i][1] in Abilities.drawAbils:
						Abilities.drawAbils[abList[i][1]].drawInfo(surface, pos, i in self.selectedAbils)
					else:
						Abilities.drawAbils[abList[i][1]] = Abilities.abilList[abList[i][1]]()
					
				else:
					print "Error in drawAbils:", abList[i][1], "not in abilList"
				pos[1] += 55
			elif i in self.selectedAbils:
				self.selectedAbils.remove(i)
			i += 1
			
class Profile:
	def __init__(self):
		self.mons = []
		self.boxedMons = []
		
		self.hovering = None
		self.selected = None
		
		self.orderMons = False
		self.saveFile = ""
		
	def checkEvolutions(self, surface, unitsInBattle):
		toEvolve = []
		for i in range(len(self.mons)):
			m = self.mons[i]
			blankyEvolved = False
			if m.getUnit() == "Blanky0" and unitsInBattle and random.random() <= 0.5:
				u = random.randint(0, len(unitsInBattle) - 1)
				if unitsInBattle[u][0] in UNITSTATS and UNITSTATS[unitsInBattle[u][0]]["EGG"] != "None":
					self.tryToEvolve(surface, i, UNITSTATS[unitsInBattle[u][0]]["EGG"])
					blankyEvolved = True
				
			if not blankyEvolved:
				fileIn = open(os.path.join("Data", "UnitStats", "Evolutions.txt"))
				for line in fileIn:
					line = line.strip().split()
					if len(line) >= 4 and line[0].upper() == m.getUnit().upper():
						req = ""
						canEvolve = True
						for token in line:
							if token.upper() in ["NAT", "LEV"]:
								req = token.upper()
							elif req == "LEV" and isInt(token):
								if m.getLevel() < int(token):
									canEvolve = False
							elif req == "NAT" and token.upper() != m.getNature()[0].upper():
								canEvolve = False
						if canEvolve:
							self.tryToEvolve(surface, i, line[1])			
							break
				fileIn.close()
	
	def tryToEvolve(self, surface, arPos, evolution):
		if evolution in UNITSTATS and self.mons[arPos].getUnit() in UNITSTATS:
			_done = False
			timer = 200
			keyPresses = 0
			evolutionAnim = random.randint(0, 1)
			m = self.mons[arPos].getUnit()
			picOld = SPRITES[UNITSTATS[m]["PIC"]][int(UNITSTATS[m]["STATE"])][1]
			picNew = SPRITES[UNITSTATS[evolution]["PIC"]][int(UNITSTATS[evolution]["STATE"])][1]
			p = [CONST["SCREENSIZE"][0] / 2, CONST["SCREENSIZE"][1] / 2]
			while not _done:
				if timer > 0:
					if evolutionAnim == 0:
						surface.blit(picOld, p)
						for i in range(4):
							if random.random() <= 0.5:
								p2 = [p[0] + math.cos(math.pi / 2.0 * i + timer * math.pi / 30.0) * timer / 2, 
											p[1] + math.sin(math.pi / 2.0 * i + timer * math.pi / 30.0) * timer / 2]
								surface.blit(picNew, p2)
					elif evolutionAnim == 1:
						offset = (timer < 180) + (timer < 150) + (timer < 110) - (timer < 40)
						if timer < 100:
							if random.randint(0, 100) > timer:
								surface.blit(picNew, [p[0] + random.randint(-offset, offset), 
																			p[1] + random.randint(-offset, offset)])
							else:
								surface.blit(picOld, [p[0] + random.randint(-offset, offset), 
																			p[1] + random.randint(-offset, offset)])
						else:
							surface.blit(picOld, [p[0] + random.randint(-offset, offset), 
																		p[1] + random.randint(-offset, offset)])
				else:
					surface.blit(picNew, p)
				pygame.display.update()
				surface.fill([0] * 3)
				for ev in pygame.event.get():
					if ev.type == QUIT:
						sys.exit(0)
					elif ev.type == KEYDOWN and timer > 0:
						keyPresses += 1
						p = [p[0] + random.randint(-3, 3), p[1] + random.randint(-3, 3)]
						if keyPresses > 3:
							_done = True
				timer -= 1 + 2 * CONST["QUICKEVOLUTION"]
				if timer <= -50:
					_done = True
				pygame.time.delay(20)
			if timer <= 0:
				newMon = BoxedMon(evolution, self.mons[arPos].getXP(), self.mons[arPos].getNature(), self.mons[arPos].getSelectedAbils())
				if self.selected == self.mons[arPos]:
					self.selected = newMon
				self.mons[arPos] = newMon
		
	def loadFromFile(self, fileName):
		fileName += ".prof"
		mode = ""
		if os.path.exists(os.path.join("Profiles", fileName)):
			while self.mons:
				del self.mons[0]
			while self.boxedMons:
				del self.boxedMons[0]
			fileIn = open(os.path.join("Profiles", fileName))
			self.saveFile = fileName[:-5]
			for line in fileIn:
				line = line.strip().split()
				if line:
					if 5 <= len(line) <= 8 and mode in ["TEAM", "BOX"]:
						parsed = [line[0], int(line[1]), [line[2], line[3]], intOf(line[4:len(line)])]
						if mode == "TEAM":
							self.mons += [BoxedMon(parsed[0], parsed[1], parsed[2], parsed[3])]
						elif mode == "BOX":
							self.boxedMons += [BoxedMon(parsed[0], parsed[1], parsed[2], parsed[3])]
					elif len(line) == 1:
						mode = line[0].upper()
			fileIn.close()
		else:
			print "ERROR LOADING PROFILE: '" + fileName + "' does not exist."
			
	def save(self):
		if self.saveFile == "":
			print "ERROR SAVING PROFILE.  Profile must be loaded before save can occure."
			return
		fileName = self.saveFile + ".prof"
		fileIn = open(os.path.join("Profiles", fileName), "w")
		fileIn.write("TEAM\n")
		for b in self.mons:
			fileIn.write(b.getSaveString())
		fileIn.write("BOX\n")
		for b in self.boxedMons:
			fileIn.write(b.getSaveString())
		fileIn.close()
			
	def getTeam(self):
		toRet = []
		for u in self.mons:
			toRet += [[u.getUnit(), u.getLevel(), u.getNature(), u.getSelectedAbils()]]
		return toRet
		
	def giveXP(self, amt):
		for i in self.mons:
			i.giveXP(amt * CONST["EXPMULT"])
	
	def update(self):
		for u in [self.hovering, self.selected]:
			if u and not self.orderMons:
				u.immobilize()
		
		for u in range(len(self.boxedMons)):
			if self.orderMons:
				pct = (u / float(len(self.boxedMons)))
				tPos = [CONST["BOXLOCATION"][0] + math.cos(math.pi * 2 * pct) * (CONST["BOXSIZE"] - 48),
								CONST["BOXLOCATION"][1] + math.sin(math.pi * 2 * pct) * (CONST["BOXSIZE"] - 48)]
				self.boxedMons[u].setTarget(tPos)
			self.boxedMons[u].update()
			
		for u in self.mons:
			u.update()
	
	def handleEvent(self, ev):
		if ev.type == KEYDOWN:
			if ev.key == K_o:
				self.orderMons = not self.orderMons
		elif ev.type == MOUSEMOTION or ev.type == MOUSEBUTTONDOWN:
			bl = CONST["BOXLOCATION"]
			bs = CONST["BOXSIZE"]
			if bl[0] - bs <= ev.pos[0] <= bl[0] + bs and \
				 bl[1] - bs <= ev.pos[1] <= bl[1] + bs:
				self.hovering = None
				if ev.type == MOUSEMOTION:
					for u in self.boxedMons:
						if u.didClickHit(ev.pos):
							self.hovering = u
				elif ev.type == MOUSEBUTTONDOWN:
					i = 0
					lastSel = self.selected
					self.selected = None
					while i < len(self.boxedMons):
						hit = self.boxedMons[i].didClickHit(ev.pos)
						if hit and lastSel == self.boxedMons[i] and len(self.mons) < CONST["TEAMSIZE"]:
							self.selected = self.boxedMons[i]
							del self.boxedMons[i]
							self.mons += [self.selected]
						else:
							if hit:
								self.selected = self.boxedMons[i]
							i += 1
			elif 600 <= ev.pos[0] <= 800 and 0 <= ev.pos[1] <= 600 and ev.type == MOUSEBUTTONDOWN:
				if self.selected:
					self.selected.modSelectedAbil((ev.pos[1] - 25) / 55)
			elif 0 <= ev.pos[0] <= 800 and 550 < ev.pos[1] <= 600:
				unit = (ev.pos[0] + 1) / 48
				if 0 <= unit < len(self.mons):
					if ev.type == MOUSEBUTTONDOWN:
						if self.selected == self.mons[unit]:
							self.boxedMons += [self.mons[unit]]
							del self.mons[unit]
						else:
							self.selected = self.mons[unit]
					else:
						self.hovering = self.mons[unit]
	
	def drawMons(self, surface):
		for i in range(len(self.mons)):
			pos = (i * 48 + 22, 575)
			drawUnit(surface, pos, self.mons[i].getUnit(), 1, drawLevUp = self.mons[i].levelledUp())
	
	def drawBox(self, surface):
		pygame.draw.circle(surface, [0, 200, 0], CONST["BOXLOCATION"], CONST["BOXSIZE"])
		pygame.draw.circle(surface, [200, 200, 50], CONST["BOXLOCATION"], CONST["BOXSIZE"], 2)
		
		for u in self.boxedMons:
			u.drawMe(surface, True)
			
		self.drawMons(surface)
			
		if self.selected:
			u = self.selected
			drawUnit(surface, (450, 210 - 50), u.getUnit(), 1, level = u.getLevel())
			drawUnitStats(surface, [450, 190], u.getUnit(), True, 0, u.getNature(), u.getLevel())
			u.drawAbils(surface, [600, 25])
			
		if self.hovering:
			u = self.hovering
			drawUnit(surface, (450, 210 + 95), u.getUnit(), 1, level = u.getLevel())
			drawUnitStats(surface, [450, 190], u.getUnit(), True, 5, u.getNature(), u.getLevel())

def loadRandomEnemyGroup(groupName, subGrp = ""):
	groups = {}
	file = open(os.path.join("Data", "Enemies", "RandomGroups.txt"))
	for line in file:
		line = line.strip().split()
		if line:
			if len(line) == 10 and line[0].upper() == groupName.upper():
				if (line[1].upper() == subGrp.upper() or subGrp == ""):
					parsed = [line[2], int(line[3]), [line[4], line[5]], intOf(line[6:10])]
					if line[1] in groups:
						groups[line[1]] += [parsed]
					else:
						groups[line[1]] = [parsed]
			elif line[0] != "GROUPNAME" and len(line) != 10:
				print "ERROR IN 'Data\Enemies\RandomGroups.txt':", line, "should be of length 10."
	subGroups = [k for k in groups]
	return groups[subGroups[random.randint(0, len(subGroups) - 1)]]
		
def addUnit(unitList, unit):
	unitList += [BoxedMon(unit)]
			
def drawUnitStats(surface, pos, unit, drawNames = False, offset = 0, nature = [], level = 0):
	clrs = {"OFF":[200, 200, 200], "DEF":[100, 100, 100], "CON":[200, 0, 0],\
					"STA":[0, 0, 200], "SPE":[200, 100, 200]}
	if unit in UNITSTATS:
		p = [pos[0], pos[1]]
		for k in ["OFF", "DEF", "CON", "STA", "SPE"]:
			if drawNames:
				drawTextBox(surface, [p[0] - 40, p[1] - 8], [40, 20], k, False)
			statVal = int(UNITSTATS[unit][k])
			
			if level:
				statVal = statVal * level / 100.0
			
			if nature:
				statVal = statVal * (1 + 0.1 * (k == nature[0]) - 0.1 * (k == nature[1]))
			
			pygame.draw.rect(surface, clrs[k], ([p[0], p[1] + offset], [statVal * 0.7, 3]))
			p[1] += 15
		

#Menus
def initBattle(surface, player, enemyGrp, enemySubGrp):
	toBattle = [["TeamA", []], ["TeamB", []]]
	for i in player.getTeam():
		toBattle[0][1] += [[i[0], i[1], i[2], i[3]]]
	toBattle[1][1] = loadRandomEnemyGroup(enemyGrp, enemySubGrp)
	if Battle.startBattle(toBattle, surface) == "TeamA":
		if toBattle[0][0]:
			xp = 0
			for i in toBattle[1][1]:
				xp += int(i[1])
			xp /= len(toBattle[0][1])
			player.giveXP(xp)
			player.checkEvolutions(surface, toBattle[1][1])
	player.save()
	
def monMenu(surface, player):
	_done = False

	while not _done:
		for ev in pygame.event.get():
			player.handleEvent(ev)
			if ev.type == QUIT:
				sys.exit()	
			elif ev.type == KEYDOWN:
				if ev.key == K_SPACE:
					_done = True
					"""toBattle = [["TeamA", []], ["TeamB", []]]
					for i in player.getTeam():
						toBattle[0][1] += [[i[0], i[1], i[2], i[3]]]
					toBattle[1][1] = loadRandomEnemyGroup("Test")
					if Battle.startBattle(toBattle, surface) == "TeamA":
						if toBattle[0][0]:
							xp = 0
							for i in toBattle[1][1]:
								xp += int(i[1])
							xp /= len(toBattle[0][1])
							player.giveXP(xp)
							player.checkEvolutions(surface, toBattle[1][1])
					player.save()"""
		
		player.update()
		player.drawBox(surface)

		pygame.display.update()
		surface.fill([0] * 3)
		pygame.time.delay(30)
		
def levSelMenu(surface, player):
	_done = False
	fights = {}
	fileIn = open(os.path.join("Data", "Enemies", "RandomGroups.txt"))
	selList = []
	for line in fileIn:
		line = line.strip().split()
		if len(line) == 10:
			if line[0] in fights and line[1] not in fights[line[0]]:
				fights[line[0]][line[1]] = [[line[2], line[3]]]
			elif line[0] in fights and line[1] in fights[line[0]]:
				fights[line[0]][line[1]] += [[line[2], int(line[3])]]
			elif line[0] not in fights:
				fights[line[0]] = {line[1]:[[line[2], line[3]]]}
				
	for k in fights:
		selList += [k]
	sel = -1
	
	while not _done:
		for ev in pygame.event.get():
			if ev.type == QUIT:
				sys.exit(1)
			elif ev.type == KEYDOWN:
				monMenu(surface, player)
			elif ev.type == MOUSEBUTTONDOWN:
				if 20 <= ev.pos[0] <= 120 and 20 <= ev.pos[1]:
					sel = (ev.pos[1] - 20) / 30
					if sel >= len(selList) or sel < 0:
						sel = -1
				elif 140 <= ev.pos[0] <= 240 and sel != -1 and 20 <= ev.pos[1] < 20 + 30 * len(fights[selList[sel]]):
					grp = selList[sel]
					on = 0
					hit = (ev.pos[1] - 20) / 30
					for k in sorted([k for k in fights[grp]]):
						if on == hit:
							subGrp = k
						on += 1
					initBattle(surface, player, grp, subGrp)
					

		pos = [20, 20]
		for i in range(len(selList)):
			drawTextBox(surface, pos, [100, 30], selList[i], True)
			if i == sel and selList[i] in fights:
				pos2 = [140, 20]
				list = [k for k in fights[selList[i]]]
				for key in sorted(list):
					drawTextBox(surface, pos2, [100, 30], key, True)
					pos3 = [pos2[0] + 100 + 30 / 2, pos2[1] + 30 / 2]
					for unit in fights[selList[i]][key]:
						drawUnit(surface, pos3, unit[0], unit[1])
						pos3[0] += 45
					#def drawUnit(surface, pos, unit, state, frame = 1, level = 0):
					pos2[1] += 30
			pos[1] += 30
			
			#drawTextBox(surface, [pos[0] - 45 / 2, pos[1] + 10], [100, 30], "Level: " + str(level), False)
		player.update()
		player.drawMons(surface)
		
		pygame.display.update()
		surface.fill([0] * 3)
		pygame.time.delay(30)
		
player = Profile()
player.loadFromFile("default")
#player.checkEvolutions(surface)
levSelMenu(surface, player)
monMenu(surface, player)