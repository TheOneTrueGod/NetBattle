import Effects, math, Buffs
from Globals import *
from Effects import effects
class Ability:
	def __init__(self, owner = None):
		self.owner = None
		self.descriptors = ["DAMAGE"]
		
		self.cooldown = [0, 0]
		self.castTime = [0, 0, None]
		self.afterDelay = 1
		self.range = 10
		self.damage = 0
		self.cost = 0
		self.ID = "DE"
		self.name = "****ERROR DEFAULT ABILITY NAME****"
		if owner:
			self.assignTo(owner)
		self.childInit()
		
	def childInit(self):
		pass
			
	def getRange(self):
		return self.range
		
	def getIdealRange(self):
		return self.range
		
	def getName(self):
		return self.name
		
	def getCost(self):
		return self.cost
		
	def getDescriptors(self):
		return self.descriptors
		
	def canBeUsedNow(self):
		return self.cooldown[0] > 0
		
	def getDescription(self):
		return "A basic ability that may have many different effects."
		
	def drawInfo(self, surface, pos, selected = True):
		toPrint = self.getName() + "\n"
		
		if self.damage != 0:
			toPrint += "Power " + str(self.damage) + " " * (4 - len(str(self.damage)))
			toPrint += "Range "
			if self.range <= 33:
				toPrint += "Melee "
			else:
				toPrint += str(self.range) + " " * (6 - len(str(self.range)))
			if self.castTime[1] > 0:
				toPrint += "Cast  " + str(self.castTime[1])
			else:
				toPrint += "Delay " + str(self.cooldown[1])
			toPrint += "\n"
		
		toPrint += self.getDescription()
		if selected:
			clr = [255] * 3
		else:
			clr = [150] * 3
		drawTextBox(surface, pos, [200, 56], toPrint, 1, clr)
		
	def calcExpectedDamage(self, target, teamStruct):
		dmg = calcDamage(self.owner.getStat("OFF"), target.getStat("DEF"), self.damage, self.owner.getLevel())
		return min(dmg / float(target.getHealth()), 1) * 30 * (30 / float(self.afterDelay))
		
	def calcPriority(self, goals, target, teamStruct):
		priCalc = -1000
		if self.owner.getEnergy() < self.cost and self.owner.getEnergyRegen() <= 0:
			return -10000
			
		if "Attack" in goals:
			#0 is our base.
			priCalc = 0
			if self.owner.teamOn == "TeamA" and CONST["DEBUGPRIORITIES"]:
					print self.ID + ":", int(priCalc),
			#Remove the number of frames it will take before we can hit them with this attack.
			#Should vary between 0 and -33 (When a target is standing pretty far away), but can rise
			#pretty high for long cooldown attacks
			d = dist(self.owner.getPos(), target.getPos())
			targRange = self.range + self.owner.getSize() + target.getSize()
			regenTime = 0
			if self.owner.getEnergyRegen() > 0:
				regenTime = min(self.owner.getEnergy() - self.cost, 0) / float(self.owner.getEnergyRegen())
				if self.owner.teamOn == "TeamA" and CONST["DEBUGPRIORITIES"]:
					#print "reg:", min(self.owner.getEnergy() - self.cost, 0), float(self.owner.getEnergyRegen()),
					print "reg:", int(regenTime),
			priCalc += min(min(-d + targRange, 0) / self.owner.getSpeed(), \
										 -self.cooldown[0] - self.castTime[1] + regenTime)
			if self.owner.teamOn == "TeamA" and CONST["DEBUGPRIORITIES"]:
				print "rng-", int(priCalc),
					
			#Add a small bonus because the ability can be used right away
			if d <= targRange and self.cooldown[0] <= 0:
				priCalc += 10
			if self.owner.teamOn == "TeamA" and CONST["DEBUGPRIORITIES"]:
					print "rng+", int(priCalc),
						
			#Factor in the damage dealt as a percentage of the opponent's max health.  
			#Should vary between 0 and 30 for a single target, but can grow large
			#for multi-target attacks.
			priCalc += self.calcExpectedDamage(target, teamStruct)
			if self.owner.teamOn == "TeamA" and CONST["DEBUGPRIORITIES"]:
					print "dmg+", int(priCalc),
			
			#Add an incentive to focus fire:
			for u in teamStruct.getAllies(self.owner.getTeamOn()):
				if u.getTarget() == target:
					priCalc += 5
					
			if self.owner.teamOn == "TeamA" and CONST["DEBUGPRIORITIES"]:
					print "fcs+", int(priCalc),
					
			#Different unit classes should appear less threatening
			priCalc += target.getPriorityMod()
			if self.owner.teamOn == "TeamA" and CONST["DEBUGPRIORITIES"]:
				print "unit", int(priCalc),
			
			#Factor in the energy cost.  Don't use an ability if a cheaper one will suffice.
			if self.cost > 0:
				priCalc -= int(math.log(self.cost + 1) / math.log(2))
			if self.owner.teamOn == "TeamA" and CONST["DEBUGPRIORITIES"]:
				print "cst:", int(priCalc),
			if self.owner.teamOn == "TeamA" and CONST["DEBUGPRIORITIES"]:
				print "Final:", int(priCalc)
		return max(int(priCalc), -1000)
		
	def checkHit(self, target, teamStruct):
		targSize = self.range + self.owner.getSize() + target.getSize()
		if dist(self.owner.getPos(), target.getPos()) < targSize:
			dmg = calcDamage(self.owner.getStat("OFF"), target.getStat("DEF"), self.damage, self.owner.getLevel())
			target.damageMe(dmg, self.owner)
	
	def doHitStuff(self, effectList, target, teamStruct):
		dmg = calcDamage(self.owner.getStat("OFF"), target.getStat("DEF"), self.damage, self.owner.getLevel())
		target.damageMe(dmg, self.owner)
	
	def useMe(self, target, teamStruct):
		if not self.cooldown[0] and self.owner.useEnergy(self.cost):
			targSize = self.range + self.owner.getSize() + target.getSize()
			if dist(self.owner.getPos(), target.getPos()) < targSize:
				self.cooldown[0] = self.cooldown[1]
				self.createEffect(target)
				self.owner.addBuff(Buffs.Cooldown(self.owner, self.afterDelay))
				
				self.owner.sprite.setState("PLAY")
				self.owner.sprite.setAnim("ATTACK")
			
			return True
		return False
		
	def canBeUsed(self):
		if self.cooldown[0] <= 0 and self.owner.getEnergy() >= self.cost:
			return True
		return False
		
	def createEffect(self, target):
		pass
			
	def update(self, teamStruct):
		if not self.owner.isStunned():
			self.cooldown[0] = max(self.cooldown[0] - 1, 0)
		if self.castTime[0]:
			if not self.owner.isStunned():
				self.castTime[0] += 1
			self.owner.setCasting(True)
			if self.castTime[0] >= self.castTime[1] and not self.owner.isStunned():
				self.useMe(self.castTime[0], teamStruct)
				self.owner.setCasting(False)
		
	def assignTo(self, owner):
		self.owner = owner
		owner.addAbility(self)

class NoAbil(Ability):
	def childInit(self):
		self.name = "Shake"
		self.damage = 0
		
	def getDescription(self):
		return "It's an egg... All it can do is shake."
		
	def calcPriority(self, goals, target, teamStruct):
		return -100000
		
#Base
class Melee(Ability):
	def childInit(self):
		self.cooldown = [0, 30]
		self.damage = 30
		self.ID = "SL"
		
	def createEffect(self, target):
		effects.addFrontLayer(Effects.TargettingPic(self.owner, target, "Scratch", 7, self))
		
class Ranged(Ability):
	def childInit(self):
		self.cooldown = [0, 50]
		self.damage = 20
		self.ID = "RS"
		self.range = 250
		self.cost = 1
		
	def createEffect(self, target):
		effects.addFrontLayer(Effects.TargettingPic(self.owner, target, "Scratch", 7, self))
	
	def checkHit(self, target, teamStruct):
		targSize = self.range + self.owner.getSize() + target.getSize()
		if dist(self.owner.getPos(), target.getPos()) < targSize:
			dmg = calcDamage(self.owner.getStat("OFF"), target.getStat("DEF"), self.damage, self.owner.getLevel())
			target.damageMe(dmg, self.owner)
			
class Whirlwind(Melee):
	def childInit(self):
		self.cooldown = [0, 15]
		self.cost = 5
		self.damage = 20
		self.ID = "WW"
		
	def calcExpectedDamage(self, target, teamStruct):
		toRet = 0
		for u in teamStruct.getEnemies(self.owner.getTeamOn()):
			if isInRange(self.owner, target, self, dist(self.owner.getPos(), u.getPos())):
				dmg = calcDamage(self.owner.getStat("OFF"), target.getStat("DEF"), self.damage, self.owner.getLevel())
				toRet += min(dmg / float(target.getMaxHealth()), 1) * 30 * (30 / float(self.afterDelay))
		return toRet
		
	def createEffect(self, target):
		pos = self.owner.getPos(); clr = [255] * 3; time = int(self.cooldown[1] * 0.7)
		reach = self.range + self.owner.getSize()
		startAng = 0; endAng = math.pi * 2;
		effects.addEffect(Effects.ArcEffect(pos, clr, time, reach, startAng, endAng))
	
	def checkHit(self, target, teamStruct):
		targSize = self.range + self.owner.getSize()
		for u in teamStruct.getEnemies(self.owner.getTeamOn()):
			if dist(self.owner.getPos(), u.getPos()) <= targSize + u.getSize():
				dmg = calcDamage(self.owner.getStat("OFF"), u.getStat("DEF"), self.damage, self.owner.getLevel())
				u.damageMe(dmg, self.owner)
				
class Taunt(Ability):
	def childInit(self):
		self.cooldown = [0, 1]
		self.cost = 0
		self.ID = "TA"
		self.range = 500
		self.descriptors = ["DISTRACTION"]
	
	def calcUsePriority(self, goals, target, teamStruct):
		toRet = 0
		if "Protect" in goals:
			if target.getTarget() == self.owner.getTarget():
					toRet += 1000
		elif "Distract" in goals:
			if target == self.owner.getTarget():
					toRet += 1000
		elif target.getType() == "Ranger" and not target.isEnraged():
			if target == self.owner.getTarget():
					toRet += 100
		return toRet
	
	def calcPriority(self, goals, target, teamStruct):
		priCalc = -1000
		if self.owner.getEnergy() < self.cost:
			return -10000
			
		if "Distract" in goals or "Protect" in goals:
			#1000 is our base.
			priCalc = 0
			if self.owner.teamOn == "TeamA" and CONST["DEBUGPRIORITIES"]:
				print self.ID + ":", int(priCalc),
			#Use the distance and range as your basis
			d = dist(self.owner.getPos(), target.getPos())
			targRange = self.range + self.owner.getSize() + target.getSize()
			priCalc += min(-d + targRange, 0) / self.owner.getSpeed()
			priCalc -= self.cooldown[0]
			
			if self.owner.teamOn == "TeamA" and CONST["DEBUGPRIORITIES"]:
				print "rng-", int(priCalc),
					
			#Add 100 because it can be used right now.
			if d <= targRange:
				priCalc += 25 + (1 - max(d, 1) / max(float(targRange - target.getSize() - self.owner.getSize()), 1.0)) * 5
				
			if self.owner.teamOn == "TeamA" and CONST["DEBUGPRIORITIES"]:
				print "rng+", int(priCalc),
						
			#Factor in the taunt's priority
			priCalc += self.calcUsePriority(goals, target, teamStruct)
			
			if self.owner.teamOn == "TeamA" and CONST["DEBUGPRIORITIES"]:
				print "dmg+", int(priCalc),
			
			#How much time we will have to wait to deal the damage
			priCalc -= self.cooldown[0] * 4 + self.castTime[1] * 2
			
			if self.owner.teamOn == "TeamA" and CONST["DEBUGPRIORITIES"]:
				print "time", int(priCalc),
			if self.owner.teamOn == "TeamA" and CONST["DEBUGPRIORITIES"]:
				print
		return max(priCalc, -1000)
	
	def createEffect(self, target):
		effects.addEffect(Effects.RingEffect(self.owner.getPos(), [255, 0, 0], 20, 20))
		effects.addEffect(Effects.RingEffect(target.getPos(), [255, 0, 0], 20, 20, False))
	
	def checkHit(self, target, teamStruct):
		targSize = self.range + self.owner.getSize() + target.getSize()
		if dist(self.owner.getPos(), target.getPos()) < targSize:
			target.addBuff(Buffs.Enraged(target, 100, self.owner))
			
	def useMe(self, target, teamStruct):
		if not self.cooldown[0] and self.owner.useEnergy(self.cost):
			self.cooldown[0] = self.cooldown[1]
			self.createEffect(target)
			self.checkHit(target, teamStruct)
			self.owner.addBuff(Buffs.Cooldown(self.owner, self.cooldown[1]))
			return True
		return False
		
class Heal(Ability):
	def childInit(self):
		self.cooldown = [0, 30]
		self.castTime = [0, 10, None]
		self.afterDelay = 1
		self.heals = 10
		self.cost = 7
		self.ID = "HE"
		self.range = 120
		self.descriptors = ["HEAL"]
		
	def getAmtHealed(self):
		return self.heals 
	
	def calcUsePriority(self, goals, target, teamStruct):
		toRet = -3001
		if self.cost > self.owner.getEnergy():
			return -100000
			
		for t in teamStruct.getAllies(self.owner.getTeamOn()):
			if t.isHealingTarget(target):
				return -100000

		if "Assist" in goals and target.getMaxHealth() - target.getHealth() >= self.heals:
			ally = target.alreadyTargetted(teamStruct, True, [self.owner])
			#If there is an ally already targetting this target, and they are closer than we are,
			#and they are currently trying to heal the target, then don't bother trying to help them.
			if ally and dist(target.getPos(), self.owner.getPos()) > \
									dist(target.getPos(), ally.getPos()) and \
									ally.getAbilToUse() and ally.getAbilToUse().canBeUsed() and \
									ally.getAbilType() in self.descriptors:
				pass
			else:
				toRet = self.heals + (target.getHealth() / float(target.getMaxHealth())) * 20 - \
														 (self.cost / self.owner.getEnergy()) * 10
		return toRet
		
	def calcPriority(self, goals, target, teamStruct):
		priCalc = -1000
		if self.owner.getEnergy() < self.cost or target.getHealth() > target.getMaxHealth() * 0.3:
			return -10000
			
		if "Assist" in goals:
			priCalc = 0
			priCalc += self.calcUsePriority(goals, target, teamStruct)
			priCalc -= max(dist(self.owner.getPos(), target.getPos()) - self.getRange(), 0) \
										/ self.owner.getSpeed()
		elif "Heal" in goals:
			priCalc = min(self.heals, target.getMaxHealth() - target.getHealth())
		
		return priCalc
		
	def createEffect(self, target):
		effects.addEffect(Effects.ExplosionEffect(target.getPos(), [255, 255, 0], 30, 30))
	
	def checkHit(self, target, teamStruct):
		target.heal(self.heals)
	
	def pickAnotherTarget(self, teamStruct):
		targ = None
		for u in teamStruct.getAllies(self.owner.getTeamOn()):
			d = dist(self.owner.getPos(), u.getPos())
			#print self.owner.getSize(), self.range, u.getSize(), self.owner.getSize() + self.range + u.getSize(), d
			if self.owner.getSize() + self.range + u.getSize() >= d:
				if targ == None or (u.getMaxHealth() - u.getHealth() > targ.getMaxHealth() - targ.getHealth()):
					targ = u
		return targ
	
	def useMe(self, target, teamStruct):
		if self.castTime[0] >= self.castTime[1]:
			target = self.castTime[2]
			if target.readyToDelete():
				target = self.pickAnotherTarget(teamStruct)
			self.cooldown[0] = self.cooldown[1]
			self.createEffect(target)
			self.checkHit(target, teamStruct)
			self.owner.addBuff(Buffs.Cooldown(self.owner, self.afterDelay))
			
			self.castTime[0] = 0
			self.owner.sprite.setState("PLAY")
			self.owner.sprite.setAnim("ATTACK")
			return True
		elif self.castTime[0] <= 0 and not self.cooldown[0] and self.owner.useEnergy(self.cost):
			self.owner.sprite.setState("LOOP")
			self.owner.sprite.setAnim("CAST")
			self.castTime[0] = 1
			self.castTime[2] = target
		return False
		
#Passive
class Harden(Ability):
	def childInit(self):
		self.cooldown = [0, 200]
		self.damage = 0
		self.afterDelay = 10
		self.ID = "HRDN"
		self.range = 100000
		self.name = "Harden"
		
	def getDescription(self):
		return "Increases defense."
		
	def calcPriority(self, goals, target, teamStruct):
		if self.owner.hasStatChange("DEF", 5):
			toRet = -100000
		else:
			stat = (6 - self.owner.getStatChange("DEF")) + 6
			toRet = min(0.5, 0.1 * stat) * 30 * (30 / float(self.afterDelay))
		return toRet
		
	def doHitStuff(self, target, teamStruct):
		self.owner.addStatBuff("DEF", 2)
		effects.addFrontLayer(Effects.FollowingPic(self.owner, "Buffing", 18, None))
		
	def useMe(self, target, teamStruct):
		if not self.cooldown[0] and self.owner.useEnergy(self.cost):
			self.cooldown[0] = self.cooldown[1]
			self.doHitStuff(target, teamStruct)
			self.owner.addBuff(Buffs.Cooldown(self.owner, self.afterDelay))
			
			self.owner.sprite.setState("PLAY")
			self.owner.sprite.setAnim("ATTACK")
			
			return True
		return False
				
#Direct Damage
class Tackle(Melee):
	def childInit(self):
		self.cooldown = [0, 50]
		self.afterDelay = 30
		self.damage = 20
		self.ID = "TCKL"
		self.name = "Tackle"
		
	def getDescription(self):
		return "Hit an enemy with a limb, or by running into them."
		
	def createEffect(self, target):
		effects.addFrontLayer(Effects.TargettingPic(self.owner, target, "Bash", 8, self))

class Scratch(Tackle):
	def childInit(self):
		self.cooldown = [0, 50]
		self.afterDelay = 30
		self.damage = 20
		self.ID = "SCRH"
		self.name = "Scratch"
		
	def getDescription(self):
		return "Scratch the enemy using claws."
		
	def createEffect(self, target):
		effect = "Scratch"
		if random.random() < 0.5:
			effect = "ScratchRight"
		effects.addFrontLayer(Effects.TargettingPic(self.owner, target, effect, 8, self))
		
		
class RapidSlash(Tackle):
	def childInit(self):
		self.cooldown = [0, 10]
		self.afterDelay = 10
		self.damage = 10
		self.ID = "RPSL"
		self.name = "Rapid Slash"
		
	def getDescription(self):
		return "Quickly scratch the enemy with claws."
		
	def createEffect(self, target):
		effect = "Scratch"
		if random.random() < 0.5:
			effect = "ScratchRight"
		effects.addFrontLayer(Effects.TargettingPic(self.owner, target, effect, 8, self))
		
class Bite(Tackle):
	def childInit(self):
		self.cooldown = [0, 50]
		self.afterDelay = 30
		self.damage = 30
		self.ID = "BITE"
		self.name = "Bite"
		
	def getDescription(self):
		return "Bites an enemy, dealing some damage."
		
	def createEffect(self, target):
		effects.addFrontLayer(Effects.TargettingPic(self.owner, target, "Bite", 8, self))
		
class BodySlam(Tackle):
	def childInit(self):
		self.cooldown = [0, 100]
		self.afterDelay = 30
		self.damage = 60
		self.ID = "BSLM"
		self.name = "Body Slam"
		
	def getDescription(self):
		return "Charge into the enemy with great vigor."
		
class GroundPound(Whirlwind):
	def childInit(self):
		self.cooldown = [0, 120]
		self.cost = 10
		self.damage = 30
		self.range = 100
		self.afterDelay = 40
		self.ID = "GRPD"
		self.name = "Ground Pound"
		
	def getDescription(self):
		return "Smashes the ground, damaging and stunning all nearby enemies"
		
	def useMe(self, target, teamStruct):
		if not self.cooldown[0] and self.owner.useEnergy(self.cost):
			self.cooldown[0] = self.cooldown[1]
			for u in teamStruct.getEnemies(self.owner.getTeamOn()):
				if isInRange(self.owner, target, self, dist(self.owner.getPos(), u.getPos())):
					dmg = calcDamage(self.owner.getStat("OFF"), u.getStat("DEF"), self.damage, self.owner.getLevel())
					self.createEffect(u)
			self.owner.addBuff(Buffs.Cooldown(self.owner, self.cooldown[1]))
			self.owner.sprite.setState("PLAY")
			self.owner.sprite.setAnim("ATTACK")
			return True
		return False
		
	def createEffect(self, target):
		effects.addFrontLayer(Effects.TargettingPic(self.owner, target, "Bash", 8, self))
	
	def doHitStuff(self, effectList, target, teamStruct):
		dmg = calcDamage(self.owner.getStat("OFF"), target.getStat("DEF"), self.damage, self.owner.getLevel())
		target.damageMe(dmg, self.owner)
		target.addBuff(Buffs.Stunned(target, 10))
		dir = math.atan2(target.getPos()[0] - self.owner.getPos()[0], target.getPos()[1] - self.owner.getPos()[1])
		
class BullRush(Tackle):
	def childInit(self):
		self.cooldown = [0, 150]
		self.afterDelay = 50
		self.damage = 10
		self.ID = "BRSH"
		self.name = "Bull Rush"
		
	def getDescription(self):
		return "Charge forward unexpectedly, knocking the enemy off balance"
	
	def calcExpectedDamage(self, target, teamStruct):
		dmg = calcDamage(self.owner.getStat("OFF"), target.getStat("DEF"), self.damage, self.owner.getLevel())
		toRet = min(dmg / float(target.getHealth()) + 0.15, 1) * 30 * (30 / float(self.afterDelay))
		return toRet
	
	def doHitStuff(self, effectList, target, teamStruct):
		dmg = calcDamage(self.owner.getStat("OFF"), target.getStat("DEF"), self.damage, self.owner.getLevel())
		target.damageMe(dmg, self.owner)
		target.addBuff(Buffs.Stunned(target, 50))
		#target.addBuff(Buffs.Knockback(target, 30, dir, 3))
		
#Ranged
class RockThrow(Ranged):
	def childInit(self):
		self.cooldown = [0, 50]
		self.damage = 30
		self.afterDelay = 20
		self.ID = "RKTH"
		self.name = "Rock Throw"
		self.range = 150
		
	def getDescription(self):
		return "Throw a rock at an enemy"
		
	def createEffect(self, target):
		effects.addFrontLayer(Effects.TargettingPic(self.owner, target, "Rock", 10, self))

class FireRay(RockThrow):
	def childInit(self):
		self.cooldown = [0, 80]
		self.damage = 10
		self.afterDelay = 20
		self.ID = "FRRY"
		self.name = "Fire Ray"
		self.range = 150
		self.rayInit()
		
	def rayInit(self):
		self.name = "Fire Ray"
		self.ID = "FRRY"
		self.rayPic = "FireRay"
		
	def getDescription(self):
		return "Hit the enemy with a ray of fire"
		
	def createEffect(self, target):
		effects.addFrontLayer(Effects.TargettingPic(self.owner, target, self.rayPic, 8, self))
		
class FrostRay(FireRay):
	def rayInit(self):
		self.name = "Ice Ray"
		self.ID = "ICRY"
		self.rayPic = "FrostRay"
		
	def getDescription(self):
		return "Hit the enemy with a ray of ice"
		
class PainRay(FireRay):
	def rayInit(self):
		self.name = "Pain Ray"
		self.ID = "ICRY"
		self.rayPic = "PainRay"
		
	def getDescription(self):
		return "Blast the enemy with a ray to cause them pain"
		
class ShockRay(FireRay):
	def rayInit(self):
		self.name = "Shock Ray"
		self.ID = "SHRY"
		self.rayPic = "ShockRay"
		
	def getDescription(self):
		return "Hit the enemy with a ray of shock"
	
class BurningRay(FireRay):
	def rayInit(self):
		self.name = "Burning Ray"
		self.ID = "BURY"
		self.cooldown = [0, 200]
		self.afterDelay = 50
		self.damage = 20
		self.cost = 5
		self.rayPic = "GreaterFireRay"
		
	def calcExpectedDamage(self, target, teamStruct):
		dmg = calcDamage(self.owner.getStat("OFF"), target.getStat("DEF"), self.damage, self.owner.getLevel())
		toRet = min(dmg * 2 / float(target.getHealth()), 1) * 30 * (30 / float(self.afterDelay))
		return toRet
		
	def getDescription(self):
		return "Hit the enemy with a ray that sets them on fire for a little while"
		
	def doHitStuff(self, effectList, target, teamStruct):
		dmg = calcDamage(self.owner.getStat("OFF"), target.getStat("DEF"), self.damage, self.owner.getLevel())
		target.addBuff(Buffs.DamagePerSec(target, 40, dmg / 20.0))
		
class FreezingRay(FrostRay):
	def rayInit(self):
		self.name = "Freezing Ray"
		self.ID = "FRRY"
		self.cooldown = [0, 200]
		self.afterDelay = 50
		self.cost = 10
		self.damage = 20
		self.rayPic = "GreaterFrostRay"
		
	def calcExpectedDamage(self, target, teamStruct):
		toRet = min(0.15, 1) * 30 * (30 / float(self.afterDelay))
		return toRet
		
	def getDescription(self):
		return "Hit the enemy with a ray that freezes the enemy for a little while."
		
	def doHitStuff(self, effectList, target, teamStruct):
		target.addBuff(Buffs.Stunned(target, 60))
		dmg = calcDamage(self.owner.getStat("OFF"), target.getStat("DEF"), self.damage, self.owner.getLevel())
		target.damageMe(dmg, self.owner)
		
class LightningRay(ShockRay):
	def rayInit(self):
		self.name = "Lightning Ray"
		self.ID = "LIRY"
		self.cooldown = [0, 200]
		self.afterDelay = 50
		self.damage = 20
		self.cost = 5
		self.jumpsLeft = 0
		self.rayPic = "GreaterShockRay"
		
	def calcExpectedDamage(self, target, teamStruct):
		dmg = calcDamage(self.owner.getStat("OFF"), target.getStat("DEF"), self.damage, self.owner.getLevel())
		toRet = min(dmg * 2 / float(target.getHealth()), 1) * 30 * (30 / float(self.afterDelay))
		return toRet
		
	def createEffect(self, target, startTarg = None):
		if self.jumpsLeft <= 0:
			self.jumpsLeft = 2
		if not startTarg:
			startTarg = self.owner
		effects.addFrontLayer(Effects.TargettingPic(startTarg, target, self.rayPic, 8, self))
		
	def getDescription(self):
		return "Hit the enemy with a ray that jumps between enemies."
		
	def doHitStuff(self, effectList, target, teamStruct):
		dmg = calcDamage(self.owner.getStat("OFF"), target.getStat("DEF"), self.damage, self.owner.getLevel())
		target.damageMe(dmg, self.owner)
		#Jumping Time.
		if self.jumpsLeft > 0:
			closest = 100000
			nextTarget = None
			for t in teamStruct.getEnemies(self.owner.getTeamOn()):
				d = dist(t.getPos(), target.getPos())
				if d < closest and not t == target:
					nextTarget = t
					closest = d
			if nextTarget:
				self.createEffect(nextTarget, target)
				self.jumpsLeft -= 1
		

class CripplingRay(PainRay):
	def rayInit(self):
		self.name = "Crippling Ray"
		self.ID = "CPRY"
		self.cooldown = [0, 200]
		self.afterDelay = 50
		self.damage = 20
		self.cost = 5
		self.rayPic = "GreaterPainRay"
		
	def calcExpectedDamage(self, target, teamStruct):
		if target.hasStatChange("OFF", -5) and target.hasStatChange("DEF", -5):
			toRet = -100000
		else:
			stat = (-6 - max(target.getStatChange("OFF"), target.getStatChange("DEF"))) + 6
			toRet = min(0.5, 0.05 * stat) * 30 * (30 / float(self.afterDelay))
		return toRet
		
	def getDescription(self):
		return "Hit the enemy with a ray that cripples their offense and defense."
		
	def doHitStuff(self, effectList, target, teamStruct):
		target.addStatBuff("OFF", -1)
		target.addStatBuff("DEF", -1)
		dmg = calcDamage(self.owner.getStat("OFF"), target.getStat("DEF"), self.damage, self.owner.getLevel())
		target.damageMe(dmg, self.owner)
		effects.addFrontLayer(Effects.FollowingPic(target, "Debuffing", 18, None))
		
class EyeOfChaos(Ability):
	def childInit(self):
		self.cooldown = [0, 200]
		self.damage = 20
		self.afterDelay = 50
		self.ID = "EYOC"
		self.cost = 10
		self.name = "Eye of Chaos"
		self.range = 200
		
	def getIdealRange(self):
		return self.range / 2
		
	def getDescription(self):
		return "Spray all nearby enemies with eye rays"
		
	def calcExpectedDamage(self, target, teamStruct):
		toRet = 0
		foundUnit = False
		for u in teamStruct.getEnemies(self.owner.getTeamOn()):
			if isInRange(self.owner, target, self, dist(self.owner.getPos(), u.getPos())):
				if target == u:
					foundUnit = True
				dmg = calcDamage(self.owner.getStat("OFF"), target.getStat("DEF"), self.damage, self.owner.getLevel())
				toRet += min(dmg / float(target.getMaxHealth()), 1) * 30 * (30 / float(self.afterDelay))
		if not foundUnit:
			return -99
		return toRet

	def createEffect(self, target):
		pic = randFromList(["FireRay", "FrostRay", "ShockRay", "PainRay"])
		effects.addFrontLayer(Effects.TargettingPic(self.owner, target, pic, 10, self))		
	
	def doHitStuff(self, effectList, target, teamStruct):
		dmg = calcDamage(self.owner.getStat("OFF"), target.getStat("DEF"), self.damage, self.owner.getLevel())
		target.damageMe(dmg, self.owner)
				
	def useMe(self, target, teamStruct):
		if not self.cooldown[0] and self.owner.useEnergy(self.cost):
			targSize = self.range + self.owner.getSize() + target.getSize()
			foundOne = False
			
			for u in teamStruct.getEnemies(self.owner.getTeamOn()):
				if dist(self.owner.getPos(), u.getPos()) <= targSize + u.getSize():
					self.createEffect(u)
					foundOne = True
				
			if foundOne:
				self.cooldown[0] = self.cooldown[1]
				self.owner.addBuff(Buffs.Cooldown(self.owner, self.afterDelay))
				self.owner.sprite.setState("PLAY")
				self.owner.sprite.setAnim("ATTACK")
			
			return foundOne
		return False
		
class Avalanche(EyeOfChaos):
	def childInit(self):
		self.cooldown = [0, 100]
		self.damage = 20
		self.afterDelay = 50
		self.ID = "AVAL"
		self.cost = 10
		self.name = "Avalanche"
		self.range = 150
		
	def createEffect(self, target):
		pic = "Rock"
		effects.addFrontLayer(Effects.TargettingPic(self.owner, target, pic, 10, self))		
	
	def doHitStuff(self, effectList, target, teamStruct):
		dmg = calcDamage(self.owner.getStat("OFF"), target.getStat("DEF"), self.damage, self.owner.getLevel())
		target.damageMe(dmg, self.owner)
		target.addBuff(Buffs.Enraged(target, 50, self.owner))
		
#Debuffs
class CuteLook(Heal):
	def childInit(self):
		self.cooldown = [0, 200]
		self.afterDelay = 10
		self.damage = 0
		self.castTime = [0, 20, None]
		self.range = 90
		self.ID = "CTLK"
		self.name = "Cute Look"
		self.descriptors = ["BUFF"]
		
	def getDescription(self):
		return "By giving the enemy a cute look, they will be less willing to hurt you."
	
	def calcPriority(self, goals, target, teamStruct):
		return Ability.calcPriority(self, goals, target, teamStruct)
	
	def calcExpectedDamage(self, target, teamStruct):
		if target.hasStatChange("OFF", -5):
			toRet = -100000
		else:
			stat = (-6 - target.getStatChange("OFF")) + 6
			toRet = min(0.5, 0.05 * stat) * 30 * (30 / float(self.afterDelay))
		return toRet
	
	def checkHit(self, target, teamStruct):
		pass
		
	def createEffect(self, target):
		effects.addFrontLayer(Effects.TargettingPic(self.owner, target, "Heart", 30, self))
	
	def doHitStuff(self, effectList, target, teamStruct):
		target.addStatBuff("OFF", -2)
		effects.addFrontLayer(Effects.FollowingPic(target, "Debuffing", 18, None))
		
#Buffs
class FirstAid(Heal):
	def childInit(self):
		self.cooldown = [0, 30]
		self.castTime = [0, 10, None]
		self.afterDelay = 1
		self.heals = 10
		self.cost = 7
		self.ID = "FAID"
		self.range = 50
		self.descriptors = ["HEAL"]
		self.name = "First Aid"
		
	def getDescription(self):
		return "Heal an ally for 10 health."

class Metabolism(Heal):
	def childInit(self):
		self.cooldown = [0, 100]
		self.castTime = [0, 5, None]
		self.afterDelay = 1
		self.heals = 5
		self.cost = 5
		self.ID = "MTAB"
		self.range = 1
		self.descriptors = ["HEAL", "DAMAGE"]
		self.name = "Metabolism"
		
	def getDescription(self):
		return "By using it's high metabolism, a young creature can heal its own wounds."
		
	def calcPriority(self, goals, target, teamStruct):
		priCalc = -1000
		if target != self.owner or self.owner.getEnergy() < self.cost or target.getHealth() > target.getMaxHealth() * 0.3:
			return -10000
		else:
			return 100
		
class Regeneration(Heal):
	def childInit(self):
		self.cooldown = [0, 1000]
		self.castTime = [0, 25, None]
		self.afterDelay = 1
		self.heals = 30
		self.cost = 100
		self.ID = "REGN"
		self.range = 1
		self.descriptors = ["HEAL", "DAMAGE"]
		self.name = "Regeneration"
		
	def checkHit(self, target, teamStruct):
		self.owner.addBuff(Buffs.Regen(self.owner, 200, self.heals))
		
	def getDescription(self):
		return "Kicks this unit's regeneration into gear, healing wounds over a long time."
		
	def calcPriority(self, goals, target, teamStruct):
		priCalc = -1000
		if target != self.owner or self.owner.getEnergy() < self.cost or target.getHealth() > target.getMaxHealth() * 0.5:
			return -10000
		else:
			return 100
		
def calcAbilList(level, unit, abilsToUse):
	toRet = []
	type = unit.getUnitName()
	on = 0
	if type in UNITABILITIES:
		for ab in UNITABILITIES[type]:
			if ab[1] in abilList:
				if on in abilsToUse and level >= ab[0]:
					toRet += [abilList[ab[1]](unit)]
			else:
				print "ERROR IN CalcAbilList:", level, ab, ab[1] in abilList
			on += 1
	else:
		print "ERROR: in calcAbilList.  '" + type + "' not in UNITABILITIES"
	return toRet
	
abilList = {"Tackle":Tackle, "BodySlam":BodySlam, "BullRush":BullRush,
						"GroundPound":GroundPound, "Bite":Bite, "Scratch":Scratch, "RapidSlash":RapidSlash,
						
						"FireRay":FireRay, "PainRay":PainRay, "FrostRay":FrostRay, "ShockRay":ShockRay,
						"BurningRay":BurningRay, "FreezingRay":FreezingRay, "LightningRay":LightningRay,
						"CripplingRay":CripplingRay, "RockThrow":RockThrow, "EyeOfChaos":EyeOfChaos,
						"Avalanche":Avalanche,
						
						"CuteLook":CuteLook, "Harden":Harden,
						
						"FirstAid":FirstAid, "Metabolism":Metabolism, "Regeneration":Regeneration,
						
						"None":NoAbil,
						
						"A0000":Melee, "A0001":Whirlwind, "A0002":Ranged,
						
						"S0000":Heal, "S0001":Taunt}
						
drawAbils = {}