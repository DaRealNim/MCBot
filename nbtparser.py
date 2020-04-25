import struct, socket

class NBTTag():
	def __init__(self, type):
		self.type = type
		self.name = None
		self.namelen = None
		
		self.value = None
		
		self.children = None
		if type in [7,9,10,11,12]:
			self.children = []
			
		self.parent = None
			
	def display_children(self, pad):
		if self.children == None:
			return
		print(pad+"%s (%d) %s"%(self.name, self.type, "="+str(self.value) if self.children==None else "(%d entries):"%len(self.children)))
		pad+="  "
		for i in self.children:
			print(pad+"%s (%d) %s"%(i.name, i.type, "="+str(i.value) if i.children==None else "(%d entries):"%len(i.children)))
			i.display_children(pad)
		
		

class NBTStruct():		
	def __init__(self):
		self.entry = None
		
	def printPretty(self):
		if self.entry == None:
			return
			
		print("")
		pad = ""
		print(pad+"%s (%d) %s"%(self.entry.name, self.entry.type,"(%d entries):"%len(self.entry.children)))
		pad += "  "
		for i in self.entry.children:
			i.display_children(pad)
		print("")
				
			
		
		
	def parseFromSocket(self, sock):
		compoundlayers = 0
		parenttag = None
		while True:
			typeid = struct.unpack(">B",sock.recv(1))[0]
			print("parsing %d"%typeid)
			
			tag = NBTTag(typeid)
			if typeid != 0:
				tag.namelen = struct.unpack(">H",sock.recv(2))[0]
				tag.name = sock.recv(tag.namelen).decode()
			tag.parent = parenttag
			
			if parenttag != None:
				parenttag.children.append(tag)
			
			if self.entry == None:
				self.entry = tag
			
			if typeid == 0:
				if not parenttag.type == 10:
					raise Exception("ERROR: TAG_End USED OUTSIDE OF TAG_Compound")
				
				compoundlayers -= 1
				if compoundlayers == 0:
					#parsing done! quitting
					break
					
			elif typeid == 1:
				tag.value = struct.unpack(">b", sock.recv(1))[0]
			elif typeid == 2:
				tag.value = struct.unpack(">h", sock.recv(2))[0]
			elif typeid == 3:
				tag.value = struct.unpack(">i", sock.recv(4))[0]
			elif typeid == 4:
				tag.value = struct.unpack(">q", sock.recv(8))[0]
			elif typeid == 5:
				tag.value = struct.unpack(">f", sock.recv(4))[0]
			elif typeid == 6:
				tag.value = struct.unpack(">d", sock.recv(8))[0]
			elif typeid == 7:
				prefix = struct.unpack(">i", sock.recv(4))[0]
				for i in range(prefix):
					ctag = NBTTag(1)
					ctag.value = struct.unpack(">b", sock.recv(1))[0]
					ctag.parent = tag
					tag.children.append(ctag)
			elif typeid == 8:
				strlen = struct.unpack(">H", sock.recv(2))[0]
				tag.value = sock.recv(strlen).decode()
			elif typeid == 9:
				ltype = struct.unpack(">B", sock.recv(1))[0]
				llen = struct.unpack(">i", sock.recv(4))[0]
				for i in range(llen):
					ctag = NBTTag(ltype)
					if ltype == 1:
						ctag.value = struct.unpack(">b", sock.recv(1))[0]
					elif ltype == 2:
						ctag.value = struct.unpack(">h", sock.recv(2))[0]
					elif ltype == 3:
						ctag.value = struct.unpack(">i", sock.recv(4))[0]
					elif ltype == 4:
						ctag.value = struct.unpack(">q", sock.recv(8))[0]
					elif ltype == 5:
						ctag.value = struct.unpack(">f", sock.recv(4))[0]
					elif ltype == 6:
						ctag.value = struct.unpack(">d", sock.recv(8))[0]
					elif ltype == 8:
						strlen = struct.unpack(">H", sock.recv(2))[0]
						ctag.value = sock.recv(strlen).decode()
					ctag.parent = tag
					tag.children.append(ctag)
			elif typeid == 10:
				parenttag = tag
				compoundlayers+=1
			elif typeid == 11:
				prefix = struct.unpack(">i", sock.recv(4))[0]
				for i in range(prefix):
					ctag = NBTTag(3)
					ctag.value = struct.unpack(">i", sock.recv(4))[0]
					ctag.parent = tag
					tag.children.append(ctag)
			elif typeid == 12:
				prefix = struct.unpack(">i", sock.recv(4))[0]
				print(prefix)
				for i in range(prefix):
					ctag = NBTTag(4)
					ctag.value = struct.unpack(">q", sock.recv(8))[0]
					ctag.parent = tag
					tag.children.append(ctag)