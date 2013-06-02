import pygame, math
from pygame.locals import *
pygame.init()

file = "Human"
size = [32, 48]

s = pygame.image.load("Pics\Chars\\" + file + ".bmp")#Sprites.Sprite("TestZombie")
s = pygame.image.load("SideView.PNG")
surface = pygame.display.set_mode((200, 200))

_done = False
time = 0
animTime = 6
on = 1
numTypes = 8
ar = [0, 0, 0, 1, 2, 3, 3, 3, 3, 3, 3]
mode = "None"
while not _done:
	for ev in pygame.event.get():
		if ev.type == KEYDOWN:
			if ev.key == K_UP:
				animTime += 0.5
				print "Frame Rate:", animTime
			elif ev.key == K_DOWN:
				animTime -= 0.5
				time = 0
				print "Frame Rate:", animTime
			elif ev.key == K_LEFT:
				on = min(on + 1, numTypes - 1)
			elif ev.key == K_RIGHT:
				on = max(on - 1, 0)
			elif ev.key == K_a:
				mode = "Attack"
				time = 0
			elif ev.key == K_s:
				mode = "Cast"
				time = 0
			elif ev.key == K_d:
				mode = "None"
			elif ev.key == K_r:
				s = pygame.image.load("Pics\Chars\A.bmp")
			else:
				_done = True
		
	#print size * on, size * ar[int(time / animTime)]
	if mode == "None":
		xMod = size[0] * ar[int(time / animTime)]
		time += 1
		if time >= len(ar) * animTime:
			time = 0
			#mode = "None"
	elif mode == "Cast":
		xMod = 6 * size[0] + int(ar[int(time / animTime)]) * size[0]
		time += 2
		if time >= len(ar) * animTime:
			time = 0
			#mode = "None"
	elif mode == "Attack":
		xMod = 3 * size[0] + int(time / animTime) * size[0]
		time += 2
		if time >= len(ar) * animTime:
			time = 0
			mode = "None"
	
	surface.blit(s.subsurface((xMod, size[1] * on), \
														size), (39, 39))
	#surface.blit(pygame.transform.rotate(
	#			 pygame.transform.scale2x(s.subsurface((size * on, size * ar[int(time / animTime)]), (size, size))), 45), 
	#			 (50, 50))
	#s.drawMe(surface, [100, 100], (math.pi + math.pi / 4.0 * int(ang)) % (math.pi * 2))
	pygame.display.update()
	surface.fill([255]*3)
	pygame.time.delay(40)

"""
import pygame, math, random, os
from pygame.locals import *
pygame.init()
surface = pygame.display.set_mode((800, 600))
img = pygame.image.load(os.path.join("Data", "Pics", "Backgrounds", "Sewerhorizontal.bmp"))
pxla = pygame.PixelArray(img)
for x in range(len(pxla)):
	for y in range(len(pxla[x])):
		if pxla[x][y] == surface.map_rgb((98, 153, 15)):
			r = random.random()
			if r < 0.3:
				newClr = surface.map_rgb((127, 125, 0))
			elif r < 0.6:
				newClr = surface.map_rgb((157, 156, 43))
			elif r < 0.604:
				newClr = surface.map_rgb((149, 149, 97))
			else:
				newClr = surface.map_rgb((192, 156, 72))
			pxla[x][y] = newClr
img = pxla.surface
del pxla
surface.blit(img, [0, 0])

pygame.display.update()
_done = False
while not _done:
	for ev in pygame.event.get():
		if ev.type == QUIT:
			_done = True
			
"""
"""
#Creates clouds with randomly decided colours
import pygame, math, random
from pygame.locals import *
pygame.init()
surface = pygame.display.set_mode((800, 600))
xsize = 400
ysize = 200
for i in range(xsize):
	for j in range(ysize):
		ang =  random.random() * math.pi * 2.0
		d = random.random()
		r = random.random()
		clr = [255]*3
			#(i > 750 or (random.randint(0, 50) + 750 < i and random.random() > 0.4))
		if ((j > 200 or (random.randint(0, 57) + 200 < j and random.random() > 0.4))):
			#if r < 0.05:
			#	clr = [0, 128, 0]
			if r < 0.5:
				clr = [0, 0, 0]
			elif r < 0.9:
				clr = [157, 79, 0]
			else:
				clr = [128] * 3
		elif ((j > 200 or (random.randint(0, 57) + 200 - 57 < j))):# and
			  #(i > 750 or (random.randint(0, 50) + 700 < i and random.random() > 0.1))): #Mix
			if r < 0.3:
				clr = [0, 128, 0]
			elif r < 0.6:
				clr = [157, 79, 0]
			elif r < 0.95:
				clr = [0, 0, 0]
			else:
				clr = [128] * 3
		else:	#Grassy
			if r < 0.7:
				clr = [0, 0, 0]
			else:
				clr = [0, 128, 0]
		if ((i - 10) % 40 in range(4) and (j - 10) % 40 in range(4)) and random.random() < 0.6:
			clr = [0, 255, 0]
		elif ((i - 10) % 40 in [39, 38, 37, 36] + range(7) and (j - 10) % 40 in [39, 38, 37, 36] + range(7) and random.random() < 0.25):
			clr = [0, 255, 0]
		else:
			if r < 0.5:
				clr = [0, 0, 0]
			elif r < 0.9:
				clr = [157, 79, 0]
			else:
				clr = [128] * 3
		if clr == [0,128,0]:
			clr = [0,0,0]
		#pos = (math.cos(ang) * d * xsize + xsize, math.sin(ang) * d * ysize + ysize)
		pos = (i, j)
		pygame.draw.circle(surface, clr, pos, 0)
pygame.display.update()
_done = False
while not _done:
	for ev in pygame.event.get():
		if ev.type == KEYDOWN:
			_done = True
"""

"""

#Creates clouds with randomly decided colours
import pygame, math, random
from pygame.locals import *
pygame.init()
surface = pygame.display.set_mode((800, 600))
xsize = 400
ysize = 200
for i in range(xsize):
	for j in range(ysize):
		ang =  random.random() * math.pi * 2.0
		d = random.random()
		r = random.random()
		clr = [255]*3
			#(i > 750 or (random.randint(0, 50) + 750 < i and random.random() > 0.4))
		if ((j > 200 or (random.randint(0, 57) + 200 < j and random.random() > 0.4))):
			#if r < 0.05:
			#	clr = [0, 128, 0]
			if r < 0.5:
				clr = [0, 0, 0]
			elif r < 0.9:
				clr = [157, 79, 0]
			else:
				clr = [128] * 3
		elif ((j > 200 or (random.randint(0, 57) + 200 - 57 < j))):# and
			  #(i > 750 or (random.randint(0, 50) + 700 < i and random.random() > 0.1))): #Mix
			if r < 0.3:
				clr = [0, 128, 0]
			elif r < 0.6:
				clr = [157, 79, 0]
			elif r < 0.95:
				clr = [0, 0, 0]
			else:
				clr = [128] * 3
		else:	#Grassy
			if r < 0.7:
				clr = [0, 0, 0]
			else:
				clr = [0, 128, 0]
		if ((i - 10) % 40 in range(4) and (j - 10) % 40 in range(4)) and random.random() < 0.6:
			clr = [0, 255, 0]
		elif ((i - 10) % 40 in [39, 38, 37, 36] + range(7) and (j - 10) % 40 in [39, 38, 37, 36] + range(7) and random.random() < 0.25):
			clr = [0, 255, 0]
		else:
			if r < 0.5:
				clr = [0, 0, 0]
			elif r < 0.9:
				clr = [157, 79, 0]
			else:
				clr = [128] * 3
		if clr == [0,128,0]:
			clr = [0,0,0]
		#pos = (math.cos(ang) * d * xsize + xsize, math.sin(ang) * d * ysize + ysize)
		pos = (i, j)
		pygame.draw.circle(surface, clr, pos, 0)
pygame.display.update()
_done = False
while not _done:
	for ev in pygame.event.get():
		if ev.type == KEYDOWN:
			_done = True
"""
"""
import random
toSpawn = 30
for i in range(4):
	x = random.randint(1, 15) * 50
	y = random.randint(1, 11) * 50
	time = random.randint(25, 35)
	print "AddObject Fire", x, y, time
	if random.random() <= 0.5:
		print "SpawnAlly", random.randint(3, 6), "Civilian Random", x - 20, y - 20, x + 20, y + 20
	else:
		print "Spawn", random.randint(3, 6), "Zombie Random", x - 20, y - 20, x + 20, y + 20
"""
"""
import pygame, math
from pygame.locals import *
pygame.init()
surface = pygame.display.set_mode((600, 600))
def fourier(f):
	N = len(f)
	DFT = []
	for k in range(N):#range(-N/2, N/2):
		total = [0, 0]
		for n in range(N):
			#e ^ i * theta = sin(theta) + i * cos (theta)
			theta = (2 * math.pi * (k*n) / float(N))
			total[0] += math.cos(theta) * f[n] / float(N)
			total[1] -= math.sin(theta) * f[n] / float(N)
		DFT += [total]
	return DFT
def invFourier(f):
	N = len(f)
	DFT = []
	for k in range(N):#range(-N/2, N/2):
		total = [0, 0]
		for n in range(N):
			#e ^ i * theta = sin(theta) + i * cos (theta)
			theta = (2 * math.pi * (k*n) / float(N))
			total[0] += math.cos(theta)
			total[1] -= math.sin(theta)
		total = [total[0] * f[n][0] + total[1] * f[n][1], total[0] * f[n][1] + total[1] * f[n][0]]
		DFT += [total]
	return DFT
ds = [0.0, .3, .7, .95, 1.0, .95, .7, .3, 0.0]
dft = fourier(ds)
dft2 = invFourier(dft)
for i in range(len(dft)):
	print str(ds[i]) + " " * (5 - len(str(ds[i]))),
	print "->", str(dft[i])
	print "      ->", dft2[i]
print
#last = (0, 300)
#pygame.draw.line(surface, [100] * 3, [0, 300], [600, 300])
#for x in range(600):
#	pygame.draw.line(surface, [255] * 3, [x, int(f(x))], [x, int(f(x - 1))])

#pygame.display.update()

#d = False
#while not d:
#	for ev in pygame.event.get():
#		if ev.type == KEYDOWN:
#			d = True
"""