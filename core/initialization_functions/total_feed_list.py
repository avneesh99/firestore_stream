from core.initialization_functions.content import ContentReserve, Content
from core.initialization_functions.firestore_functions import UpdateCacheContentDetailsDict


def BuildTotalFeedList(contentReserveList: list[ContentReserve], cacheContentDetailsDict: [str, Content],
                       feedPreferenceDict: dict[str, str]) -> list[Content]:

    categoryWiseContentReserveDict: dict[str, dict[str, list[ContentReserve]]] = {}
    for contentReserveObj in contentReserveList:
        if contentReserveObj.category not in categoryWiseContentReserveDict.keys():
            categoryWiseContentReserveDict[contentReserveObj.category] = {
                'high': [], 'low': [], 'gold': []
            }
        categoryWiseContentReserveDict[contentReserveObj.category][contentReserveObj.level].append(contentReserveObj)

    # Sorting the list with increasing rank
    for category, value in categoryWiseContentReserveDict.items():
        for level, levelWiseContentReserveList in value.items():
            levelWiseContentReserveList.sort(key=lambda x: x.rank)

    categoryList = [x for x in categoryWiseContentReserveDict.keys()]
    skeletonFeedList: list[dict[str, str]] = GenerateSkeletonFeedList(
        feedPreferenceDict=feedPreferenceDict,
        categoryList=categoryList)

    loopCounter = 0
    missedCounter = 0
    totalFeedList: list[Content] = []
    levelMap = {
        'high': ['high', 'low', 'gold'],
        'low': ['low', 'gold'],
        'gold': ['gold', 'low', 'high']
    }
    # loop till either we reach 100 content or we miss > half of categories
    while len(totalFeedList) <= 100 and missedCounter < len(categoryWiseContentReserveDict.keys()) / 2:
        category, level = skeletonFeedList[loopCounter % len(skeletonFeedList)]['category'], \
                          skeletonFeedList[loopCounter % len(skeletonFeedList)]['level']

        for item in levelMap[level]:
            levelWiseContentReserveList = categoryWiseContentReserveDict[category][item]
            if len(levelWiseContentReserveList) > 0:
                contentReserveObj = levelWiseContentReserveList.pop(0)
                try:
                    totalFeedList.append(
                        ConvertContentReserveToContent(contentId=contentReserveObj.contentId,
                                                       cacheContentDetailsDict=cacheContentDetailsDict)
                    )
                    missedCounter = 0
                    break
                except Exception as e:
                    print(f"error while converting ContentReserve to Content: {e}")
        else:
            missedCounter += 1

        loopCounter += 1

    # need to transfer leftover content from categoryWiseContentReserveDict to contentReserveList
    # used [:] because it will change the original list without creating a new one
    contentReserveList[:] = [
        contentReserveObj
        for category, value in categoryWiseContentReserveDict.items()
        for level, levelWiseContentReserveList in value.items()
        for contentReserveObj in levelWiseContentReserveList
    ]

    return totalFeedList


def GenerateSkeletonFeedList(feedPreferenceDict: dict[str, str], categoryList: list[str]) -> list[dict[str, str]]:
    preferenceValueMapping: dict[str, list[str]] = {
        'skipped': [],
        'notAnswered': [],
        'rare': ['gold', 'low'],
        'low': ['low', 'gold', 'low', 'gold'],
        'medium': ['low', 'high', 'gold', 'low', 'high', 'gold', 'low', 'high'],
        'high': ['low', 'high', 'gold', 'low', 'high', 'gold', 'low', 'high', 'gold', 'low', 'high',
                 'gold', 'low', 'high', 'gold', 'low']
    }

    preferenceOrder = {'high': 0, 'medium': 1, 'low': 2, 'rare': 3, 'notAnswered': 4, 'skipped': 5}
    categoryList = sorted(categoryList, key=lambda x: preferenceOrder[feedPreferenceDict[x]])

    totalLengthOfSkeletonFeedList = 0
    for category in categoryList:
        feedPreferenceValue = feedPreferenceDict[category]
        totalLengthOfSkeletonFeedList += len(preferenceValueMapping[feedPreferenceValue])

    skeletonFeedList: list = [None] * (totalLengthOfSkeletonFeedList * 2)

    for category in categoryList:
        preferenceValue = feedPreferenceDict[category]
        if len(preferenceValueMapping[preferenceValue]) == 0:
            continue
        skip: int = int(totalLengthOfSkeletonFeedList / len(preferenceValueMapping[preferenceValue]))
        idx: int = 0
        for level in preferenceValueMapping[preferenceValue]:
            while True:
                if skeletonFeedList[idx] is None:
                    skeletonFeedList[idx] = {'category': category, 'level': level}
                    idx += skip
                    break
                else:
                    idx += 1

    skeletonFeedList[:] = [x for x in skeletonFeedList if x is not None]

    return skeletonFeedList


def ConvertContentReserveToContent(contentId, cacheContentDetailsDict: dict[str, Content]) -> Content:
    if contentId not in cacheContentDetailsDict.keys():
        # Since this particular content is missing so we request it from firestore
        UpdateCacheContentDetailsDict(contentId=contentId, cacheContentDetailsDict=cacheContentDetailsDict)

    return cacheContentDetailsDict[contentId]
