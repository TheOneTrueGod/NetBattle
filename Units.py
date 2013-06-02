import pygame, Globals, random, math, Effects, Abilities, Buffs, Sprites
from Globals import *
from Effects import effects
class Unit:
	def __init__(self, pos, unit="None", level=1, nature=[], abilsToUse=[]):
		self.pos = pos
		self.teamOn = "None"
		
		self.sprite = Sprites.Sprite("Spikey", 1)
		self.state = 0
		
		self.ID = GLOBALS["ID"]
		GLOBALS["ID"] += 1
		
		self.level = level
		
		self.target = None
		self.abilities = []
		self.abilToUse = None
		self.casting = False
		
		self.stats = {"OFF":[5, 100], "DEF":[5, 100], "CON":[5, 100], "STA":[5, 100], "SPE":[5, 100]}
		self.statBuffs = {"OFF":0, "DEF":0, "CON":0, "STA":0, "SPE":0}
		self.health = [50, 50, 0]
		self.energy = [50, 50, 0]
		self.speed = 3
		self.size = 15
		
		self.nature = nature
		self.abilsToUse = abilsToUse
		
		self.buffs = []
		
		self.obeying = False
		
		self.currGoal = "None"
		
		self.angFacing = 0
		
		self.damageTaken = [0, None]
		self.enragedAt = None
		self.movedThisFrame = False
		
		self.enraged = False
		self.cooldown = False
		self.stunned = False
		
		self.safeTime = 0
		
		self.unitName = unit
		self.loadStats(unit)
		
	#Gets	
	def getPos(self):
		return [self.pos[0], self.pos[1]]
		
	def getPriorityMod(self):
		return 0
		
	def getSize(self):
		return self.size
		
	def getUnitName(self):
		return self.unitName
		
	def getState(self):
		return self.state
		
	def getID(self):
		return self.ID
		
	def getAngle(self):
		return self.angFacing
		
	def getStat(self, stat):
		if stat in self.stats:
			toRet = self.stats[stat][0]
			mod = self.statBuffs[stat]
			mod = max(min(mod + 6, 12), 0)
			statMods = [0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1, 1.1, 1.25, 1.43, 1.67, 2.0, 2.5]
			return toRet * statMods[mod]
		print "ERROR IN GETSTAT: '" + stat + "' not a valid stat."
		assert(False)
			
	def getDmgMod(self):
		return calcDmgMod(self.stats["OFF"][0])
			
	def getEnergy(self):
		return self.energy[0]
	
	def getMaxEnergy(self):
		return self.energy[1]
		
	def getEnergyRegen(self):
		return self.energy[2]
		
	def getHealth(self):
		return self.health[0]
		
	def getMaxHealth(self):
		return self.health[1]
		
	def getHealthRegen(self):
		return self.health[2]
		
	def getSpeed(self):
		return self.speed
	
	def getTeamOn(self):
		return self.teamOn
		
	def getCooldown(self):
		if self.cooldown:
			return 1
		return 0
	
	def getAbilType(self):
		if not self.abilToUse:
			return ""
		return self.abilToUse.getDescriptors()[0]
		
	def getAbilToUse(self):
		return self.abilToUse
		
	def isEnraged(self):
		return self.enraged
		
	def isStunned(self):
		return self.stunned
		
	def isHealingTarget(self, target):
		return target == self.target and self.abilToUse and "HEAL" in self.abilToUse.getDescriptors() and \
				(self.casting or isInRange(self, target, self.abilToUse, dist(self.getPos(), target.getPos()))) and\
				(self.energy[0] >= self.abilToUse.getCost() or self.casting)
	
	def canUseAbilNow(self, abil, target):
		return self.energy[0] >= abil.getCost() and self.canAct and \
			abil.canBeUsedNow()
	
	def getTarget(self):
		return self.target
		
	def getLevel(self):
		return self.level
		
	def getType(self):
		return "Default"
	
	def needsHealing(self):
		return self.health[0] < self.health[1] * 0.2
		
	def hasStatChange(self, stat, max):
		mod = self.statBuffs[stat]
		if max < 0 and mod < max or (max > 0 and mod > max):
			return True
		return False
		
	def getStatChange(self, stat):
		if stat not in self.statBuffs:
			return 0
		return self.statBuffs[stat]
	
	def alreadyTargetted(self, teamStruct, allies = True, exclude = []):
		if allies:
			for u in teamStruct.getAllies(self.teamOn):
				if u.getTarget() == self and u not in exclude:
					return u
		else:
			for u in teamStruct.getEnemies(self.teamOn):
				if u.getTarget() == self and u not in exclude:
					return u
	#Sets
	def forceMove(self, delta):
		self.pos = [self.pos[0] + delta[0], self.pos[1] + delta[1]]
		
	def addStatBuff(self, stat, mod):
		self.statBuffs[stat] = max(min(self.statBuffs[stat] + mod, 6), -6)
	
	def loadStats(self, unit):
		if unit in UNITSTATS:
			#Set default values of stats
			for k in self.stats:
				if k in UNITSTATS[unit]:
					self.stats[k] = [0, int(UNITSTATS[unit][k])]
				else:
					print "ERROR when loading stats.  UNITSTATS[" + unit + "] does not contain '" + k + "'"
			
			#Add Nature Bonuses
			if self.nature:
				if self.nature[0] in self.stats:
					self.stats[self.nature[0]][1] *= 1.1
				if self.nature[1] in self.stats:
					self.stats[self.nature[1]][1] *= 0.9
			#Set picture/evolution state
			if "PIC" in UNITSTATS[unit] and "STATE" in UNITSTATS[unit]:
				self.sprite = Sprites.Sprite(UNITSTATS[unit]["PIC"], int(UNITSTATS[unit]["STATE"]))
				self.state = UNITSTATS[unit]["STATE"]
			else:
				print "ERROR when loading stats.  UNITSTATS[" + unit + "] does not contain PIC or STATS"
			#Set size
			if "SIZE" in UNITSTATS[unit]:
				self.size = int(UNITSTATS[unit]["SIZE"]) / 2
			else:
				print "ERROR when loading stats.  UNITSTATS[" + unit + "] does not contain SIZE"
			#Calculate current values of stats
			calcStatsAtLevel(self.level, self.stats, self.health, self.energy)
			self.speed = calcSpeed(self.getStat("SPE"), self.level)
			
		else:
			print "ERROR: ", unit, "not in Unit stats"
			
		self.abilities = Abilities.calcAbilList(self.level, self, self.abilsToUse)
		
	
	def enrage(self, target):
		self.enragedAt = target
		self.enraged = True
	
	def coolingDown(self):
		self.cooldown = True
		
	def stun(self):
		self.stunned = True
		
	def setTeam(self, newTeam, teamStruct):
		teamStruct.wipeBoard(self.teamOn, self)
		self.teamOn = newTeam
		
	def setCasting(self, val):
		self.casting = val
		
	def addAbility(self, newAbil):
		self.abilities += [newAbil]
		
	def recalcDamageTaken(self):
		if len(self.damageTaken) >= 7:
			del self.damageTaken[2]
		
		self.damageTaken[0] = 0
		
		for i in range(2, len(self.damageTaken)):
			self.damageTaken[0] += self.damageTaken[i]
			
		if len(self.damageTaken) - 2 > 0:
			self.damageTaken[0] /= float(len(self.damageTaken) - 2)
		
	def heal(self, amt):
		self.health[0] = min(self.health[0] + amt, self.health[1])
		text = str(int(amt * 10))
		if not self.readyToDelete():
			pos = [self.pos[0] - len(text) * 5 / 2, self.pos[1] - self.getSize() - 10]
			effects.addFrontLayer(Effects.TextEffect(pos, [0, 255, 0], 20, text))
		
	def damageMe(self, amt, unit):
		self.health[0] -= amt
		text = str(int(amt * 10))
		pos = [self.pos[0] - len(text) * 5 / 2, self.pos[1] - self.getSize() - 10]
		if not self.readyToDelete():
			effects.addFrontLayer(Effects.TextEffect(pos, [255, 0, 0], 20, text))
		
		self.damageTaken[1] = unit
		self.damageTaken += [amt]

		self.recalcDamageTaken()
		
	def useEnergy(self, amt):
		if self.energy[0] >= amt:
			self.energy[0] -= amt
			return True
		return False
		
	def addBuff(self, buff):
		self.buffs += [buff]

		#Private methods
	def updateAbilities(self, teamStruct):
		for i in self.abilities:
			i.update(teamStruct)
	
	def updateHashMap(self, map):
		toDel = []
		
		for k in map:
			map[k] -= 1
			if map[k] < 0:
				toDel += [k]
				
		for k in toDel:
				del map[k]
				
	def updateBuffs(self):
		b = 0
		while b < len(self.buffs):
			self.buffs[b].update()
			if self.buffs[b].readyToDelete():
				del self.buffs[b]
			else:
				b += 1		
		
	def pickGoal(self, teamStruct):
		self.currGoal = "None"
		
	def pickAbility(self, teamStruct, goal = None):
		self.abilToUse = None
		
	def pickTarget(self, teamStruct):
		pass
		
	def canMove(self):
		return not self.casting and not self.stunned
		
	def canAct(self):
		if self.cooldown or self.casting or self.stunned:
			return False
		return True
		
	def moveTo(self, moveTarget, moveAdjust = 1, direction = 1):
		if not self.canMove() or self.movedThisFrame or self.sprite.getAnim() in ["ATTACK"]:
			return
		self.movedThisFrame = True
		moveAdjust = min(max(0, moveAdjust), 1)
			
		ang = math.atan2(moveTarget[1] - self.pos[1] , moveTarget[0] - self.pos[0]) 
		if direction == -1:
			ang = ang + math.pi
		
		deltaX = math.cos(ang) * self.getSpeed() * moveAdjust
		deltaY = math.sin(ang) * self.getSpeed() * moveAdjust
		
		self.pos = [self.pos[0] + deltaX,
								self.pos[1] + deltaY]
		
	def moveAway(self, moveTarget, moveAdjust = 1):
		self.moveTo(moveTarget, moveAdjust, -1)

	def goalRunAwayActions(self, teamStruct):
		self.target = None
		sum = [0, 0]
		#Throw in the average
		avgPos = getAvgPos(teamStruct.getAllies(self.teamOn), False, "")
		avgAng = math.atan2(avgPos[1] - self.pos[1], avgPos[0] - self.pos[0])
		distFactor = dist(avgPos, self.pos) * 0.02
		
		sum = [sum[0] + math.cos(avgAng) * distFactor, sum[1] + math.sin(avgAng) * distFactor]
		
		foundOne = False
		
		if self.damageTaken[1]:
			teamStruct.postMessage(self.teamOn, Message(self, self, "Protect", ""))
			teamStruct.postMessage(self.teamOn, Message(self, self.damageTaken[1], "Distract", ""))
			self.damageTaken[1] = None
		
		for u in teamStruct.getEnemies(self.teamOn):
			if u.getTarget() == self:
				foundOne = True
				uAng = math.atan2(self.pos[1] - u.getPos()[1], self.pos[0] - u.getPos()[0])
				deltaAng = math.fabs(uAng - avgAng)
				if deltaAng > math.pi:
					deltaAng = (math.pi - deltaAng)
				if deltaAng > math.pi / 32.0 or deltaAng > math.pi * 2 - math.pi / 32.0:
					uAng += math.pi / 24.0
				
				sum = [sum[0] + math.cos(uAng), sum[1] + math.sin(uAng)]
		
		if foundOne:
			self.angFacing = math.atan2(sum[1], sum[0])
		if foundOne or distFactor < 1:
			self.moveTo([self.pos[0] + math.cos(self.angFacing), self.pos[1] + math.sin(self.angFacing)])
		else:
			if len(self.damageTaken) >= 3:
				del self.damageTaken[2]
				self.recalcDamageTaken()
			
	#External, general methods							
	def checkMessages(self, teamStruct):
		pass
		
	def moveAround(self, teamStruct):
		angDiff = math.pi / 8.0
		foundUnit = False
		for u in teamStruct.getAllies(self.teamOn):
			if dist(self.pos, u.getPos()) <= self.size + u.getSize() * 0.8 and u.getID() != self.getID():
				foundUnit = u
				
		if foundUnit:
			a = math.atan2(self.pos[1] - self.target.getPos()[1], self.pos[0] - self.target.getPos()[0])
			if foundUnit.getID() < self.ID:
				a += math.pi / 2.0
			else:
				a -= math.pi / 2.0
			#a2 = math.atan2(self.pos[1] - self.target.getPos()[1], self.pos[0] - self.target.getPos()[0])
			
			self.moveTo([self.pos[0] + math.cos(a) * 20, self.pos[1] + math.sin(a) * 20], 0.5)
		
	def readyToDelete(self):
		return self.health[0] <= 0
		
	def update(self, teamStruct):
		self.movedThisFrame = False
		self.stunned = False
		teamStruct.wipeBoard(self.teamOn, self)
		self.updateAbilities(teamStruct)
		self.enraged = False
		self.cooldown = False
		self.updateBuffs()
		self.sprite.update()
		self.energy[0] = min(self.energy[1], self.energy[0] + self.energy[2])
		
		if self.target and self.target.readyToDelete():
			self.target = None
			
	def drawBar(self, surface, stat, clr, bckgrd, yOffset):
		if stat[1] > 0:
			pct = min(1, max(0, stat[0] / float(stat[1])))
			
			pos = intOf([self.pos[0] - GLOBALS["CAMPOS"][0] - self.getSize() - 1, 
									 self.pos[1] + yOffset - GLOBALS["CAMPOS"][1]])
			pos2 = intOf([pos[0] + self.getSize() * 2 * pct, pos[1]])
			pos3 = intOf([pos[0] + self.getSize() * 2, pos[1]])
			
			pygame.draw.line(surface, bckgrd, pos, pos3)
			pygame.draw.line(surface, clr, pos, pos2)
			
	def drawMe(self, surface):
		#print self.unitName, self.pos
		pos = [self.pos[0] - GLOBALS["CAMPOS"][0], self.pos[1] - GLOBALS["CAMPOS"][1]]
		self.sprite.drawMe(surface, pos)
		#pygame.draw.circle(surface, [255, 0, 0], intOf(pos), 5)
		self.drawBar(surface, self.health, [0, 255, 0], [255, 0, 0], self.getSize() + 2)
		self.drawBar(surface, self.energy, [0, 0, 255], [255, 0, 0], self.getSize() + 4)
		
		for b in self.buffs:
			b.drawMe(surface)
		
class Warrior(Unit):
	def __init__(self, pos, unit="None", level=1, nature=[], abilsToUse=[]):
		Unit.__init__(self, pos, unit, level, nature, abilsToUse)
		self.lastCallForHelp = 0
		
	def getType(self):
		return "Warrior"
		
	def getPriorityMod(self):
		return 3
		
	def pickTarget(self, teamStruct):
		targets = teamStruct.getEnemies(self.teamOn)
		if not targets:
			return
		
		if self.target:
			if self.isEnraged():
				if not self.enragedAt.readyToDelete():
					self.target = self.enragedAt
				return
			#self.pickAbility(teamStruct)
			currTarg = self.target
			min = [None, -1001, None]
			for targ in targets:
				self.target = targ
				pri = self.pickAbility(teamStruct)
				if targ == currTarg and self.obeying:
					pri += 50
				if pri > min[1]:
					min = [self.abilToUse, pri, targ]
			self.target = min[2]
			self.abilToUse = min[0]
			if self.currGoal == "Protect" and "PROTECT" not in self.abilToUse.getDescriptors():
				self.currGoal = "Distract"
			
		else:
			closest = [100000, None]
			for targ in targets:
				d = dist(targ.getPos(), self.getPos())
				if d < closest[0]:
					closest[0] = d; closest[1] = targ
			self.target = closest[1]
			
			teamStruct.postMessage(self.teamOn, Message(self, self.target, "Attack", "Charge"))
					
	def pickGoal(self, teamStruct):
		if self.target == None and self.currGoal != "Run Away":
			self.currGoal = "None"
			
		#If the unit we're supposed to distract is attacking us, I'd say it is sufficiently distracted
		if self.currGoal == "Distract" and (self.target.getTarget() == self or self.target.readyToDelete()):
			self.currGoal = "Attack"
			self.addBuff(Buffs.Enraged(self, 10, self.target))
			self.obeying = False
			
		#If the unit we're supposed to protect is no longer under attack, then we've done our job.
		if self.currGoal == "Protect":
			targ = None
			for u in teamStruct.getEnemies(self.teamOn):
				if u.getTarget() == self.target:
					targ = u
			if not targ:
				self.currGoal = "Attack"
				self.obeying = False
				
		if self.isEnraged() or self.currGoal == "None":
			self.currGoal = "Attack"
			self.obeying = False
		elif self.health[0] <= self.damageTaken[0] * 5:
			if self.lastCallForHelp <= 0:
				teamStruct.postMessage(self.teamOn, Message(self, self, "Heal", "Help Me"))
				self.lastCallForHelp = 50
			self.lastCallForHelp -= 1
			self.obeying = False
			
	def pickAbility(self, teamStruct, goal = None):
		self.abilToUse = None
		
		if not goal:
			goal = self.currGoal
			
		if not self.target or not self.abilities:
			return -100000

		highest = [None, -1000]
		for abil in self.abilities:
			pri = -1001
			if (goal == "Attack" and "DAMAGE" in abil.getDescriptors()) or \
				 (goal == "Protect" and "DISTRACTION" in abil.getDescriptors()) or \
				 (goal == "Distract" and "DISTRACTION" in abil.getDescriptors()):
				pri = abil.calcPriority([goal], self.target, teamStruct)
			if pri > highest[1]:
				highest[0] = abil
				highest[1] = pri
		
		self.abilToUse = highest[0]
		if self.abilToUse == None and goal in ["Distract", "Protect"]:
			return self.pickAbility(teamStruct, "Attack")
			
		return highest[1]
			
	def checkMessages(self, teamStruct):
		if self.isEnraged() or self.obeying:
			return
		messages = teamStruct.getMessages(self.teamOn)
		
		for m in messages:
			if m.getMessage() == "Attack":
				if not self.target:
					self.target = m.getTarget()
					self.currGoal = "Attack"
				else:
					tDist = dist(self.target.getPos(), self.pos)
					sDist = dist(m.getTarget().getPos(), self.pos)

					if (sDist - tDist) / self.getSpeed() < 20:
						self.target = m.getTarget()
						self.currGoal = "Attack"
			elif (m.getMessage() == "Distract" or m.getMessage() == "Protect") and self.currGoal != "Run Away":
				if m.getTarget() == None:
					print m.getOwner(), m.getTarget(), m.getMessage(), m.getDisplay()
				if dist(self.getPos(), m.getTarget().getPos()) < self.size + 100:
					teamStruct.postMessage(self.teamOn, Message(self, None, "", "On It"))
					self.currGoal = m.getMessage()
					self.target = m.getTarget()
					self.obeying = True
	
	def goalAttackActions(self, teamStruct):
		self.pickTarget(teamStruct)
		if not self.target:
			return
		
		tPos = self.target.getPos()
		self.angFacing = math.atan2(tPos[1] - self.pos[1], tPos[0] - self.pos[0])
		
		d = dist(self.pos, self.target.getPos())
		
		if not self.abilToUse:
			self.pickAbility(teamStruct)
		else:
			targRange = 5 + self.size + self.target.getSize()
			if d > targRange:
				self.moveTo(self.target.getPos())
			elif d < targRange - self.speed:
				self.moveAway(self.target.getPos())
			else:
				self.moveAround(teamStruct)
						
			if self.canAct():
				useRange = self.abilToUse.getRange() + self.size + self.target.getSize() - 1
				if d <= useRange and self.canAct() and self.abilToUse.useMe(self.target, teamStruct):
						self.pickAbility(teamStruct)
	
	def goalDistractActions(self, teamStruct):
		tPos = self.target.getPos()
		self.angFacing = math.atan2(tPos[1] - self.pos[1], tPos[0] - self.pos[0])
		
		d = dist(self.pos, self.target.getPos())
		
		if not self.abilToUse:
			self.pickAbility(teamStruct)
		else:
			targRange = 5 + self.size + self.target.getSize()
			if d > targRange:
				self.moveTo(self.target.getPos())
			if self.canAct():
				useRange = self.abilToUse.getRange() + self.size + self.target.getSize() - 1
				if d <= useRange and self.canAct() and self.abilToUse.useMe(self.target, teamStruct):
					self.pickAbility(teamStruct)
					
	def goalProtectActions(self, teamStruct):
		tPos = self.target.getPos()
		self.angFacing = math.atan2(tPos[1] - self.pos[1], tPos[0] - self.pos[0])
		foundOne = False
		for a in self.abilities:
			if "PROTECT" in a.getDescriptors():
				foundOne = True
		if not foundOne:
			self.pickTarget(teamStruct)
		else:
			self.pickAbility(teamStruct)
			targRange = 5 + self.size + self.target.getSize()
			if d > targRange:
				self.moveTo(self.target.getPos())
			if self.canAct():
				useRange = self.abilToUse.getRange() + self.size + self.target.getSize() - 1
				if d <= useRange and self.canAct() and self.abilToUse.useMe(self.target, teamStruct):
					self.pickAbility(teamStruct)
		
	def update(self, teamStruct):
		Unit.update(self, teamStruct)
		
		self.checkMessages(teamStruct)
		
		self.pickGoal(teamStruct)
		
		if self.currGoal == "Attack":
			self.goalAttackActions(teamStruct)
		elif self.currGoal == "Distract":
			self.goalDistractActions(teamStruct)
		elif self.currGoal == "Protect":
			self.goalProtectActions(teamStruct)
		elif self.currGoal == "Run Away":
			self.goalRunAwayActions(teamStruct)

		if self.sprite.getAnim() not in ["ATTACK", "CAST"]:
			if self.movedThisFrame:
				self.sprite.setAnim("WALK")
			else:
				self.sprite.setAnim("STAND")

class Healer(Unit):
	def __init__(self, pos, unit="None", level=1, nature=[], abilsToUse=[]):
		Unit.__init__(self, pos, unit, level, nature, abilsToUse)
		self.runningTime = 0
	
	def getType(self):
		return "Healer"
		
	def getPriorityMod(self):
		return 0
		
	def checkMessages(self, teamStruct):
		if self.isEnraged():
			return
		messages = teamStruct.getMessages(self.teamOn)
		
		for m in messages:
			if (m.getMessage() == "Heal"):
				if self.currGoal != "Heal" or \
						not (self.target and \
						dist(self.pos, self.target.getPos()) < dist(self.pos, m.getTarget().getPos())):
					self.target = m.getTarget()
					self.obeying = True
					self.currGoal = "Heal"
	
	def pickGoal(self, teamStruct):
		if self.isEnraged() or self.obeying:
			return
		
		if self.currGoal == "None":
			self.currGoal = "Assist"
		
		if self.damageTaken[0] > 0 and self.getHealth() <= self.getMaxHealth() * 0.1:
			if self.currGoal != "Run Away":
				if self.damageTaken[1]:
					teamStruct.postMessage(self.teamOn, Message(self, self.damageTaken[1], "Distract", "Save Me"))
				else:
					teamStruct.postMessage(self.teamOn, Message(self, self, "Protect", "Save Me"))
			self.currGoal = "Run Away"
			self.safeTime = 0
			
		if self.currGoal == "Run Away":
			targ = None
			for u in teamStruct.getEnemies(self.teamOn):
				if u.getTarget() == self:
					targ = u
			
			self.runningTime += 1
			if self.runningTime >= 50 and len(self.damageTaken) >= 3:
				del self.damageTaken[2]
				self.recalcDamageTaken()
				if len(self.damageTaken) <= 2:
					self.currGoal = "None"
					
			if not targ:
				self.currGoal = "None"
				self.damageTaken = [0, None]
			self.runningTime += 1
		else:
			self.runningTime = 0
				
	def pickTarget(self, teamStruct):
		if self.obeying:
			return
		
		if self.currGoal == "Assist":
			highest = -1000
			
			if self.abilToUse and self.getEnergy() < self.abilToUse.getCost():
				self.abilToUse = None
				self.target = None
			
			foundAbil = False
			for u in teamStruct.getAllies(self.teamOn) + [self]:
				for abi in self.abilities:
					pri = abi.calcPriority("Assist", u, teamStruct)
					if pri > highest:
						highest = pri
						self.target = u
						self.abilToUse = abi
						foundAbil = True
						
			if not foundAbil:
				for u in teamStruct.getEnemies(self.teamOn):
					for abi in self.abilities:
						pri = abi.calcPriority("Attack", u, teamStruct)
						if pri > highest:
							highest = pri
							self.target = u
							self.abilToUse = abi
				
	def pickAbility(self, teamStruct, goal = None):
		self.abilToUse = None
		if not goal:
			goal = self.currGoal
			
		if not self.target or not self.abilities:
			return -100000

		highest = [None, -1000]
		for abil in self.abilities:
			pri = -1001
			if (goal == "Assist" and ("HEAL" in abil.getDescriptors() or \
																"BUFF" in abil.getDescriptors() or \
																"DEBUFF" in abil.getDescriptors())) or \
				(goal == "Attack" and "DAMAGE" in abil.getDescriptors()):
				pri = abil.calcPriority([goal], self.target, teamStruct)
				
			if pri > highest[1] and pri > 0:
				highest[0] = abil
				highest[1] = pri
					
		self.abilToUse = highest[0]

		if self.abilToUse == None and goal != "Attack": #and self.energy[0] >= self.energy[1] * 0.2:
			return self.pickAbility(teamStruct, "Attack")
		return highest[1]
	
	def goalAssistActions(self, teamStruct):
		self.pickTarget(teamStruct)
		
		if not self.abilToUse or not self.target:
			avgPos = getAvgPos(teamStruct.getAllies(self.teamOn), False)
			if not avgPos:
				avgPos = self.pos
			d = dist(self.pos, avgPos)
			if d > 100:
				self.moveTo(avgPos)
			return
		
		tPos = self.target.getPos()
		self.angFacing = math.atan2(tPos[1] - self.pos[1], tPos[0] - self.pos[0])
		
		d = dist(self.pos, self.target.getPos())
		
		if self.abilToUse:
			targRange = self.abilToUse.getIdealRange() + self.size + self.target.getSize()
			if d > targRange:
				self.moveTo(self.target.getPos())
			elif d < targRange * 0.5 and "DAMAGE" in self.abilToUse.getDescriptors():
				self.moveAway(self.target.getPos())
			else:
				self.moveAround(teamStruct)
				
			if self.canAct():
				if self.abilToUse:
					useRange = self.abilToUse.getRange() + self.size + self.target.getSize()
					if d <= useRange and self.canAct():
						self.abilToUse.useMe(self.target, teamStruct)
	
	def goalHealActions(self, teamStruct):
		if self.target == None or not self.target.needsHealing():
			self.currGoal = "None"
			self.obeying = False
			return
		
		self.pickAbility(teamStruct)
		
		if not self.abilToUse:
			self.currGoal = "None"
			self.obeying = False
		else:
			targRange = self.abilToUse.getRange() + self.size + self.target.getSize()
			d = dist(self.getPos(), self.target.getPos())
			if d > targRange:
				self.moveTo(self.target.getPos())
			if self.canAct():
				if self.abilToUse:
					useRange = self.abilToUse.getRange() + self.size + self.target.getSize() - 1
					if d <= useRange and self.canAct():
						self.abilToUse.useMe(self.target, teamStruct)
						
	def update(self, teamStruct):
		Unit.update(self, teamStruct)
		
		self.checkMessages(teamStruct)
		
		self.pickGoal(teamStruct)
		
		#print self.teamOn, self.canAct(), self.canMove(), self.currGoal, self.abilToUse, self.target
		if self.currGoal == "Assist":
			self.goalAssistActions(teamStruct)
		elif self.currGoal == "Run Away":
			self.goalRunAwayActions(teamStruct)
			toUse = [None, -10000]
			for a in self.abilities:
				if "HEAL" in a.getDescriptors():
					if (a.getAmtHealed() < self.health[1] - self.health[0] and a.getAmtHealed() > toUse[1]):
						toUse = [a, a.getAmtHealed()]
					elif self.health[0] / float(self.health[1]) < 0.2:
						pri = min(0, (self.health[1] - self.health[0]) - a.getAmtHealed()) + a.getAmtHealed()
						if pri > toUse[1]:
							toUse = [a, pri]
						
			if toUse[0]:
				toUse[0].useMe(self, teamStruct)
				
		elif self.currGoal == "Heal":
			self.goalHealActions(teamStruct)
			
		if self.sprite.getAnim() not in ["ATTACK", "CAST"]:
			if self.movedThisFrame:
				self.sprite.setAnim("WALK")
			else:
				self.sprite.setAnim("STAND")
			
class Ranger(Warrior):
	def getType(self):
		return "Ranger"
		
	def getPriorityMod(self):
		return 1
		
	def pickTarget(self, teamStruct):
		targets = teamStruct.getEnemies(self.teamOn)
		if not targets:
			return
		
		if self.target:
			if self.isEnraged():
				if not self.enragedAt.readyToDelete():
					self.target = self.enragedAt
				return
			#self.pickAbility(teamStruct)
			min = [None, -1001, None]
			for targ in targets:
				self.target = targ
				pri = self.pickAbility(teamStruct)
				if pri > min[1]:
					min = [self.abilToUse, pri, targ]
			self.target = min[2]
			self.abilToUse = min[0]
			
		else:
			closest = [100000, None]
			for targ in targets:
				d = dist(targ.getPos(), self.getPos())
				if d < closest[0]:
					closest[0] = d; closest[1] = targ
			self.target = closest[1]
					
	def pickGoal(self, teamStruct):
		if self.target == None and self.currGoal != "Run Away":
			self.currGoal = "None"
			
		if self.isEnraged() or self.currGoal == "None":
			self.currGoal = "Attack"
			self.obeying = False
		elif self.health[0] <= self.damageTaken[0] * 5:
			if self.lastCallForHelp <= 0:
				teamStruct.postMessage(self.teamOn, Message(self, self, "Heal", "Help Me"))
				self.lastCallForHelp = 50
			self.lastCallForHelp -= 1
			self.obeying = False
			
	def pickAbility(self, teamStruct, goal = None):
		self.abilToUse = None
		
		if not goal:
			goal = self.currGoal
			
		if not self.target or not self.abilities:
			return -100000

		highest = [None, -1000]
		for abil in self.abilities:
			pri = -1001
			if (goal == "Attack" and "DAMAGE" in abil.getDescriptors()):
				pri = abil.calcPriority([goal], self.target, teamStruct)
			if pri > highest[1]:
				highest[0] = abil
				highest[1] = pri
					
		self.abilToUse = highest[0]
		return highest[1]
			
	def goalAttackActions(self, teamStruct):
		self.pickTarget(teamStruct)
		if not self.target:
			return
		
		tPos = self.target.getPos()
		self.angFacing = math.atan2(tPos[1] - self.pos[1], tPos[0] - self.pos[0])
		
		d = dist(self.pos, self.target.getPos())
		
		if not self.abilToUse:
			self.pickAbility(teamStruct)
		else:
			targRange = self.abilToUse.getIdealRange() - 5 + self.size + self.target.getSize()
			if d > targRange:
				self.moveTo(self.target.getPos())
			elif d < targRange - self.speed and not self.isEnraged():
				self.moveAway(self.target.getPos())
			else:
				self.moveAround(teamStruct)
						
			if self.canAct():
				useRange = self.abilToUse.getRange() + self.size + self.target.getSize() - 1
				if d <= useRange and self.canAct() and self.abilToUse.useMe(self.target, teamStruct):
						self.pickAbility(teamStruct)
							
	def checkMessages(self, teamStruct):
		pass
		
	def update(self, teamStruct):
		Unit.update(self, teamStruct)
		
		self.checkMessages(teamStruct)
		
		self.pickGoal(teamStruct)
		if self.currGoal == "Attack":
			self.goalAttackActions(teamStruct)
		elif self.currGoal == "Distract":
			print "Rangers should never be distracting."
			self.goalDistractActions(teamStruct)
		elif self.currGoal == "Protect":
			print "Rangers should never be protecting."
			self.goalProtectActions(teamStruct)
		elif self.currGoal == "Run Away":
			self.goalRunAwayActions(teamStruct)

		if self.sprite.getAnim() not in ["ATTACK", "CAST"]:
			if self.movedThisFrame:
				self.sprite.setAnim("WALK")
			else:
				self.sprite.setAnim("STAND")
	
class NoAI(Unit):
	def getType(self):
		return "NoAI"
		
	def getPriorityMod(self):
		return -100

class Egg(NoAI):
	def getPriorityMod(self):
		return -200
	
class Message:
	def __init__(self, owner, target, message, toDisplay, display = True):
		self.owner = owner
		self.target = target
		self.message = message
		self.toDisplay = toDisplay
		self.display = display
		
	def shouldDisplay(self):
		return self.display
		
	def getMessage(self):
		return self.message
		
	def getTarget(self):
		return self.target
		
	def getDisplay(self):
		return self.toDisplay
		
	def getOwner(self):
		return self.owner
		
class TeamStruct:
	def __init__(self, teamList):
		self.teams = {}
									
		self.messageBoard = {}
		for k in self.teams:
			self.messageBoard[k] = []

		for team in teamList:
			for unit in team[1]:
				self.addUnit(team[0], unit)
				
		indicators = pygame.image.load(os.path.join("Pics", "Other", "TeamIndicators.bmp"))
		indicators.set_colorkey([255] * 3)
		size = indicators.get_width()
		self.teamIndicators = []
		for i in range(2):
			self.teamIndicators += [indicators.subsurface([0, size * i, size, size])]

	#Sets
	def addTeam(self, teamName):
		if teamName not in self.teams:
			self.teams[teamName] = []
			self.messageBoard[teamName] = []
			
	def unitCount(self, teamName):
		if teamName in self.teams:
			return len(self.teams[teamName])
		return 0
	
	def getWinner(self):
		winner = None
		winnerSet = False
		for k in self.teams:
			if len(self.teams[k]) > 0:
				if not winner and not winnerSet:
					winner = k
					winnerSet = True
				elif winner:
					winner = None
		return winner
	
	def addUnit(self, teamName, unit):
		if teamName not in self.teams:
			self.addTeam(teamName)
		self.teams[teamName] += [unit]
		unit.setTeam(teamName, self)
	#Gets
	def getAllies(self, teamName):
		if teamName is "None" or teamName not in self.teams:
			return []
		return self.teams[teamName]
		
	def getEnemies(self, teamName):
		toRet = []
		for name in self.teams:
			if name != teamName or teamName == "None":
				toRet += self.teams[name]
		return toRet
	#MessageBoard
	def postMessage(self, team, message):
		if team in self.teams:
			self.messageBoard[team] += [message]
			pos = message.getOwner().getPos()
			pos = [pos[0] + message.getOwner().getSize(), pos[1]]
			if message.shouldDisplay():
				effects.addEffect(Effects.TextEffect(pos, [255] * 3, 60, message.getDisplay()))
			
	def getMessages(self, team):
		if team in self.messageBoard:
			return self.messageBoard[team]
		return []
		
	def wipeBoard(self, team, owner):
		if team in self.messageBoard:
			curr = 0
			while curr < len(self.messageBoard[team]):
				if self.messageBoard[team][curr].getOwner() is owner:
					del self.messageBoard[team][curr]
				else:
					curr += 1
	def wipeMessage(self, team, message):
		if team in self.messageBoard:
			self.messageBoard[team].remove(message)
			
	#General external methods
	def recalcCamPos(self):
		if not GLOBALS["MOVECAMERA"]:
			return
		avgPos = [0, 0]
		total = 0
		for teamName in self.teams:
			for u in self.teams[teamName]:
				if 0 <= u.getPos()[0] - GLOBALS["CAMPOS"][0] <= CONST["SCREENSIZE"][0] and \
					 0 <= u.getPos()[1] - GLOBALS["CAMPOS"][1] <= CONST["SCREENSIZE"][1]:
					total += 1
					avgPos[0] += u.getPos()[0]
					avgPos[1] += u.getPos()[1]
		if total:
			avgPos = [avgPos[0] / total - CONST["SCREENSIZE"][0] / 2, 
							  avgPos[1] / total - CONST["SCREENSIZE"][1] / 2]
			GLOBALS["CAMPOS"][0] += (avgPos[0] - GLOBALS["CAMPOS"][0]) * 0.1
			GLOBALS["CAMPOS"][1] += (avgPos[1] - GLOBALS["CAMPOS"][1]) * 0.1
			#GLOBALS["CAMPOS"] = [(GLOBALS["CAMPOS"][0] + avgPos[0])/2, (GLOBALS["CAMPOS"][1] + avgPos[1])/2]
			
	def recalcCamPos(self):
		if not GLOBALS["MOVECAMERA"]:
			return
							#Top, Right, Bottom, Left
		corners = [100000, -100000, -100000, 100000]
		for teamName in self.teams:
			for u in self.teams[teamName]:
				if isOnScreen(u.getPos()):
					p = u.getPos()
					if p[1] < corners[0]:
						corners[0] = p[1]
					if p[0] > corners[1]:
						corners[1] = p[0]
					if p[1] > corners[2]:
						corners[2] = p[1]
					if p[0] < corners[3]:
						corners[3] = p[0]
		
		avgPos = [(corners[1] + corners[3]) / 2 - CONST["SCREENSIZE"][0] / 2, 
							(corners[0] + corners[2]) / 2 - CONST["SCREENSIZE"][1] / 2]
		GLOBALS["CAMPOS"][0] += (avgPos[0] - GLOBALS["CAMPOS"][0]) * 0.1
		GLOBALS["CAMPOS"][1] += (avgPos[1] - GLOBALS["CAMPOS"][1]) * 0.1
			
	def update(self):
		for teamName in self.teams:
			curr = 0
			while curr < len(self.teams[teamName]):
				unit = self.teams[teamName][curr]
				unit.update(self)
				if unit.readyToDelete():
					self.wipeBoard(teamName, unit)
					del self.teams[teamName][curr]
				else:
					curr += 1
		self.recalcCamPos()
		
	def drawMe(self, surface):
		team = 0
		for teamName in self.teams:
			for unit in self.teams[teamName]:
				unit.drawMe(surface)
				if team < len(self.teamIndicators):
					c = GLOBALS["CAMPOS"]
					u = unit.getPos()
					surface.blit(self.teamIndicators[team], 
							[u[0] - c[0] - 5 / 2, u[1] - unit.getSize() - 10 - c[1]])
			team += 1
	
	def drawSkipping(self, surface):
		y = 0
		for teamName in self.teams:
			x = 0
			for unit in self.teams[teamName]:
				drawUnit(surface, [100 + x * 45, 100 + y * 50], unit.getUnitName(), unit.getState(), frame = 1)
				pygame.draw.rect(surface, [255, 0, 0], [[80 + x * 45, 115 + y * 50],
										[40 * (unit.getHealth() / float(unit.getMaxHealth())), 2]])
				pygame.draw.rect(surface, [0, 0, 255], [[80 + x * 45, 118 + y * 50],
										[40 * (unit.getEnergy() / float(unit.getMaxEnergy())), 2]])
				x += 1
			y += 1
			#avgPos = getAvgPos(self.getAllies(teamName), True, "Healer")
			#if avgPos:
			#	avgPos = intOf([avgPos[0] - GLOBALS["CAMPOS"][0], avgPos[1] - GLOBALS["CAMPOS"][1]])
			#	pygame.draw.circle(surface, [255, 255, 0], avgPos, 3)