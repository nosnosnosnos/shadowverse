import argparse
import numpy as np
import json
import io
import sys
import pickle
import os
import copy
import random
import math
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
from operator import itemgetter
# sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def readDeckTable():
    if not os.path.isfile("deck.pickle"):
        return {}
    with open('deck.pickle', 'rb') as f:
        return pickle.load(f)


def onclick(event):
    print("event.button={0},  event.x={1}, event.y={2}, event.xdata={3} ,event.ydata={4}".format(
        event.button, event.x, event.y, event.xdata, event.ydata))
    y = event.ydata
    x = event.xdata

    mi = math.pow(2, 30)
    mi_index = 0
    for i in range(len(X)):
        buf = math.sqrt(math.pow(X[i][0] - x, 2) + pow(X[i][1] - y, 2))
        if mi > buf:
            mi = buf
            mi_index = i

    print(mi, mi_index)
    print(decks[mi_index].url)


class VectorLib:
    def __init__(self, path):
        self.card_vector = self.read_words_vector(path)

    def read_words_vector(self, path):
        vectors = {}
        num_lines = sum(1 for line in open(path))

        with open(path, "r", encoding="utf-8") as vec:
            for i, line in enumerate(vec):
                try:
                    elements = line.strip().split(" ")
                    word = elements[0]
                    vec = np.array(elements[1:], dtype=float)
                    if not word in vectors and len(vec) >= 100:
                        # ignore the case that vector size is invalid
                        vectors[word] = vec
                except ValueError:
                    continue
                except UnicodeDecodeError:
                    continue

        print("")
        return vectors

    def printVector(self):
        for k, v in self.card_vector.items():
            print("{0}_{1}".format(k, len(v)))

    def toVector(self, cards: list):
        vec = copy.deepcopy(list(self.card_vector.values())[0])
        vec *= 0

        for card in cards:
            if not card in self.card_vector:
                continue
                # raise Exception("{0} is missing".format(card))
            if vec.shape != self.card_vector[card].shape:
                # vec = self.card_vector[card]
                # print("reshape")
                continue
            vec += self.card_vector[card]
        return vec

    def similarity(slef, v1, v2):
        n1 = np.linalg.norm(v1)
        n2 = np.linalg.norm(v2)
        return np.dot(v1, v2) / n1 / n2

    def distance(slef, v1, v2):
        v = np.subtract(v1, v2)
        return np.linalg.norm(v)

    def evaluate(path, word, negative, threshold):
        if not word:
            raise Exception("word is missing")

        vectors = read_words_vector(path)

        if word not in vectors:
            raise Exception("Sorry, this word is not registered in model.")

        w_vec = vectors[word]
        candidates = {}

        for w in vectors:
            try:
                if w_vec.shape != vectors[w].shape:
                    raise Exception("size not match")
                s = distance(w_vec, vectors[w])
            except Exception as ex:
                print(w + " is not valid word.")
                continue

            candidates[w] = s

        sorted_candidates = sorted(
            candidates, key=candidates.get, reverse=True)
        count = 0
        for c in sorted_candidates:
            print("{0}, {1}".format(c, candidates[c]))
            count += 1
            if count > 100:
                break


class Deck:
    def __init__(self, url: str, vl: VectorLib):
        # if len(data) != 42:
            # raise Exception("dataformat err")
        self.url = url
        data = url.replace(
            "https://shadowverse-portal.com/deck/", "").split(".")
        self.cards = data[2:]
        self.charaID = data[:2]

        self.vec = vl.toVector(self.cards)

    def getCards(self):
        return self.cards

    def getCharaID(self):
        return self.charaID

    def getCharaIdHash(self):
        return self.charaID[0] * 10 + self.charaID[1]

    def getVec(self):
        return self.vec

    def range(self):
        return np.linalg.norm(self.vec)


X_data = []

if __name__ == "__main__":
    # vector読み込み
    vl = VectorLib("model.vec")

    # デッキデータ読み込み
    decks = []
    deck_vecs = []
    deck_ids = []
    pic = readDeckTable()
    for v in pic.values():
        deck = Deck(v, vl)

        # 30枚のとか混じっているので除去
        if len(deck.getCards()) != 40:
            continue

        decks.append(deck)
        deck_vecs.append(deck.getVec())
        deck_ids.append(deck.getCharaIdHash())

    # numpy + tsne
    deck_np = np.array(deck_vecs)
    deck_id = np.array(deck_ids)
    model = TSNE(n_components=2, perplexity=80,
                 n_iter=500, verbose=3, random_state=100)
    X = model.fit_transform(deck_np)
    X_data = X

    # Plot the points
    plt.figure(1, figsize=(8, 6)).canvas.mpl_connect(
        'button_press_event', onclick)
    plt.clf()
    plt.scatter(X[:, 0], X[:, 1], c=deck_id,
                cmap=plt.cm.Paired, alpha=0.7, s=10)
    plt.xlabel('tsne1')
    plt.ylabel('tsne2')

    plt.show()
