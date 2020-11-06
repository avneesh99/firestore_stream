from core.initialization_functions.content import ContentReserve
from core.models import ContentScoreModel
from datetime import timedelta
from django.utils import timezone
from django.db.models import Q


def GetContentReserveList(feedPreferenceDict: dict[str, str]) -> list[ContentReserve]:
    categoryList = [category
                    for category, preferenceValue in feedPreferenceDict.items()
                    if preferenceValue not in ['skipped', 'notAnswered']]

    categoryCriteria = Q(category__in=categoryList)
    timeCriteria = Q(time__gte=timezone.now() - timedelta(hours=24))
    goldCriteria = Q(level='gold')

    contentReserveList = [
        ContentReserve(
            contentId=item.id,
            category=GetModifiedCategory(category=item.category),
            level=item.level,
            rank=item.rank,
            time=item.time
        )
        for item in ContentScoreModel.objects.filter(
            categoryCriteria & (timeCriteria | goldCriteria)
        ).all()
    ]

    return contentReserveList


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
