import math
for xp in range(30):
	lvl = math.sqrt(xp * 2 / 5.0)
	print lvl, xp
	
for lvl in range(1, 20):
	xp = (lvl ** 2 / 2.0) * 5
	xp2 = xp - ((lvl - 1) ** 2 / 2.0) * 5
	print lvl, int(xp), xp2