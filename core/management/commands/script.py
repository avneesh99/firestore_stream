from django.core.management.base import BaseCommand
from django.utils import timezone

import firebase_admin
from firebase_admin import credentials, firestore
from time import sleep

from core.initialization_functions.main import OnboardingQueueOnSnapshot
from core.sharing_story_functions.main_function import SharingQueueOnSnapshot
from core.social_functions.main_function import FollowingQueueOnSnapshot
from core.story_action_functions.main_function import story_action_queue_on_snapshot
from firestore_stream.firebase_cred import firestore_cred_data


class Command(BaseCommand):
    def handle(self, *args, **options):
        print('Starting script.py........................')
        print('\n')
        print('\n')

        cred = credentials.Certificate(firestore_cred_data)
        firebase_admin.initialize_app(cred)
        db = firestore.client()

        print('Connection Initialised')

        sharingQueueColRef = db.collection(u'SharingQueue')
        sharingQueueColRef.on_snapshot(SharingQueueOnSnapshot)

        onboardingQueueColRef = db.collection(u'OnboardingQueue')
        onboardingQueueColRef.on_snapshot(OnboardingQueueOnSnapshot)

        followingQueueColRef = db.collection(u'FollowingQueue')
        followingQueueColRef.on_snapshot(FollowingQueueOnSnapshot)

        story_action_queue_col_ref = db.collection(u'StoryActionQueue')
        story_action_queue_col_ref.on_snapshot(story_action_queue_on_snapshot)

        while True:
            print(f'processing @ {timezone.now()}!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
            sleep(300)
