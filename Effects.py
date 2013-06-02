import pygame
from Globals import *

class Effect:
	def __init__(self, pos, type, clr, time, other):
		assert(False) #This should never be created.  It is a superclass that I stole from
		              #a different program of mine.
		self.pos = pos
		self.type = type
		self.time = time
		self.clr = clr
		self.other = other
		
		if self.type.upper() == "BULLET" or self.type.upper() == "EXPLOSION":
			self.inc = (clr[0] / float(time), clr[1] / float(time), clr[2] / float(time))
			if self.type.upper() == "EXPLOSION":
				self.deltaRad = self.other[0] * 0.7 / self.time
		elif self.type.upper() == "SMOKE":
			self.rad = 0
			self.deltaRad = 5 / float(time)
		elif self.type.upper() == "RING":
			if other[1] == -1:
				self.rad = other[0]
			else:
				self.rad = 0
			self.deltaRad = other[0] / float(time) * other[1]
		elif self.type.upper() == "TEXT":
			self.text = other
			self.inc = (clr[0] / float(time),clr[1] / float(time),clr[2] / float(time))
		elif self.type.upper() == "PING":
			self.rad = [80, 80, 80]
			self.time = max(time, 10)
			self.startTime = self.time
			self.deltaRad = [-80 / float(time), -80 / float(time - 5), -80 / float(time - 10)]
	
	def getPos(self):
		return self.pos
		
	def deleting(self, effectList, teamStruct):
		pass
	
	def calcTimeRate(self):
		return CONST["TIMERATE"]
	
	def getType(self):
		return self.type.upper()
	
	def update(self):
		self.time -= 1 * self.calcTimeRate()
		if self.type.upper() == "BULLET" or self.type.upper() == "EXPLOSION":
			self.clr = (self.clr[0] - self.inc[0] * self.calcTimeRate(), 
						self.clr[1] - self.inc[1] * self.calcTimeRate(), 
						self.clr[2] - self.inc[2] * self.calcTimeRate())
			if self.type.upper() == "EXPLOSION":
				self.other[0] = self.other[0] - self.deltaRad * self.calcTimeRate()
		elif self.type.upper() == "ORB":
			self.pos = (self.pos[0] + self.other[0] * self.calcTimeRate(), 
						self.pos[1] + self.other[1] * self.calcTimeRate())
		elif self.type.upper() == "SMOKE":
			self.pos = (self.pos[0] + self.other[0] * self.calcTimeRate(), 
						self.pos[1] + self.other[1] * self.calcTimeRate())
			self.rad += self.deltaRad * self.calcTimeRate()
		elif self.type.upper() == "RING":
			self.rad += self.deltaRad * self.calcTimeRate()
		elif self.type.upper() == "PING":
			self.rad[0] += self.deltaRad[0] * self.calcTimeRate()
			if self.time < self.startTime - 5:
				self.rad[1] += self.deltaRad[1] * self.calcTimeRate()
			if self.time < self.startTime - 10:
				self.rad[2] += self.deltaRad[2] * self.calcTimeRate()
		elif self.type.upper() == "TEXT":
			self.pos = (self.pos[0], self.pos[1] - 0.3 * self.calcTimeRate())
			self.clr = (self.clr[0] - self.inc[0] * self.calcTimeRate(), 
						self.clr[1] - self.inc[1] * self.calcTimeRate(), 
						self.clr[2] - self.inc[2] * self.calcTimeRate())
	
	def readyToDelete(self):
		return self.time <= 0
	
	def drawMe(self, surface):
		if self.type.upper() == "BULLET":
			pygame.draw.line(surface, self.clr, intOf(self.pos[0]), intOf(self.pos[1]))
		elif self.type.upper() == "ORB":
			pygame.draw.circle(surface, self.clr, intOf(self.pos), 0)
		elif self.type.upper() == "SMOKE" or self.type.upper() == "RING":
			if self.rad < 1:
				pygame.draw.circle(surface, self.clr, intOf(self.pos), 0)
			else:
				pygame.draw.circle(surface, self.clr, intOf(self.pos), int(self.rad), 1)
		elif self.type.upper() == "PING":
			for i in range(len(self.rad)):
				if self.rad[i] > 1:
					pygame.draw.circle(surface, self.clr, intOf(self.pos), int(self.rad[i]), 1)
		elif self.type.upper() == "TEXT":
			surface.blit(FONTS["EFFECTFONT"].render(self.text, False, self.clr), self.pos)
		elif  self.type.upper() == "EXPLOSION":
			pygame.draw.circle(surface, intOf(self.clr), intOf(self.pos), int(self.other[0]))

			
class TextEffect(Effect):
	def __init__(self, pos, clr, time, text):
		self.pos = pos
		self.type = "Text"
		self.time = time
		self.clr = clr
		self.deltaPos = [random.uniform(-3, 3), random.uniform(-1, -6)]
		self.deltaPos += [self.deltaPos[1] * -(random.uniform(1, 4)) / float(time)]
		
		self.text = text
		self.inc = (clr[0] / float(time),clr[1] / float(time),clr[2] / float(time))
	
	def update(self):
		self.time -= 1 * self.calcTimeRate()
		#self.pos = (self.pos[0], self.pos[1] - 0.9 * self.calcTimeRate())
		self.pos = (self.pos[0] + self.deltaPos[0], self.pos[1] + self.deltaPos[1])
		self.deltaPos[1] += self.deltaPos[2]
		self.clr = (self.clr[0] - self.inc[0] * self.calcTimeRate(), 
					self.clr[1] - self.inc[1] * self.calcTimeRate(), 
					self.clr[2] - self.inc[2] * self.calcTimeRate())
	
	def drawMe(self, surface):
		pos = [self.pos[0] - GLOBALS["CAMPOS"][0], self.pos[1] - GLOBALS["CAMPOS"][1]]
		surface.blit(FONTS["EFFECTFONT"].render(self.text, False, self.clr), pos)
		
class PicEffect(Effect):
	def __init__(self, pos, pic, frameRate):
		self.pos = (pos[0] - 8, pos[1] - 8)
		self.pic = pic
		self.time = -1
		if self.pic in ATTACKSPRITES:
			self.maxFrames = len(ATTACKSPRITES[self.pic])
			self.time = frameRate
			self.frameRate = self.maxFrames / float(self.time)
	
	def getType(self):
		return "PICTURE"
	
	def update(self):
		self.time -= 1 * self.calcTimeRate()
	
	def drawMe(self, surface):
		if self.pic in ATTACKSPRITES and self.frameRate > 0:
			pic = ATTACKSPRITES[self.pic][(self.maxFrames) - int(self.time * self.frameRate) - 1][0]
			pos = [self.pos[0] - GLOBALS["CAMPOS"][0] - pic.get_width() / 2, 
						 self.pos[1] - GLOBALS["CAMPOS"][1] - pic.get_height() / 2]
			surface.blit(pic, pos)
			
class MovingPic(PicEffect):
	def __init__(self, startPos, endPos, pic, frameRate, hiddenValue = []):
		PicEffect.__init__(self, startPos, pic, frameRate)
		self.startPos = startPos
		self.endPos = endPos
		self.startTime = self.time
		self.hiddenValue = hiddenValue
	
	def getStartPos(self):
		return self.startPos
		
	def getEndPos(self):
		return self.endPos
		
	def getHiddenVal(self):
		return self.hiddenVal
		
	def drawMe(self, surface):
		if self.pic in ATTACKSPRITES and self.frameRate > 0 and self.startTime > 0:
			pic = ATTACKSPRITES[self.pic][(self.maxFrames) - int(self.time * self.frameRate) - 1][0]
			pos = [self.getStartPos()[0] + (self.getEndPos()[0] - self.getStartPos()[0]) * (1 - self.time / float(self.startTime)) - pic.get_width() / 2,
						 self.getStartPos()[1] + (self.getEndPos()[1] - self.getStartPos()[1]) * (1 - self.time / float(self.startTime)) - pic.get_height() / 2]
			pos = [pos[0] - GLOBALS["CAMPOS"][0], pos[1] - GLOBALS["CAMPOS"][1]]
			surface.blit(pic, pos)

class TargettingPic(MovingPic):
	def __init__(self, startUnit, endUnit, pic, frameRate, abil, hiddenValue = []):
		PicEffect.__init__(self, startUnit.getPos(), pic, frameRate)
		self.startUnit = startUnit
		self.endUnit = endUnit
		self.startTime = self.time
		self.launchingAbil = abil
		self.hiddenValue = hiddenValue
		
	def deleting(self, effectList, teamStruct):
		if self.launchingAbil:
			self.launchingAbil.doHitStuff(effectList, self.endUnit, teamStruct)
	
	def getStartPos(self):
		return self.startUnit.getPos()
		
	def getEndPos(self):
		return self.endUnit.getPos()
		
class FollowingPic(MovingPic):
	def __init__(self, unit, pic, frameRate, abil):
		PicEffect.__init__(self, unit.getPos(), pic, frameRate)
		self.unit = unit
		self.abil = abil
		self.startTime = self.time
		
	def deleting(self, effectList, teamStruct):
		if self.abil:
			self.abil.doHitStuff(effectList, self.unit, teamStruct)	
	
	def getStartPos(self):
		return self.unit.getPos()
				
	def getEndPos(self):
		return self.unit.getPos()
		
#
#
#
#	
class RingEffect(Effect):
	def __init__(self, pos, clr, time, rad, expand = True):
		self.pos = pos
		self.type = "RING"
		self.time = time
		self.clr = clr
		
		self.deltaRad = -rad / float(time)
		self.rad = rad
		if expand:
			self.rad = 0
			self.deltaRad *= -1
		
	def update(self):
		self.time -= 1 * self.calcTimeRate()
		self.rad += self.deltaRad * self.calcTimeRate()

	def drawMe(self, surface):
		pos = [self.pos[0] - GLOBALS["CAMPOS"][0], self.pos[1] - GLOBALS["CAMPOS"][1]]
		if self.rad < 1:
			pygame.draw.circle(surface, self.clr, intOf(pos), 0)
		else:
			pygame.draw.circle(surface, self.clr, intOf(pos), int(self.rad), 1)
			
class ExplosionEffect(Effect):
	def __init__(self, pos, clr, time, rad):
		self.pos = pos
		self.type = "EXPLOSION"
		self.time = time
		self.clr = clr
		self.rad = rad
		
		self.inc = (clr[0] / float(time), clr[1] / float(time), clr[2] / float(time))
		self.deltaRad = self.rad * 0.7 / self.time
	
	def update(self):
		self.time -= 1 * self.calcTimeRate()
		
		self.clr = (self.clr[0] - self.inc[0] * self.calcTimeRate(), 
					self.clr[1] - self.inc[1] * self.calcTimeRate(), 
					self.clr[2] - self.inc[2] * self.calcTimeRate())
		self.rad = self.rad - self.deltaRad * self.calcTimeRate()
	
	def drawMe(self, surface):
		pos = [self.pos[0] - GLOBALS["CAMPOS"][0], self.pos[1] - GLOBALS["CAMPOS"][1]]
		pygame.draw.circle(surface, intOf(self.clr), intOf(pos), int(self.rad))
		
class LineEffect(Effect):
	def __init__(self, pos, clr, time, rad):
		self.pos = pos
		self.time = time
		self.inc = (clr[0] / float(time), clr[1] / float(time), clr[2] / float(time))
		self.clr = clr
		self.deltaRad = 0.7 / float(self.time)
		self.rad = rad
	
	def getType(self):
		return "LINE"
	
	def update(self):
		self.time -= 1 * self.calcTimeRate()
		self.clr = (self.clr[0] - self.inc[0] * self.calcTimeRate(), 
					self.clr[1] - self.inc[1] * self.calcTimeRate(), 
					self.clr[2] - self.inc[2] * self.calcTimeRate())
		self.rad -= self.deltaRad * self.calcTimeRate()
	
	def drawMe(self, surface):
		pos = [self.pos[0] - GLOBALS["CAMPOS"][0], self.pos[1] - GLOBALS["CAMPOS"][1]]
		pygame.draw.line(surface, self.clr, intOf(pos[0]), intOf(pos[1]), int(self.rad))

class ArcEffect(LineEffect):
	def __init__(self, pos, clr, time, rad, startAng, endAng):
		self.pos = pos
		self.time = time
		self.inc = (clr[0] / float(time), clr[1] / float(time), clr[2] / float(time))
		self.clr = clr
		self.rad = rad
		self.angles = [startAng, endAng]
	
	def getType(self):
		return "ARC"
	
	def update(self):
		self.time -= 1 * self.calcTimeRate()
		self.clr = (self.clr[0] - self.inc[0] * self.calcTimeRate(), 
					self.clr[1] - self.inc[1] * self.calcTimeRate(), 
					self.clr[2] - self.inc[2] * self.calcTimeRate())
	
	def drawMe(self, surface):
		pos = [self.pos[0] - GLOBALS["CAMPOS"][0], self.pos[1] - GLOBALS["CAMPOS"][1]]
		r = pygame.rect.Rect(pos[0] - self.rad, pos[1] - self.rad, 
							 self.rad * 2, self.rad * 2)
		pygame.draw.arc(surface, self.clr, r, self.angles[0], self.angles[1], int(self.rad * 0.7))

class SpawnGas(Effect):
	def __init__(self, pos):
		self.pos = (pos[0] - 8, pos[1] - 8)
		self.frameRate = 3
		self.maxFrames = 6
		self.time = (self.maxFrames - 1) * self.frameRate - 1
	
	def getType(self):
		return "SPAWNGAS"
	
	def update(self):
		self.time -= 1 * self.calcTimeRate()
	
	def drawMe(self, surface):
		pos = [self.pos[0] - GLOBALS["CAMPOS"][0], self.pos[1] - GLOBALS["CAMPOS"][1]]
		surface.blit(SPRITES["SPAWNGAS"].subsurface([0, 16 * ((self.maxFrames - 1) - int(self.time) / self.frameRate), 16, 16]), 
					 pos)

class Corpse(Effect):
	def __init__(self, sprite, pos, angle):
		self.sprite = sprite
		self.pos = pos
		self.angle = angle
	
	def getPos(self):
		return [self.pos[0], self.pos[1]]
	
	def getType(self):
		return "CORPSE"
	
	def drawMe(self, surface):
		pos = [self.pos[0] - GLOBALS["CAMPOS"][0], self.pos[1] - GLOBALS["CAMPOS"][1]]
		self.sprite.drawMe(surface, pos, self.angle)

class BloodSurge(Effect):
	def __init__(self, pos):
		self.pos = [pos[0], pos[1]]
		self.timer = [0,200]
		self.type = random.randint(0, 2)
	
	def getType(self):
		return "BLOOD"
	
	def update(self):
		self.timer[0] += 1 * self.calcTimeRate()
	
	def readyToDelete(self):
		return self.timer[0] >= self.timer[1]
	
	def drawMe(self, surface):
		fr = 15
		frameOn = 0
		if self.timer[0] < self.timer[1] - fr * 4:
			frameOn = min(int(self.timer[0]) / fr, 4)
		else:
			frameOn = min(int(self.timer[1] - self.timer[0]) / fr,4)
		pos = [self.pos[0] - GLOBALS["CAMPOS"][0], self.pos[1] - GLOBALS["CAMPOS"][1]]
		img = SPRITES["BLOODSURGE"].subsurface([16 * self.type,frameOn * 16,16,16])
		surface.blit(img, pos)

class EffectStruct:
	def __init__(self):
		self.effects = []
		self.corpses = []
		self.frontLayer = []
	
	def clearAll(self):
		self.effects = []
		self.corpses = []
		self.frontLayer = []
	
	def removeCorpsesInRange(self, pos, rad):
		i = 0
		toRet = []
		while i < len(self.corpses):
			d = dist(self.corpses[i].getPos(), pos)
			if d <= rad:
				toRet += [self.corpses[i].getPos()]
				del self.corpses[i]
			else:
				i += 1
		return toRet
	
	def update(self, teamStruct):
		for ef in self.effects + self.frontLayer:
			ef.update()
		i = 0
		while (i < len(self.effects)):
			if self.effects[i].readyToDelete():
				self.effects[i].deleting(self, teamStruct)
				del self.effects[i]
			else:
				i += 1
		i = 0
		while (i < len(self.frontLayer)):
			if self.frontLayer[i].readyToDelete():
				self.frontLayer[i].deleting(self, teamStruct)
				del self.frontLayer[i]
			else:
				i += 1
	
	def addEffect(self, newEffect):
		self.effects += [newEffect]
	
	def addFrontLayer(self, newEffect):
		self.frontLayer += [newEffect]
	
	def addCorpse(self, newCorpse):
		if len(self.corpses) >= CONST["MAXCORPSES"]:
			del self.corpses[0]
		self.corpses += [newCorpse]
	
	def drawMe(self, surface, layer):
		if layer <= 0:
			for ef in self.effects + self.corpses:
				ef.drawMe(surface)
		elif layer >= 1:
			for ef in self.frontLayer:
				ef.drawMe(surface)
effects = EffectStruct()