import pygame, os, math, random
from Globals import *
class Buff:
	def __init__(self, owner, time):
		self.owner = owner
		self.time = time
		
	def update(self):
		if self.time != -1:
			self.time -= 1
		
	def getStatMod(self, stat):
		return 0
		
	def readyToDelete(self):
		if self.time == -1:
			return False
		return self.time <= 0
		
	def drawMe(self, surface):
		pass
		
class StatChange(Buff):
	def __init__(self, owner, time, stat, mod):
		self.owner = owner
		self.time = time
		self.stat = stat
		self.mod = mod
		
	def getStatMod(self, stat):
		if stat.upper() == self.stat.upper():
			return self.mod
		return 0
		
	def drawMe(self, surface):
		clr = [255] * 3
		if self.stat == "OFF":
			clr = [255, 0, 0]
		elif self.stat == "DEF":
			clr = [128, 64, 0]
		elif self.stat == "SPE":
			clr = [0, 255, 255]
		p = [self.owner.getPos()[0] + math.cos(math.pi / 15.0 * self.time) * 10, 
				 self.owner.getPos()[1] - self.owner.getSize() / 2 + math.sin(math.pi / 15.0 * self.time)]
		p = [p[0] - GLOBALS["CAMPOS"][0], p[1] - GLOBALS["CAMPOS"][1]]
		p2 = [p[0] - math.cos(math.pi / 15.0 * self.time) * 20, 
				  p[1] - math.sin(math.pi / 15.0 * self.time) * 2]
		pygame.draw.circle(surface, clr, intOf(p), 2)
		pygame.draw.circle(surface, clr, intOf(p2), 2)
		
class Cooldown(Buff):
	def update(self):
		if self.time != -1:
			self.time -= 1
		self.owner.coolingDown()
		
class Stunned(Buff):
	def update(self):
		if self.time != -1:
			if self.owner.isStunned():
				self.time -= 0.3
			else:
				self.time -= 1
		self.owner.stun()
	
	def drawMe(self, surface):
		p = [self.owner.getPos()[0] + math.cos(math.pi / 15.0 * self.time) * 10, 
				 self.owner.getPos()[1] - self.owner.getSize() / 2 + math.sin(math.pi / 15.0 * self.time)]
		p = [p[0] - GLOBALS["CAMPOS"][0], p[1] - GLOBALS["CAMPOS"][1]]
		p2 = [p[0] - math.cos(math.pi / 15.0 * self.time) * 20, 
				  p[1] - math.sin(math.pi / 15.0 * self.time) * 2]
		pygame.draw.circle(surface, [255] * 3, intOf(p), 2)
		pygame.draw.circle(surface, [255] * 3, intOf(p2), 2)
		
class Knockback(Buff):
	def __init__(self, owner, time, direction, amt):
		self.owner = owner
		self.time = time
		self.direction = direction
		self.startAmt = amt
		self.startTime = time
		
	def update(self):
		if self.time != -1:
			self.time -= 1
		amt = self.startAmt * self.time / float(self.startTime)
		delta = [math.cos(self.direction) * amt, math.sin(self.direction) * amt]
		self.owner.forceMove([delta[0], delta[1]])
		
class DamagePerSec(Buff):
	def __init__(self, owner, time, amt):
		self.owner = owner
		self.time = time
		self.amt = amt
		
	def update(self):
		if self.time != -1:
			self.time -= 1
		self.owner.damageMe(self.amt, None)
		
class DamageOverTime(DamagePerSec):
	def __init__(self, owner, time, amt, delay):
		self.owner = owner
		self.time = time
		self.amt = amt
		self.delay = delay
		self.lastHit = time
		
	def update(self):
		if self.time != -1:
			self.time -= 1
		while self.lastHit - self.time > self.delay:
			self.lastHit += self.delay
			self.owner.damageMe(self.amt, None)	

class Regen(Buff):
	def __init__(self, owner, time, amt):
		self.owner = owner
		self.time = time
		self.amt = amt
		
	def update(self):
		if self.time != -1:
			self.time -= 1
		if self.time % 10 == 0:
			self.owner.heal(self.amt)
		
class Enraged(Buff):
	def __init__(self, owner, time, target):
		self.owner = owner
		self.time = time
		self.target = target
		
	def update(self):
		if self.time != -1:
			self.time -= 1
		self.owner.enrage(self.target)