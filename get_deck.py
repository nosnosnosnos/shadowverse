from requests_oauthlib import OAuth1Session
import json
import io
import sys
import pickle
import os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

api_key = "********************"
api_secret = "********************"
access_token = "********************"
access_secret = "********************"

twitter = OAuth1Session(api_key, api_secret, access_token, access_secret)

# API残り制限を確認


def canSearchAPI():
    req = twitter.get(
        "https://api.twitter.com/1.1/application/rate_limit_status.json")

    try:
        count = json.loads(req.text)[
            'resources']['users']['/users/search']['remaining']
    except KeyError:
        print(json.loads(req.text))
        sys.exit(1)

    print("api_remaining:" + str(count))
    return json.loads(req.text)['resources']['users']['/users/search']['remaining'] > 0

# dic読み込み


def readDeckTable():
    if not os.path.isfile("deck.pickle"):
        return {}
    with open('deck.pickle', 'rb') as f:
        return pickle.load(f)

# dic書き込み


def writeDeckTable(dec):
    with open('deck.pickle', 'wb') as f:
        pickle.dump(dec, f)


deckTable = readDeckTable()
print(len(deckTable))

# すべてのTLを取得する
params = {"q": "#shadowverse_deck", "count": 100}

# 総取得数
get_count = 0
while True:
    # 取得
    req = twitter.get(
        "https://api.twitter.com/1.1/search/tweets.json", params=params)
    timeline = json.loads(req.text)

    if 'errors' in timeline:
        print(timeline)
        break

    for tweet in timeline['statuses']:

        for url in tweet['entities']['urls']:
            print(url['expanded_url'])

            # 目的のURLかどうか
            if not url['expanded_url'].startswith("https://shadowverse-portal.com/deck/"):
                continue

            # テーブルに格納
            deckTable[tweet["id"]] = url['expanded_url']

        params["max_id"] = tweet["id"]

    print(len(timeline['statuses']))
    get_count += len(timeline['statuses'])

    # if len(timeline['statuses']) != params["count"]:
    #     break

print(get_count)
writeDeckTable(deckTable)
