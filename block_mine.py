import hashlib
import json
import numpy as np
import pprint
import re
import string
import sys
import time

__author__ = "Dennis Biber"

class CreateBlock(object):

    def __init__(self):
        super(CreateBlock, self).__init__()
        self.msg = ""

    def buildMsg(self, user, recipient, msgInput, tCount):
        stackedMsg = ""
        encrypted_user = self.getEncrypt(user)
        encrypted_recipient = self.getEncrypt(recipient)

        msg = f"input: {msgInput}, user: {encrypted_user}, recipient: {encrypted_recipient}, blockId: 000000001000"
        stackedMsg = f"msg{tCount}: " + msg
        self.msg = "\n" + stackedMsg
        pprint.pprint(self.msg)
        time.sleep(2)


    def findHash(self, x, coin):
        nonce = 0
        print(x)
        new_msg = json.dumps(self.msg) + str(x)
        encrpyt_msg = self.getEncrypt(new_msg)
        encryptCoin = self.getEncrypt(coin)
        if re.findall(f"^{coin}", encrpyt_msg):
            print(encrpyt_msg)
            time.sleep(2)
            nonce = encrpyt_msg[0:8]
            print(nonce)
            return encrpyt_msg
        return 0

    def getTime(self):
        return time.time()

    def getEncrypt(self, value):
        return hashlib.sha256(value.encode("utf-8")).hexdigest()


def getCurrencyType(question):
    coincrypt = ""
    abet = string.ascii_lowercase + string.ascii_uppercase
    coin = input(question)
    for value in coin:
        idx = abet.index(value)
        if len(f"{idx}") < 2:
            idx = f"{idx}" + "0"
        else:
            idx = f"{idx}"
        coincrypt = coincrypt + idx
    if len(coincrypt) == 6:
        coincrypt = "00" + coincrypt
    elif len(coincrypt) == 8:
        pass
    else:
        raise ValueError("Invalid currency type. Currency must contain 3 or 4 characters.")
    return coincrypt


def main():
    Block = CreateBlock()
    addInfo = False
    transactionCount =1
    while addInfo == False:
        currencyType = input("Buying coin from crypto or fiat? ")
        if currencyType == "crypto":
            coin = getCurrencyType("What coin are you selling? (Please gave 3-4 character name (example: BTC)) ")
        elif currencyType == "fiat":
            coin = getCurrencyType("What fiat are you selling? (Please give 3-4 character name (example: USD) ")
        else:
            raise ValueError("The currency type does not match crypto or fiat correctly.")
        user = input("Username: ")
        amount = input("Enter amount sending: ")
        if re.match("^[0-9]+", amount):
            msgInput = amount
        else:
            raise ValueError("Invalid amount")
        recipient = input("Enter recipient: ")
        addAnother = input("Do you want to add another transaction? (y/n)")
        Block.buildMsg(user, recipient, msgInput=msgInput, tCount=transactionCount)
        transactionCount += 1
        if addAnother == "n":
            addInfo = True
        elif addAnother == "y":
            pass
        else:
            raise ValueError("Invalid response")
    arraySecondLayers = np.arange(0, 10000000000, 1000000000)
    arrayRange = np.arange(0, 1000000000, 100000000)
    arraySubRange = np.arange(0, 100000000, 1)
    t0 = Block.getTime()
    found_hash = 0
    for x in arraySecondLayers:
        for y in arrayRange:
            for z in arraySubRange:
                value = x + y + z
                if z == 0:
                    pass
                else:
                    found_hash = Block.findHash(value, coin)
                if found_hash == 0:
                    continue
                else:
                    break
            if found_hash != 0:
                break
    t1 = Block.getTime()
    print(found_hash)
    print((t1-t0))


if __name__ == "__main__":
    main()