from django.core.management.base import BaseCommand
from django.utils import timezone

import firebase_admin
from firebase_admin import credentials, firestore
from time import sleep

from core.initialization_functions.main_function import onboarding_queue_on_snapshot
from core.sharing_story_functions.main_function import sharing_queue_on_snapshot
from core.social_functions.main_function import following_queue_on_snapshot
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

        # sharing_queue_col_ref = db.collection(u'SharingQueue')
        # sharing_queue_col_ref.on_snapshot(sharing_queue_on_snapshot)

        onboarding_queue_col_ref = db.collection(u'OnboardingQueue')
        onboarding_queue_col_ref.on_snapshot(onboarding_queue_on_snapshot)

        # following_queue_col_ref = db.collection(u'FollowingQueue')
        # following_queue_col_ref.on_snapshot(following_queue_on_snapshot)
        #
        # story_action_queue_col_ref = db.collection(u'StoryActionQueue')
        # story_action_queue_col_ref.on_snapshot(story_action_queue_on_snapshot)

        while True:
            print(f'processing @ {timezone.now()}!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
            sleep(300)


