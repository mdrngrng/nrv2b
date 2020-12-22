import struct

def getbit(pos, recordDataEncoded, fourBytes, count):
	#Get the bit at position count. If count == 0, reinitialize count and move to next decompression.
	if count == 0:
		count = 31
		fourBytes = struct.unpack('<L', recordDataEncoded[pos:pos+4])[0]
		pos += 4
	else:
		count -= 1
	bit = ((fourBytes >> count ) & 1)
	return (bit, pos, fourBytes, count)

def decompress(recordDataEncoded):
	recordDataDecoded = b''
	sPos = 0
	dPos = 0
	lastMOff = 1
	shift = 0
	fourBytes = 0
	#Main Loop
	while True:
		if sPos >= len(recordDataEncoded):
			return recordDataDecoded
		(gb, sPos, fourBytes, shift) = getbit(sPos, recordDataEncoded, fourBytes, shift)
		while(gb != 0):
			recordDataDecoded += bytes([recordDataEncoded[sPos]])
			sPos += 1
			if sPos > len(recordDataEncoded):
				return recordDataDecoded
			dPos += 1
			(gb, sPos, fourBytes, shift) = getbit(sPos, recordDataEncoded, fourBytes, shift)
		#mOff calculation
		if sPos >= len(recordDataEncoded):
			return recordDataDecoded
		(gb, sPos, fourBytes, shift) = getbit(sPos, recordDataEncoded, fourBytes, shift)
		mOff = 2+gb
		if sPos >= len(recordDataEncoded):
			return recordDataDecoded
		(gb, sPos, fourBytes, shift) = getbit(sPos, recordDataEncoded, fourBytes, shift)
		while(gb == 0):
			if sPos >= len(recordDataEncoded):
				return recordDataDecoded
			(gb, sPos, fourBytes, shift) = getbit(sPos, recordDataEncoded, fourBytes, shift)
			mOff = 2*mOff + gb
			if sPos >= len(recordDataEncoded):
				return recordDataDecoded
			(gb, sPos, fourBytes, shift) = getbit(sPos, recordDataEncoded, fourBytes, shift)
		if mOff == 2:
			mOff = lastMOff
		else:
			mOff = (mOff - 3) * 256 + recordDataEncoded[sPos]
			sPos += 1
			if sPos > len(recordDataEncoded):
				return recordDataDecoded
			if int(mOff) == -1:
				break
			else:
				mOff += 1
				lastMOff = mOff
		#mLen calculation
		if sPos >= len(recordDataEncoded):
			return recordDataDecoded
		(mLen, sPos, fourBytes, shift) = getbit(sPos, recordDataEncoded, fourBytes, shift)
		if sPos >= len(recordDataEncoded):
			return recordDataDecoded
		(gb, sPos, fourBytes, shift) = getbit(sPos, recordDataEncoded, fourBytes, shift)
		mLen = mLen*2 + gb
		if mLen == 0:
			mLen += 1
			if sPos >= len(recordDataEncoded):
				return recordDataDecoded
			(gb, sPos, fourBytes, shift) = getbit(sPos, recordDataEncoded, fourBytes, shift)
			mLen = 2*mLen + gb
			if sPos >= len(recordDataEncoded):
				return recordDataDecoded
			(gb, sPos, fourBytes, shift) = getbit(sPos, recordDataEncoded, fourBytes, shift)
			while (gb == 0):
				if sPos >= len(recordDataEncoded):
					return recordDataDecoded
				(gb, sPos, fourBytes, shift) = getbit(sPos, recordDataEncoded, fourBytes, shift)
				mLen = 2*mLen + gb
				(gb, sPos, fourBytes, shift) = getbit(sPos, recordDataEncoded, fourBytes, shift)
			mLen += 2
		if mOff > 0xd00:
			mLen += 1
		mPos = dPos - mOff
		if mPos < 0:
			return recordDataDecoded
		if mPos > dPos:
			return recordDataDecoded
		#Copy uncompressed data
		recordDataDecoded += bytes([recordDataDecoded[mPos]])
		mPos += 1
		dPos += 1
		while mLen > 0:
			mLen -= 1
			recordDataDecoded += bytes([recordDataDecoded[mPos]])
			dPos += 1
			mPos += 1
	return recordDataDecoded