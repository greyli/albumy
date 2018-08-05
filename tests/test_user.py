# -*- coding: utf-8 -*-
"""
    :author: Grey Li (李辉)
    :url: http://greyli.com
    :copyright: © 2018 Grey Li <withlihui@gmail.com>
    :license: MIT, see LICENSE for more details.
"""
import io

from flask import url_for

from albumy.models import User, Photo
from albumy.settings import Operations
from albumy.utils import generate_token
from tests.base import BaseTestCase


class UserTestCase(BaseTestCase):

    def test_index_page(self):
        response = self.client.get(url_for('user.index', username='normal'))
        data = response.get_data(as_text=True)
        self.assertIn('Normal User', data)

        self.login(email='locked@helloflask.com', password='123')
        response = self.client.get(url_for('user.index', username='locked'))
        data = response.get_data(as_text=True)
        self.assertIn('Locked User', data)
        self.assertIn('Your account is locked.', data)

    def test_show_collections(self):
        response = self.client.get(url_for('user.show_collections', username='normal'))
        data = response.get_data(as_text=True)
        self.assertIn("Normal User's collection", data)
        self.assertIn('No collection.', data)

        user = User.query.get(2)
        user.collect(Photo.query.get(1))
        response = self.client.get(url_for('user.show_collections', username='normal'))
        data = response.get_data(as_text=True)
        self.assertNotIn('No collection.', data)

    def test_follow(self):
        response = self.client.post(url_for('user.follow', username='admin'), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Please log in to access this page.', data)

        self.login(email='unconfirmed@helloflask.com', password='123')
        response = self.client.post(url_for('user.follow', username='admin'), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Please confirm your account first.', data)

        self.logout()

        self.login()
        response = self.client.post(url_for('user.follow', username='admin'), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('User followed.', data)

        response = self.client.post(url_for('user.follow', username='admin'), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Already followed.', data)

        user = User.query.get(1)
        self.assertEqual(len(user.notifications), 1)

    def test_unfollow(self):
        response = self.client.post(url_for('user.follow', username='admin'), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Please log in to access this page.', data)

        self.login()
        response = self.client.post(url_for('user.unfollow', username='admin'), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Not follow yet.', data)

        self.client.post(url_for('user.follow', username='admin'), follow_redirects=True)

        response = self.client.post(url_for('user.unfollow', username='admin'), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('User unfollowed.', data)

    def test_show_followers(self):
        response = self.client.get(url_for('user.show_followers', username='normal'))
        data = response.get_data(as_text=True)
        self.assertIn('Normal User\'s followers', data)
        self.assertIn('No followers.', data)

        user = User.query.get(1)
        user.follow(User.query.get(2))

        response = self.client.get(url_for('user.show_followers', username='normal'))
        data = response.get_data(as_text=True)
        self.assertIn('Admin', data)
        self.assertNotIn('No followers.', data)

    def test_show_following(self):
        response = self.client.get(url_for('user.show_following', username='normal'))
        data = response.get_data(as_text=True)
        self.assertIn('Normal User\'s following', data)
        self.assertIn('No followings.', data)

        user = User.query.get(2)
        user.follow(User.query.get(1))

        response = self.client.get(url_for('user.show_following', username='normal'))
        data = response.get_data(as_text=True)
        self.assertIn('Admin', data)
        self.assertNotIn('No followers.', data)

    def test_edit_profile(self):
        self.login()
        response = self.client.post(url_for('user.edit_profile'), data=dict(
            username='newname',
            name='New Name',
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Profile updated.', data)
        user = User.query.get(2)
        self.assertEqual(user.name, 'New Name')
        self.assertEqual(user.username, 'newname')

    def test_change_avatar(self):
        self.login()
        response = self.client.get(url_for('user.change_avatar'))
        data = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Change Avatar', data)

    def test_upload_avatar(self):
        self.login()
        data = {'image': (io.BytesIO(b"abcdef"), 'test.jpg')}
        response = self.client.post(url_for('user.upload_avatar'), data=data, follow_redirects=True,
                                    content_type='multipart/form-data')
        data = response.get_data(as_text=True)
        self.assertIn('Image uploaded, please crop.', data)

    def test_change_password(self):
        user = User.query.get(2)
        self.assertTrue(user.validate_password('123'))

        self.login()
        response = self.client.post(url_for('user.change_password'), data=dict(
            old_password='123',
            password='new-password',
            password2='new-password',
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Password updated.', data)
        self.assertTrue(user.validate_password('new-password'))
        self.assertFalse(user.validate_password('old-password'))

    def test_change_email(self):
        user = User.query.get(2)
        self.assertEqual(user.email, 'normal@helloflask.com')
        token = generate_token(user=user, operation=Operations.CHANGE_EMAIL, new_email='new@helloflask.com')

        self.login()
        response = self.client.get(url_for('user.change_email', token=token), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Email updated.', data)
        self.assertEqual(user.email, 'new@helloflask.com')

        response = self.client.get(url_for('user.change_email', token='bad'), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Invalid or expired token.', data)

    def test_notification_setting(self):
        self.login()
        response = self.client.post(url_for('user.notification_setting'), data=dict(
            receive_collect_notification='',
            receive_comment_notification='',
            receive_follow_notification=''
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Notification settings updated.', data)

        user = User.query.get(2)

        self.assertEqual(user.receive_collect_notification, False)
        self.assertEqual(user.receive_comment_notification, False)
        self.assertEqual(user.receive_follow_notification, False)

        self.logout()
        self.login(email='admin@helloflask.com', password='123')
        self.client.post(url_for('user.follow', username='normal'))
        self.client.post(url_for('main.new_comment', photo_id=2), data=dict(body='test comment from admin user.'))
        self.client.post(url_for('main.collect', photo_id=2))
        self.assertEqual(len(user.notifications), 0)

    def test_privacy_setting(self):
        self.login()
        response = self.client.post(url_for('user.privacy_setting'), data=dict(
            public_collections='',
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Privacy settings updated.', data)

        user = User.query.get(2)

        self.assertEqual(user.public_collections, False)
        self.logout()
        response = self.client.get(url_for('user.show_collections', username='normal'))
        data = response.get_data(as_text=True)
        self.assertIn("Normal User's collection", data)
        self.assertIn('This user\'s collections was private.', data)

    def test_delete_account(self):
        self.login()
        response = self.client.post(url_for('user.delete_account'), data=dict(
            username='normal',
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Your are free, goodbye!', data)
        self.assertEqual(User.query.get(2), None)
