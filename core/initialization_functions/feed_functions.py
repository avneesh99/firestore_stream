from core.initialization_functions.content import Content, ContentReserve
from core.initialization_functions.content_reserve_list import GetContentReserveList
from core.initialization_functions.firestore_functions import SendingTotalFeedListToFirestore, \
    EditFeedPreferenceCollection, AddToContentReserveCollection
from core.initialization_functions.total_feed_list import BuildTotalFeedList


def BuildAndSendFeed(userUid: str, rawFeedPreferenceDict: dict[str, list[str]]):
    cacheContentDetailsDict: dict[str, Content] = {}

    feedPreferenceDict = BuildFeedPreferenceDict(rawFeedPreferenceDict=rawFeedPreferenceDict)

    contentReserveList: list[ContentReserve] = GetContentReserveList(feedPreferenceDict=feedPreferenceDict)

    totalFeedList = BuildTotalFeedList(
        contentReserveList=contentReserveList,
        cacheContentDetailsDict=cacheContentDetailsDict,
        feedPreferenceDict=feedPreferenceDict,
    )

    result = SendingTotalFeedListToFirestore(
        totalFeedList=totalFeedList,
        userUid=userUid
    )

    AddToContentReserveCollection(userUid=userUid, contentReserveList=contentReserveList)

    EditFeedPreferenceCollection(uid=userUid, initialFeedPreferenceDict=feedPreferenceDict)


def BuildFeedPreferenceDict(rawFeedPreferenceDict: dict[str, list[str]]) -> dict[str, str]:
    feedPreferenceDict: dict[str, str] = {}

    if 'coding' in rawFeedPreferenceDict.keys():
        feedPreferenceDict['coding'] = rawFeedPreferenceDict['coding'][0]
    else:
        feedPreferenceDict['coding'] = 'notAnswered'

    if 'finance' in rawFeedPreferenceDict.keys():
        feedPreferenceDict['finance'] = rawFeedPreferenceDict['finance'][0]
    else:
        feedPreferenceDict['finance'] = 'notAnswered'

    if 'football' in rawFeedPreferenceDict.keys():
        feedPreferenceDict['football'] = rawFeedPreferenceDict['football'][0]
    else:
        feedPreferenceDict['football'] = 'notAnswered'

    if 'indPolitics' in rawFeedPreferenceDict.keys():
        feedPreferenceDict['indPolitics'] = rawFeedPreferenceDict['indPolitics'][0]
        feedPreferenceDict['india'] = 'medium'
    else:
        feedPreferenceDict['indPolitics'] = 'notAnswered'
        feedPreferenceDict['india'] = 'low'

    if 'cricket' in rawFeedPreferenceDict.keys():
        feedPreferenceDict['cricket'] = rawFeedPreferenceDict['cricket'][0]
    else:
        feedPreferenceDict['cricket'] = 'notAnswered'

    feedPreferenceDict['tv'] = 'rare'
    feedPreferenceDict['world'] = 'low'
    feedPreferenceDict['marketing'] = 'rare'
    feedPreferenceDict['history'] = 'rare'
    feedPreferenceDict['random'] = 'rare'
    feedPreferenceDict['indNonPolitics'] = 'high'

    if 'tech' in rawFeedPreferenceDict.keys():
        if feedPreferenceDict['coding'] not in ['notAnswered', 'skipped']:
            feedPreferenceDict['tech'] = 'high'
        else:
            feedPreferenceDict['tech'] = rawFeedPreferenceDict['tech'][0]
    else:
        feedPreferenceDict['tech'] = 'notAnswered'

    if 'market' in rawFeedPreferenceDict.keys():
        feedPreferenceDict['market'] = rawFeedPreferenceDict['market'][0]
        if feedPreferenceDict['market'] == 'skipped':
            feedPreferenceDict['market'] = 'medium'
    else:
        feedPreferenceDict['market'] = 'skipped'

    for item in ['python', 'flutter', 'golang', 'nodejs', 'ml', 'frontend']:
        feedPreferenceDict[item] = 'skipped'
    if 'codingTech' in rawFeedPreferenceDict.keys():
        for i in rawFeedPreferenceDict['codingTech']:
            feedPreferenceDict[i] = 'high'

    for item in ['f1', 'ufc', 'tennis']:
        feedPreferenceDict[item] = 'skipped'
    if 'otherSports' in rawFeedPreferenceDict.keys():
        for i in rawFeedPreferenceDict['otherSports']:
            feedPreferenceDict[i] = 'medium'

    for item in ['music', 'rock', 'rap']:
        feedPreferenceDict[item] = 'skipped'
    for item in rawFeedPreferenceDict['music']:
        feedPreferenceDict[item] = 'high'
        feedPreferenceDict['music'] = 'low'

    if feedPreferenceDict['tech'] == 'high':
        feedPreferenceDict['gaming'] = 'rare'
        feedPreferenceDict['science'] = 'rare'
    else:
        feedPreferenceDict['gaming'] = 'skipped'
        feedPreferenceDict['science'] = 'skipped'

    return feedPreferenceDict
