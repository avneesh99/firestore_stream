from datetime import datetime


class Media:
    def __init__(self, link: str, previewLink: str, mediaType: str):
        self.link = link
        self.previewLink = previewLink
        self.mediaType = mediaType


class Page:
    def __init__(self, text: str, media: Media):
        self.text = text
        self.media = media


class Content:
    def __init__(self, contentId: str, category: str, score: int, time: datetime, url: str, twitterHandle: str,
                 contentType: str, profilePicture: str, level: str,
                 firestoreMapList: list[Page]):
        self.contentId = contentId
        self.category = category
        self.score = score
        self.time = time
        self.url = url
        self.twitterHandle = twitterHandle
        self.contentType = contentType
        self.profilePicture = profilePicture
        self.level = level
        self.firestoreMapList = firestoreMapList


class ContentReserve:
    def __init__(self, contentId, time, category, level, rank):
        self.contentId = contentId
        self.time = time
        self.category = category
        self.level = level
        self.rank = rank
