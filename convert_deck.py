from requests_oauthlib import OAuth1Session
import json
import io
import sys
import pickle
import os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def readDeckTable():  # dic読み込み
    if not os.path.isfile("deck.pickle"):
        return {}
    with open('deck.pickle', 'rb') as f:
        return pickle.load(f)


def writeDeckTable(dec):  # dic書き込み
    with open('deck.pickle', 'wb') as f:
        pickle.dump(dec, f)


def convert(url):  # convert
    data = {}
    url = url.replace("https://shadowverse-portal.com/deck/", "")
    data["deck"] = url.split(".")[2:]
    data["status"] = url.split(".")[:2]
    return data


deckTable = readDeckTable()
print(len(deckTable))

output = open('deck.dat', 'w')
for key in deckTable:
    deck = convert(deckTable[key])
    print(len(deck["deck"]))

    if len(deck["deck"]) != 40:
        continue

    output.write(" ".join(deck["deck"]) + "\n")
