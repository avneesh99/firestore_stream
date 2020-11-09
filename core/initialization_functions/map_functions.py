from firebase_admin import firestore
from django.utils import timezone


def BuildAndSendMap(uid: str) -> bool:
    mappingSubTopics: dict[str, dict[str, dict[str, float]]] = {
        'Home': {
            'Finance': {'x': 0, 'y': 0, 'height': 0.25, 'width': 0.5},
            'India': {'x': 0.5, 'y': 0, 'height': 0.25, 'width': 0.5},

            'Music': {'x': 0, 'y': 0.25, 'height': 0.15, 'width': 0.33},
            'TV': {'x': 0.33, 'y': 0.25, 'height': 0.15, 'width': 0.34},
            'Gaming': {'x': 0.67, 'y': 0.25, 'height': 0.15, 'width': 0.33},

            'Sports': {'x': 0, 'y': 0.4, 'height': 0.25, 'width': 0.75},
            'World': {'x': 0.75, 'y': 0.4, 'height': 0.25, 'width': 0.25},

            'Science': {'x': 0.0, 'y': 0.65, 'height': 0.2, 'width': 0.5},
            'Tech': {'x': 0.5, 'y': 0.65, 'height': 0.2, 'width': 0.5},

            'Marketing': {'x': 0, 'y': 0.85, 'height': 0.15, 'width': 0.33},
            'History': {'x': 0.33, 'y': 0.85, 'height': 0.15, 'width': 0.34},
            'Random': {'x': 0.67, 'y': 0.85, 'height': 0.15, 'width': 0.33},
        },

        'Music': {
            'MusicGeneral': {'x': 0.0, 'y': 0.0, 'height': 1.0, 'width': 0.5},
            'Rap': {'x': 0.5, 'y': 0.0, 'height': 0.5, 'width': 0.5},
            'Rock': {'x': 0.5, 'y': 0.5, 'height': 0.5, 'width': 0.5},
        },

        'Sports': {
            'Cricket': {'x': 0.0, 'y': 0.0, 'height': 0.5, 'width': 0.5},
            'Football': {'x': 0.5, 'y': 0.0, 'height': 0.5, 'width': 0.5},

            'F1': {'x': 0.0, 'y': 0.5, 'height': 0.5, 'width': 0.33},
            'UFC': {'x': 0.33, 'y': 0.5, 'height': 0.5, 'width': 0.34},
            'Tennis': {'x': 0.67, 'y': 0.5, 'height': 0.5, 'width': 0.33},
        },

        'Tech': {
            'TechGeneral': {'x': 0.0, 'y': 0.0, 'height': 1.0, 'width': 0.5},
            'Coding': {'x': 0.5, 'y': 0.0, 'height': 1.0, 'width': 0.5}
        },

        'Coding': {
            'Python': {'x': 0.0, 'y': 0.0, 'height': 0.34, 'width': 0.5},
            'ML': {'x': 0.5, 'y': 0.0, 'height': 0.34, 'width': 0.5},
            'GoLang': {'x': 0.0, 'y': 0.34, 'height': 0.33, 'width': 0.5},
            'Flutter': {'x': 0.5, 'y': 0.34, 'height': 0.33, 'width': 0.5},
            'nodejs': {'x': 0.0, 'y': 0.67, 'height': 0.33, 'width': 0.5},
            'frontend': {'x': 0.5, 'y': 0.67, 'height': 0.33, 'width': 0.5},
        }
    }

    try:
        db = firestore.client()
        db.collection('Map').document(uid).set({
            'mappingSubTopics': mappingSubTopics
        })
        db.collection('Map').document(uid).collection('Coordinates').document('other').set({
            'onboardingStory':
                {
                    'xCoord': 0.70,
                    'yCoord': 0.4,
                    'viewed': False,
                    'publisherUsername': 'hotavneesh',
                    'publisherUid': 'DAi3ntCGIwZNr9OKhQ5dfljz2Q73',
                    'storyCreatedTime': timezone.now(),
                    'text': 'Hello! Please tap inside the box below',
                    'referencedPage': {
                        'media': {'link': None, 'previewLink': None, 'type': None},
                        'text': 'Click Here'
                    },
                    'referencedUsername': 'hotavneesh',
                    'referencedProfilePicture': 'https://firebasestorage.googleapis.com/v0/b/hota-e8550.appspot.com/o/profilePics%2FDAi3ntCGIwZNr9OKhQ5dfljz2Q73?alt=media&token=3e3ad93c-c100-4313-b869-9980fa6f6ece',
                    'referencedContentId': '0000Onboarding',
                    'ownStory': False
                }
        })
        db.collection('Map').document(uid).collection('Coordinates').document('self').set({})
    except Exception as e:
        print(f'Error in adding map: {e}')
        return False

    return True
