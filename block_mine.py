import hashlib
import numpy as np
import pprint
import re
import sys
import time

__author__ = "Dennis Biber"

class CreateBlock(object):

	def __init__(self):
		super(CreateBlock, self)__init__()
		self.msg = {}

	def buildMsg(self, user, recipient, msgInput, tCount):
		encrypted_user = self.getEncryptUser(user)
		encrypted_recipient = self.getEncryptUser(recipient)
		msg = {"source_info": {"input": "${0}".format(msgInput),
							   "user": encrypted_user},
			   "recipient": encrypted_recipient}

		self.msg["msg{0}".format(tCount)] = msg
		pprint.pprint(self.msg)


	def generateArrays(self, startAmount, endAmount):
		npArray = np.arrange(startAmount, endAmount - 1, 1)
		new_msg = self.findHash(npArray)
			
		if new_msg == 0:
			return 0
		else:
			return(new_msg)

	def findHash(self, npArray):
		nounce = 0
		for x in npArray:
			print(x)
			new_msg = "{0}".format(self.msg) + str(x)
			encrpyt_msg = hashlib.sha256(new_msg.encode("utf-8")).hexdigest()
			if re.findall("^0000000000", encrpyt_msg):
				print(encrpyt_msg)
				nounce = encrpyt_msg[0:10]
				print(nounce)
				return encrpyt_msg
		return 0

	def getTime(self):
		return time.time()

	def getEncryptUser(self, user):
		return hashlib.sha256(user.encode("utf-8")).hexdigest()


def main():
	Block = CreateBlock()
	addInfo = False
	transactionCount =1
	while addInfo == False:
		user = input("Username: ")
		amount = input("Enter amount sending: ")
		if re.match("^[0-9]+", amount):
			msgInput = amount
		else: 
			print("Invaild amount")
			sys.exit()
		recipient = input("Enter recipient: ")
		addAnother = input("Do you want to add another transaction? (y/n)")
		Block.buildMsg(user, recipient, msgInput=msgInput, tCount=transactionCount)
		transactionCount += 1
		if addAnother == "n":
			addInfo = True
		elif addAnother == "y":
			pass
		else:
			print("Invalid response")
			sys.exit()
	arrayRange = [0, 100000000, 200000000, 300000000, 400000000]
	t0 = Block.getTime()
	for x in range(len(arrayRange)):
		found_hash = 0
		if arrayRange[x] == 0:
			pass
		else:
			found_hash = Block.generateArrays(arrayRange[x-1], arrayRange[x])
		if found_hash == 0:
			continue
		else:
			break
	t1 = Block.getTime()
	print(found_hash)
	print((t1-t0)*.001, "ms")


if __name__ == "__main__":
	main()