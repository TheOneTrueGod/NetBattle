import pygame, os, math, random
pygame.init()

CONST = {"SCREENSIZE":[800, 600], "BATTLESIZE":[600, 500], "TIMERATE":1, 
				 "DEBUGPRIORITIES":0, "BOXLOCATION":[210, 210], "BOXSIZE":200, "TEAMSIZE":5,
				 "QUICKEVOLUTION":0, "EXPMULT":7}

GLOBALS = {"CAMPOS":[0, 0], "ID":0, "MOVECAMERA":True}

UNITSTATS = {}
UNITABILITIES = {}

STATLIMITS = {"FREETHOUGHT":10}

SPRITES = {}

ATTACKSPRITES = {}

FONTS = {
		 "FEATFONT":pygame.font.Font(os.path.join("Data", "Fonts", "FeatFont.ttf"),12), "PAUSEFONT":pygame.font.Font(os.path.join("Data", "Fonts", "FeatFont.ttf"),25),
		 "CLIPFONT":pygame.font.Font(os.path.join("Data", "Fonts", "FeatFont.ttf"),12), "EFFECTFONT":pygame.font.Font(os.path.join("Data", "Fonts", "FeatFont.ttf"),10),
		 "TITLEFONT":pygame.font.Font(os.path.join("Data", "Fonts", "FeatFont.ttf"), 24), "TEXTBOXFONT":pygame.font.Font(os.path.join("Data", "Fonts", "FeatFont.ttf"), 10)}

#Functions
def isInt(str):
	for t in str:
		if not "0" <= t <= "9":
			return False
	return True

def getXPReq(lvl):
	return (lvl * (lvl + 1) / 2 - (lvl - 1) * lvl / 2) * 5
	
def buttonHit(mousePos, butPos):
	if butPos[0][0] <= mousePos[0] <= butPos[1][0] and butPos[0][1] <= mousePos[1] <= butPos[1][1]:
		return True
	return False
	
def loadStatLine(statStruct, inputLine, statOrder):
	statStruct[inputLine[0]] = {}
	u = statStruct[inputLine[0]]
	u["Test"] = inputLine[1]
	
	if len(inputLine) == len(statOrder):
		for i in range(1, len(inputLine)):
			u[statOrder[i]] = inputLine[i]
	else:
		print "Error in loadStatLine.  inputLine and statOrder should be the same length."
				
def loadUnitStats(statStruct):
	fileIn = open(os.path.join("Data", "UnitStats", "UnitStats.txt"))
	line = fileIn.readline()
	statOrder = []
	while line:
		line = line.split()
		if line:
			if len(line) < 11:
				print "ERROR loading stats from file.  The following line is too short."
				print line
			elif len(line) > 12:
				print "ERROR loading stats from file.  The following line is too long."
				print line
			elif line[0] == "UNIT":
				statOrder = []
				for i in range(len(line)):
					statOrder += [line[i]]
			else:
				if line[0] in statStruct:
					print "ERROR loading stats from file. '" + line[0] + "' is already loaded."
				loadStatLine(statStruct, line, statOrder)
		line = fileIn.readline()
		
def loadAbilityLine(abilStruct, line):
	unit = line[0]
	i = 1
	while i < len(line):
		lev = int(line[i])
		abil = line[i + 1]
		if unit in abilStruct:
			abilStruct[unit] += [[lev, abil]]
		else:
			abilStruct[unit] = [[lev, abil]]
		i += 2
		
def loadUnitAbilities(abilStruct):
	fileIn = open(os.path.join("Data", "UnitStats", "Abilities.txt"))
	line = fileIn.readline()
	while line:
		line = line.split()
		if line:
			if line[0] == "UNIT":
				pass
			else:
				loadAbilityLine(abilStruct, line)
		line = fileIn.readline()
	
	for k in abilStruct:
		abilStruct[k].sort()

def loadSprites():
	#SPRITES
	loadPicsFromLocation(SPRITES, os.path.join("Pics", "Chars"))
	for k in SPRITES:
		SPRITES[k].set_colorkey([3, 20, 100])
		
	for k in SPRITES:
		size = SPRITES[k].get_width() / 9
		chopUpSprite(SPRITES, k, [size, size])
	
	#ATTACKSPRITES
	loadPicsFromLocation(ATTACKSPRITES, os.path.join("Pics", "Attacks"))
	for k in ATTACKSPRITES:
		ATTACKSPRITES[k].set_colorkey([3, 20, 100])
		
	for k in ATTACKSPRITES:
		size = ATTACKSPRITES[k].get_width()
		chopUpSprite(ATTACKSPRITES, k, [size, size])
		
def loadPicsFromLocation(map, path):
	for file in os.listdir(path):
		i = os.path.splitext(file)[0]
		if os.path.splitext(file)[1] in [".bmp", ".jpg"]:
			map[i] = pygame.image.load(os.path.join(path, file))
	
def intOf(list):
	toRet = []
	for part in list:
		toRet += [int(part)]
	return toRet

def dist(a, b):
	return math.sqrt((a[0] - b[0]) **2 + (a[1] - b[1])**2)

def randFromList(list):
	if not list:
		return None
	return list[random.randint(0, len(list) - 1)]

def isOnScreen(pos):
	return 0 <= pos[0] - GLOBALS["CAMPOS"][0] <= CONST["SCREENSIZE"][0] and \
				 0 <= pos[1] - GLOBALS["CAMPOS"][1] <= CONST["SCREENSIZE"][1]
	
def getAvgPos(listOfUnits, onSameScreen = False, diffType = ""):
	toRet = [0, 0]
	total = 0
	for u in listOfUnits:
		if u.getType() != diffType and u.getType() != "NoAI" and (not onSameScreen or isOnScreen(u.getPos())):
			toRet = [toRet[0] + u.getPos()[0], toRet[1] + u.getPos()[1]]
			total += 1
	if total:
		toRet = [toRet[0] / total, toRet[1] / total]
	if toRet[0] and toRet[1]:
		return toRet
	else:
		return [CONST["SCREENSIZE"][0] / 2, CONST["SCREENSIZE"][1] / 2]
		
def calcTurn(facingAng, targetAng, turnRate):
	selfAng = math.atan2(self.speed[1], self.speed[0])
	angDiff = (ang - selfAng)
	#pi - -pi
	if -self.sightAng < angDiff < 0 or angDiff > math.pi * 2 - self.sightAng:
		selfAng = selfAng - self.turnRate * self.calcTimeRate()
	else:
		selfAng = selfAng + self.turnRate * self.calcTimeRate()
	speed = dist(self.speed, [0, 0])
	self.speed = [math.cos(selfAng) * speed, math.sin(selfAng) * speed]
		
	if math.fabs(angDiff) > self.tolerance:
		speedMod = 0.5

def calcStatsAtLevel(level, statStruct, health, energy):
	for k in statStruct:
		statStruct[k][0] = (2 ** (level / 20.0 + 1) + (statStruct[k][1] / 20.0 * level / 2.0))
		
	health[1] = statStruct["CON"][0] * 2 * level ** 0.1 + 10
	health[0] = health[1]
	health[2] = 0
	
	energy[1] = statStruct["STA"][0] / 2 + 12
	energy[0] = energy[1]
	energy[2] = 0.01#energy[1] * 0.004
	
def calcDamage(offense, defense, baseDamage, attackerLevel):
	return (offense * attackerLevel * baseDamage / (100 * defense) + baseDamage * 0.05)
	
def isInRange(caster, target, ability, distance):
	return caster.getSize() + target.getSize() + ability.getRange() >= distance

def calcSpeed(stat, charLev):
	if charLev >= 1:
		return stat / charLev
	else:
		return 1
	
def calcDmgMod(off):
	return str / 100.0
	
def chopUpSprite(map, key, picSize):
	largeSurface = map[key]
	map[key] = []
	for y in xrange(largeSurface.get_height() / picSize[1]):
		map[key] += [[]]
		for x in xrange(largeSurface.get_width() / picSize[0]):
			map[key][y] += [largeSurface.subsurface([x * picSize[0], y * picSize[1], picSize[0], picSize[1]])]


def drawTextBox(surface, pos, size, text, drawBorder, clr = [255] * 3):
	textSpacing = 5
	if drawBorder:
		pygame.draw.rect(surface, [0]*3,(pos,size))
		pygame.draw.rect(surface, clr,(pos[0] + 2, pos[1] + 2,size[0] - 4, size[1] - 4),2)
	currPos = [pos[0] + 6,pos[1] + 6]
	for lines in text.split("\n"):
		currText = lines.split(" ")
		for i in currText:
			if currPos[1] < pos[1] + size[1]:
				if i.find('\n') != -1:
					toDraw = FONTS["TEXTBOXFONT"].render(i[:i.find('\n')], False, clr)
				else:
					toDraw = FONTS["TEXTBOXFONT"].render(i, False, clr)
				if currPos[0] + toDraw.get_width() - pos[0] + textSpacing > size[0]:
					currPos[0] = pos[0] + 6
					currPos[1] = currPos[1] + 12
				surface.blit(toDraw,(currPos))
				currPos[0] += toDraw.get_width() + textSpacing
		currPos[0] = pos[0] + 6
		currPos[1] = currPos[1] + 12
def drawUnit(surface, pos, unit, state, frame = 1, level = 0, drawLevUp = False):
	if unit in UNITSTATS and "PIC" in UNITSTATS[unit] \
			and "STATE" in UNITSTATS[unit]:
		pic = UNITSTATS[unit]["PIC"]
		if pic in SPRITES:
			state = int(UNITSTATS[unit]["STATE"])
			pic = SPRITES[pic][state][frame]
			height = pic.get_height()
			p = [pos[0] - height / 2, pos[1] - height / 2]
			surface.blit(pic, p)
	if level:
		drawTextBox(surface, [pos[0] - 45 / 2, pos[1] + 10], [100, 30], "Level: " + str(level), False)
	
	if drawLevUp:
		size = [55, 25]
		drawTextBox(surface, intOf([pos[0] - size[0] / 2, pos[1] - size[1] / 2]), 
								size, "Level Up!", False, [255, 120, 0])
								
loadUnitStats(UNITSTATS)
loadUnitAbilities(UNITABILITIES)
loadSprites()