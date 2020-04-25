

class Player():
	def __init__(self, eid, gamemode, dimension):
		self.eid = eid
		self.gamemode = gamemode
		self.dimension = dimension
		self.x = 0
		self.y = 0
		self.z = 0
		self.yaw = 0
		self.pitch = 0
		
class ChunkSection():
	# self.blocks represents blocks from (inclusive):
	#    x: super().x*16 to super().x*16 + 15
	#    y: 16*self.id  to 16*self.id + 15
	#    z: super().z*16 to super().z*16 + 15
	def __init__(self):
		self.blocks = []
		self.id = -1 # to set, from 0 to 15
		
		
class Chunk():
	def __init__(self, x, z):
		self.x = x
		self.z = z
		self.coordToBlockMap = {} #coords stored as (x,y,z) tuple
		self.sections = [] #ChunkSections, in order (from 0 to 15)
		
		
		
class World():
	def __init__(self, hashedseed, leveltype, viewdistance, enablerespawnscreen):
		self.hashedseed = hashedseed
		self.leveltype = leveltype
		self.viewdistance = viewdistance
		self.enablerespawnscreen = enablerespawnscreen
		self.pluginchannel = ""
		self.plugindata = ""
		self.chunklist = []
		
	def getChunk(x, z):
		for i in self.chunklist:
			if i.x == x and i.y == y:
				return i
		return None


		
