# -+-+- TODO -+-+- 
# MAIN:
# - Finish chunk receiving and parsing
# - Implement falling if no block under bot (don't forget to change isOnGround state)
# - Fix walking in straight line
# - Implement jumping (with a constantly adjusting y velocity)
# - Implement sprinting
# - Implement A* (! good luck)
#
# SECONDARY:
# - Implement velocity-everything (walk acceleration instead of constant speed)
# - Implement throwback when player is hit (or not? :])
# - 

#IMPORTANT: FOR NOW NO ENCRYPTION NOR COMPRESSION, OFFLINE MODE ONLY

import socket
import os
import json
from struct import *
from threading import Thread
import time
import math

import protocol as proto
import classes
import nbtparser

os.system("cls")

global PROT_VERSION, HOST, PORT, NAME, SELF, WORLD, SENDPOSTHREAD, CURRENTORDER, ACTIONLIST, MOVING

PROT_VERSION = 578
HOST = "localhost"
PORT = 25565
NAME = "MCBot"

SELF = None
WORLD = None

SENDPOSTHREAD = None

CURRENTORDER = ""
ACTIONLIST = []
MOVING = False


def printBytesProperly(bytestring):
	print(''.join(['\\x%02x' % b for b in bytestring]))
	
	
def calcDistance(x1, y1, x2, y2):
	dist = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
	return dist
	
def dotProduct(v1, v2):
	return (v1[0]*v2[0] + v1[1]*v2[1])
	
def vectorMagnitude(v):
	return math.sqrt( v[0]**2 + v[1]**2 )

def divideVectorBy(v, x):
	return [v[0]/x, v[1]/x]
	
def executeActions(sock):
	global PROT_VERSION, HOST, PORT, NAME, SELF, WORLD, SENDPOSTHREAD, CURRENTORDER, ACTIONLIST, MOVING
	
	walkspeed = 4.317  # en bloc/s
	pps = 10.0
	blocperpacket = walkspeed/pps
	
	print("executeActions started")
	while True:
		if len(ACTIONLIST) > 0:
			print("ACTION")
			action = ACTIONLIST[0]
			ACTIONLIST.pop(0)
			if action[0] == "MOVE":
				# MOVING = True
				v1 = [1.0, 0.0]
				v2 = [action[1][0]-SELF.x, action[1][1]-SELF.z]
				
				uv1 = divideVectorBy(v1, vectorMagnitude(v1))
				uv2 = divideVectorBy(v2, vectorMagnitude(v2))
				dot = dotProduct(uv1,uv2)
				angle = math.acos(dot)
				print(angle)
				
				
				motionx = blocperpacket*math.cos(angle)
				motionz = blocperpacket*math.sin(angle)
				print(motionx, motionz)
				while calcDistance(SELF.x, SELF.z, action[1][0], action[1][1]) > 1:
					if CURRENTORDER == "stop":
						CURRENTORDER = ""
						break
					SELF.x += motionx
					SELF.z += motionz
					print("x = ",SELF.x)
					print("z = ",SELF.z)
					print("sending posupdate")
					# p = proto.craft_packet(0x11, pack(">d", SELF.x) + pack(">d", SELF.y) + pack(">d", SELF.z) + pack(">?", True))
					# sock.send(p)
					time.sleep(1.0/pps)
				# MOVING = False

		time.sleep(0.1)


def sendPositionUpdate(sock):
	global PROT_VERSION, HOST, PORT, NAME, SELF, WORLD, SENDPOSTHREAD, CURRENTORDER, ACTIONLIST, MOVING
	while True:
		if not MOVING:
			# print("sending posupdate ","(%.2f, %.2f, %.2f)"%(SELF.x, SELF.y, SELF.z))
			p = proto.craft_packet(0x11, pack(">d", SELF.x) + pack(">d", SELF.y) + pack(">d", SELF.z) + pack(">?", True))
			sock.send(p)
		time.sleep(0.05)
		

def main():
	global PROT_VERSION, HOST, PORT, NAME, SELF, WORLD, SENDPOSTHREAD, CURRENTORDER, ACTIONLIST
	s = socket.socket()
	s.connect((HOST, PORT))
	p = proto.craft_packet(0x00, proto.pack_varint(PROT_VERSION) + proto.pack_string(HOST) + pack(">H",PORT) + b"\x02")
	s.send(p)
	
	p = proto.craft_packet(0x00, proto.pack_string(NAME))
	s.send(p)
	
	Thread(target=executeActions, args=(s,)).start()
	
	while True:
		plength = proto.unpack_varint(s)-1
		pid = proto.unpack_varint(s)
		if pid == 0x21:
			# print("Responding to Keep-Alive...")
			data = s.recv(plength)
			p = proto.craft_packet(0x0F, data)
			s.send(p)
		elif pid == 0x26:
			eid = unpack(">i",s.recv(4))
			gamemode = unpack(">B",s.recv(1))
			dimension = unpack(">i",s.recv(4))
			hseed = unpack(">q",s.recv(8))
			mplayer = unpack(">B",s.recv(1))
			lvltype = proto.recv_string(s)
			viewdist = proto.unpack_varint(s)
			rdi = unpack(">?",s.recv(1))
			ers = unpack(">?",s.recv(1))
			SELF = classes.Player(eid, gamemode, dimension)
			WORLD = classes.World(hseed, lvltype, viewdist, ers)
			print(SELF.eid, SELF.gamemode, SELF.dimension)
			print(WORLD.leveltype, WORLD.viewdistance, WORLD.enablerespawnscreen)
		elif pid == 0x0F:
			json_data = proto.recv_string(s)
			pos = unpack(">B", s.recv(1))
			j = json.loads(json_data)
			
			sender = j["with"][0]["text"]
			content = j["with"][1]
			print("From %s: %s"%(sender, content))
			
			try:
				if content.startswith(NAME):
					msgl = content.split()
					if msgl[1] == "introduce":
						p = proto.craft_packet(0x03, proto.pack_string("Hi, my name is %s."%NAME))
						s.send(p)
					elif msgl[1] == "move":
						print("MOVING")
						CURRENTORDER = "move"
						ACTIONLIST.append(["MOVE", (float(msgl[2]), float(msgl[3]))])
					elif msgl[1] == "stop":
						print("STOPPING")
						CURRENTORDER = "stop"
					elif msgl[1] == "sitrep":
						p = proto.craft_packet(0x03, proto.pack_string( "(%.2f, %.2f, %.2f)"%(SELF.x, SELF.y, SELF.z) ))
						s.send(p)
					elif msgl[1] == "strafe":
						SELF.x += 0.3
			except AttributeError:
				pass
					
		elif pid == 0x36:
			
			x = unpack(">d", s.recv(8))[0]
			y = unpack(">d", s.recv(8))[0]
			z = unpack(">d", s.recv(8))[0]
			yaw = unpack(">f", s.recv(4))[0]
			pitch = unpack(">f", s.recv(4))[0]
			flags = unpack(">B", s.recv(1))[0]
			teleport_id = proto.unpack_varint(s)
			p = proto.craft_packet(0x00, proto.pack_varint(teleport_id))
			s.send(p)
			print("GOT YOUR POSITION (%.2f, %.2f, %.2f). If you see this message more than once, something is wrong."%(x, y, z))
			SELF.x = x
			SELF.y = y
			SELF.z = z
			SELF.yaw = yaw
			SELF.pitch = pitch
			# print("Position updated: (%.2f, %.2f, %.2f)"%(x,y,z))
			# print("yaw/pitch : (%.2f/%.2f)"%(yaw, pitch))
			if SENDPOSTHREAD == None:
				SENDPOSTHREAD = Thread(target=sendPositionUpdate, args=(s,))
				SENDPOSTHREAD.start()
		
		elif pid == 0x22:
			#UNFINISHED
			#NOTHING WORKS AND MY LIFE IS A PAIN
			data = s.recv(plength)
			
			# # print("Receiving chunk data")
			# chunkx = unpack(">i",s.recv(4))[0]
			# chunkz = unpack(">i",s.recv(4))[0]
			
			# fullchunk = unpack(">?",s.recv(1))[0]
			# if fullchunk:
				# chunk = classes.Chunk(chunkx, chunkz)
			# else:
				# chunk = WORLD.getChunk(chunkx, chunkz)
				
			# readbytes = 9
			
			# primarybitmask = proto.unpack_varint(s)
			# readbytes += len(proto.pack_varint(primarybitmask))
			# heightmap = nbtparser.NBTStruct()
			# heightmap.parseFromSocket(s)
			# heightmap.printPretty()
			
			# readbytes += 2*36*8 + 13 + 15 + 4 + (2+1+1+4)*2
			
			# if fullchunk:
				# biomes = s.recv(1024*4)
				# readbytes+=(1024*4)
			# else:
				# biomes = None
				
			# # print(biomes)
			
			# datasize = proto.unpack_varint(s)
			# readbytes += len(proto.pack_varint(datasize))
			# count = ("{0:b}".format(primarybitmask)).count("1")
			
			# ####
			# data = s.recv(datasize)
			# readbytes += datasize
			# ####
			
			
			# # for i in range(count):
				# # chunksection = classes.ChunkSection()
				# # bloccount = unpack(">H", s.recv(2))[0]
				# # bitsperblock = unpack(">B", s.recv(1))[0]
				
				# # palettetype = "indirect"
				# # if bitsperblock < 4:
					# # bitsperblock = 4
				# # if bitsperblock > 8:
					# # bitsperblock = 14
					# # palettetype = "direct"
				
				# # if palettetype == "indirect":
					# # palette_len = proto.unpack_varint(s)
					# # palette = None
					# # if palette_len:
						# # palette = []
						# # for j in range(palette_len):
							# # palette.append(proto.unpack_varint(s))
				# # datalongs = proto.unpack_varint(s)
				# # print(datalongs)
				# # datablocks = []
				# # for j in range(datalongs):
					# # datablocks.append(unpack(">Q", s.recv(8))[0])

			# nobe = proto.unpack_varint(s)
			# readbytes += len(proto.pack_varint(nobe))

			# print(chunkx, "/", chunkz)
			# print("Nb of active sections: ",count)
			# blockentities = s.recv(plength-readbytes)

			
			
		else:
			# print("Received unimplemented %s (%d data bytes):"%(hex(pid),plength))
			data = s.recv(plength)
			# printBytesProperly(data)
			
			
	

if __name__ == "__main__":
	main()

