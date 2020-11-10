from firebase_admin import firestore
from django.utils import timezone

from core.initialization_functions.content import Content, Page, Media, ContentReserve


def UpdateCacheContentDetailsDict(contentId: str, cacheContentDetailsDict: dict[str, Content]):
    db = firestore.client()
    contentDoc = db.collection('Content').document(contentId).get()
    if contentDoc.exists:
        contentDict = contentDoc.to_dict()
        cacheContentDetailsDict[contentId] = ConvertContentDictToObj(contentDict=contentDict)


def ConvertContentDictToObj(contentDict: dict):
    return Content(
        contentId=contentDict['contentId'],
        score=contentDict['score'],
        time=contentDict['time'],
        category=contentDict['category'],
        level=contentDict['level'],
        url=contentDict['url'],
        twitterHandle=contentDict['user']['username'],
        profilePicture=contentDict['user']['profilePicture'],
        firestoreMapList=ConvertPagesToFirestoreMapList(contentDict['pages']),
        contentType=contentDict['type']
    )


def ConvertPagesToFirestoreMapList(pages: list[dict]) -> list[Page]:
    return [
        Page(
            text=page['text'],
            media=Media(
                link=page['media']['link'],
                previewLink=page['media']['previewLink'],
                mediaType=page['media']['type']
            )
        ) for page in pages
    ]


def SendingTotalFeedListToFirestore(totalFeedList: list[Content], userUid: str) -> bool:
    db = firestore.client()
    newsfeedColRef = db.collection('UserFeed').document(userUid).collection('NewsFeed')
    i = 0
    try:
        while (i * 10) < len(totalFeedList):
            newsfeedColRef.document(f"feed_{DocumentNameFromIndex(i)}").set({
                'contentList': firestore.ArrayUnion([
                    ConvertContentObjToDict(contentObject=contentObject)
                    for contentObject in totalFeedList[i * 10: (i + 1) * 10]
                ])
            })
            i += 1

        # Delete the documents which were not modified
        # if feed_11 doesn't exist this means feed_12,feed_13,etc will also not exist as we are filling sequentially
        while True:
            i += 1
            if newsfeedColRef.document(f"feed_{DocumentNameFromIndex(i)}").get().exists:
                newsfeedColRef.document(f"feed_{DocumentNameFromIndex(i)}").delete()
            else:
                break

        return True

    except Exception as e:
        for x in [
            ConvertContentObjToDict(contentObject=contentObject)
            for contentObject in totalFeedList[i * 10: (i + 1) * 10]
        ]:
            print(x)
            print('\n')
        print(f"Error while sending the feedList to firestore: {e}")
        return False


def DocumentNameFromIndex(idx: int):
    if idx < 10:
        return f"0{idx}"
    else:
        return f"{idx}"


def ConvertContentObjToDict(contentObject: Content) -> dict:
    return {
        'contentId': contentObject.contentId,
        'score': contentObject.score,
        'time': contentObject.time,
        'category': contentObject.category,
        'level': contentObject.level,
        'url': contentObject.url,
        'user': {'username': contentObject.twitterHandle, 'profilePicture': contentObject.profilePicture},
        'pages': ConvertFirestoreMapListToList(firestoreMapList=contentObject.firestoreMapList),
        'type': contentObject.contentType
    }


def ConvertFirestoreMapListToList(firestoreMapList: list[Page]) -> list[dict]:
    pages: list[dict] = []
    for page in firestoreMapList:
        pages.append({
            'text': page.text,
            'media': {
                'link': page.media.link,
                'previewLink': page.media.previewLink,
                'type': page.media.mediaType
            }
        })

    return pages


def EditFeedPreferenceCollection(uid: str, initialFeedPreferenceDict: dict):
    db = firestore.client()
    db.collection('FeedPreference').document(uid).set({
        'InitialPreference': initialFeedPreferenceDict,
        'LastUpdated': timezone.now(),
        'LastFannedOut': timezone.now()
    })


def AddToContentReserveCollection(contentReserveList: list[ContentReserve], userUid: str):
    db = firestore.client()
    finalDict = {}
    for contentReserveObj in contentReserveList:
        finalDict[contentReserveObj.contentId] = GetModifiedCategory(category=contentReserveObj.category)

    db.collection('ContentReserve').document(userUid).set(finalDict)


def GetModifiedCategory(category: str):
    # Content and ContentReserve collection will have category a different category
    # Like 'flutter' will be 'coding' there.
    # Original category will only remain in postgres db: contentScoreModel
    categoryMap = {
        'coding': ['flutter', 'golang', 'python', 'ml', 'nodejs', 'frontend'],
        'music': ['rock', 'rap'],
        'india': ['indPolitics', 'indNonPolitics']
    }
    for key, value in categoryMap.items():
        if category in value:
            return key

    return category
