import struct
import zlib
import socket

def pack_varint(number, max_bits=32):
	number_min = -1 << (max_bits - 1)
	number_max = +1 << (max_bits - 1)
	if not (number_min <= number < number_max):
		raise ValueError("varint does not fit in range: %d <= %d < %d"
						 % (number_min, number, number_max))

	if number < 0:
		number += 1 << 32

	out = b""
	for i in range(10):
		b = number & 0x7F
		number >>= 7
		out += struct.pack(">B", b | (0x80 if number > 0 else 0))
		if number == 0:
			break
	return out
		
		
def unpack_varint(sock, max_bits=32):
	number = 0
	for i in range(10):
		b = sock.recv(1)
		number |= (ord(b) & 0x7F) << 7*i
		if not ord(b) & 0x80:
			break

	if number & (1 << 31):
		number -= 1 << 32

	number_min = -1 << (max_bits - 1)
	number_max = +1 << (max_bits - 1)
	if not (number_min <= number < number_max):
		raise ValueError("varint does not fit in range: %d <= %d < %d"
						 % (number_min, number, number_max))

	return number
	
	
def craft_packet(packetid, data, compression=False):
	pid_b = pack_varint(packetid)
	if not compression:
		l = len(pid_b) + len(data)
		l_b = pack_varint(l)
		packet = l_b + pid_b + data
	else:
		datalength = len(pid_b)+len(data)
		
	return packet
		
		
def pack_string(str):
	return pack_varint(len(str)) + str.encode("utf-8")
	
def recv_string(sock):
	size = unpack_varint(sock)
	string = sock.recv(size).decode()
	return string