import math, pygame
from Globals import SPRITES, intOf
class Sprite:
	def __init__(self, image, evolution):
		self.frame = 0
		self.state = "LOOP"
		self.anim = "WALK"
		self.last = [0, None, -10]
		self.playSpeed = 6
		self.scale = 1
		if image in SPRITES:
			self.image = SPRITES[image][evolution]
		else:
			print image, "not in SPRITES"
			self.image = None
			
	def getSize(self):
		return (self.image[0].get_width(), self.image[0].get_height())
		
	def setState(self, newState):
		if newState in ["PLAY", "STOP", "LOOP"]:
			self.state = newState
			
	def setScale(self, newScale):
		self.scale = max(min(newScale, 6), 0.01)
		
	def getState(self):
		return self.state
		
	def setPlaySpeed(self, newSpeed):
		self.playSpeed = max(int(newSpeed), 1)
		
	def setAnim(self, newAnim):
		if newAnim.upper() in ["CAST", "ATTACK"]:
			self.frame = 0
			self.anim = newAnim.upper()
			if newAnim in ["ATTACK"]:
				self.setPlaySpeed(4)
			elif newAnim in ["CAST"]:
				self.setPlaySpeed(2)
		elif newAnim.upper() in ["WALK"]:
			if self.anim not in ["WALK", "STAND"]:
				self.frame = 0
			self.anim = newAnim.upper()
			self.setPlaySpeed(6)
		elif newAnim.upper() in ["STAND"]:
			self.anim = newAnim.upper()
				
	def getAnim(self):
		return self.anim
		
	def update(self):
		if ((self.state == "PLAY" and self.frame < self.playSpeed * 3 - 1) or self.state == "LOOP") and \
				self.anim != "STAND":
			self.frame += 1
			if self.state == "LOOP":
				if self.anim in ["WALK", "CAST"]:
					self.frame %= self.playSpeed * 4
				elif self.anim in ["ATTACK"]:
					self.frame %= self.playSpeed * 3
			if self.state == "PLAY" and self.anim == "ATTACK" and self.frame >= self.playSpeed * 3 - 1:
				self.frame = 0
				self.setAnim("WALK")
				self.setState("LOOP")
				
	def drawMe(self, surface, pos):
		if self.image == None:
			return
			
		img = None
		#print self.anim
		if int(self.last[0]) == int(self.frame) and self.last[1] != -10 and self.anim == self.last[2]:
			img = self.last[1]
		else:
			frameOn = 0
			if self.anim in ["WALK", "CAST"]:
				convertFrame = [0,1,2,1]
				frameOn = convertFrame[(int(self.frame) / self.playSpeed % 4)] + (self.anim == "CAST") * 6
			#elif self.anim == "CAST":
				#frameOn = (int(self.frame) / self.playSpeed % 3) + 6
			elif self.anim == "ATTACK":
				frameOn = (int(self.frame) / self.playSpeed % 3) + 3
			elif self.anim == "STAND":
				frameOn = 1
				
			img = self.image[frameOn]
			self.last = [int(self.frame), img, self.anim]
		if self.scale != 1:
			img = pygame.transform.scale(img, (int(img.get_width() * self.scale), int(img.get_height() * self.scale)))
		pos = [pos[0] - self.getSize()[0] / 2, pos[1] - self.getSize()[1] / 2]
		surface.blit(img, intOf(pos))