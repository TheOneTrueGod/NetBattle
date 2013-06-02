space = 6
print " " * space, " " * 3,
for baseVal in [25, 50, 75, 100, 150, 200]:
	toPr = str(baseVal)
	print toPr + " " * (space - len(toPr)),
print
print
	
for lev in [1, 5, 10, 25, 50, 100]:
	toPr = str(lev)
	print " " * (space - len(toPr))+ toPr, 
	print " " * 3,
	for baseVal in [25, 50, 75, 100, 150, 200]:
		stat = (lev * baseVal) / 50.0 
		toPr = str(int(stat))
		print toPr + " " * (space - len(toPr)),
	print