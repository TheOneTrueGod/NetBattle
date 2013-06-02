import pygame, random, Effects, sys, Units, Globals
from pygame.locals import *
from Effects import effects
from Globals import *
#Created and Developed by Jeremy Prevoe

def prepUnitsForBattle(teamList):
	toRet = []
	teamOn = 0
	corner = 1
	for team in teamList:
		toRet += [[team[0], []]]
		unitOn = 0
		line = 1
		#unit[3] is a list of abilities.
		for unit in team[1]:
			if unit[0] in UNITSTATS and "CLASS" in UNITSTATS[unit[0]]:
				c = UNITSTATS[unit[0]]["CLASS"]
				if corner == 1: #topLeft
					pos = [line * 30 - unitOn * 30, 30 + unitOn * 30]
				elif corner == 2:#bottomRight
					pos = [CONST["BATTLESIZE"][0] - (line * 30 - unitOn * 30), CONST["BATTLESIZE"][1] - (30 + unitOn * 30)]
				elif corner == 3:#topRight
					pos = [CONST["BATTLESIZE"][0] - (line * 30 - unitOn * 30), (30 + unitOn * 30)]
				elif corner == 4:#bottomLeft
					pos = [(line * 30 - unitOn * 30), CONST["BATTLESIZE"][1] - (30 + unitOn * 30)]
					
				if c == "Tank":
					newUnit = Units.Warrior(pos, unit[0], unit[1], unit[2], unit[3])
				elif c == "Heal":
					newUnit = Units.Healer(pos, unit[0], unit[1], unit[2], unit[3])
				elif c == "Ranger":
					newUnit = Units.Ranger(pos, unit[0], unit[1], unit[2], unit[3])
				elif c == "Egg":
					newUnit = Units.Egg(pos, unit[0], unit[1], unit[2], unit[3])
				else:
					print "NOT IMPLEMENTED: unit AI of '" + c + "'"
					newUnit = Units.NoAI(pos, unit[0], unit[1], unit[2], unit[3])
					
				toRet[teamOn][1] += [newUnit]
				unitOn += 1
				if unitOn >= line:
					line += 1
					unitOn = 0
			else:
				print "Error creating unit '" + unit[0] + "'.  It is not in UNITSTATS"
		teamOn += 1
		corner += 1
	return toRet

#Init structs
def startBattle(teamList, surface):
	teams = Units.TeamStruct(prepUnitsForBattle(teamList))
	
	timeOut = 0
	
	effects.clearAll()
	GLOBALS["CAMPOS"] = [0, 0]
	
	skipping = False
	
	_done = False
	paused = False
	while not _done:
		for ev in pygame.event.get():
			if ev.type == QUIT:
				sys.exit()
			elif ev.type == KEYDOWN:
				if ev.key == K_SPACE:
					#teams = Units.TeamStruct(prepUnitsForBattle(teamList))
					#GLOBALS["CAMPOS"] = [-10, -10]
					skipping = True
					surface.fill([0] * 3)
				elif ev.key == K_p:
					paused = not paused
				elif ev.key == K_UP:
					GLOBALS["CAMPOS"] = [GLOBALS["CAMPOS"][0], GLOBALS["CAMPOS"][1] - 10]
				elif ev.key == K_ESCAPE:
					_done = True
		
		if not paused:
			effects.update(teams)
			teams.update()
		
		if not skipping:
			effects.drawMe(surface, 0)
			teams.drawMe(surface)
			effects.drawMe(surface, 1)
			
			pygame.display.update()
			pygame.time.delay(30)
			surface.fill([0] * 3)
		else:
			surface.fill([0] * 3)
			teams.drawSkipping(surface)
			pygame.display.update()
		if CONST["DEBUGPRIORITIES"] and not paused:
			print
		
		if teams.getWinner() != None:
			timeOut += 1
			if timeOut >= 50:
				_done = True
	if teams.getWinner:
		print "A winner is you", teams.getWinner()
	return teams.getWinner()