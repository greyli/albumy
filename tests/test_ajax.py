# -*- coding: utf-8 -*-
"""
    :author: Grey Li (李辉)
    :url: http://greyli.com
    :copyright: © 2018 Grey Li <withlihui@gmail.com>
    :license: MIT, see LICENSE for more details.
"""
from flask import url_for

from albumy.models import User, Photo
from tests.base import BaseTestCase


class AjaxTestCase(BaseTestCase):

    def test_notifications_count(self):
        response = self.client.get(url_for('ajax.notifications_count'))
        data = response.get_json()
        self.assertEqual(response.status_code, 403)
        self.assertEqual(data['message'], 'Login required.')

        self.login()
        response = self.client.get(url_for('ajax.notifications_count'))
        self.assertEqual(response.status_code, 200)

    def test_get_profile(self):
        response = self.client.get(url_for('ajax.get_profile', user_id=1))
        data = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Admin', data)

    def test_followers_count(self):
        response = self.client.get(url_for('ajax.followers_count', user_id=1))
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['count'], 0)

        user = User.query.get(2)
        user.follow(User.query.get(1))

        response = self.client.get(url_for('ajax.followers_count', user_id=1))
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['count'], 1)

    def test_collectors_count(self):
        response = self.client.get(url_for('ajax.collectors_count', photo_id=1))
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['count'], 0)

        user = User.query.get(1)
        user.collect(Photo.query.get(1))

        response = self.client.get(url_for('ajax.collectors_count', photo_id=1))
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['count'], 1)

    def test_collect(self):
        response = self.client.post(url_for('ajax.collect', photo_id=1))
        data = response.get_json()
        self.assertEqual(response.status_code, 403)
        self.assertEqual(data['message'], 'Login required.')

        self.login(email='unconfirmed@helloflask.com', password='123')
        response = self.client.post(url_for('ajax.collect', photo_id=1))
        data = response.get_json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['message'], 'Confirm account required.')
        self.logout()

        self.login()
        response = self.client.post(url_for('ajax.collect', photo_id=1))
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['message'], 'Photo collected.')

        response = self.client.post(url_for('ajax.collect', photo_id=1))
        data = response.get_json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['message'], 'Already collected.')

    def test_uncollect(self):
        response = self.client.post(url_for('ajax.uncollect', photo_id=1))
        data = response.get_json()
        self.assertEqual(response.status_code, 403)
        self.assertEqual(data['message'], 'Login required.')

        self.login()
        response = self.client.post(url_for('ajax.uncollect', photo_id=1))
        data = response.get_json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['message'], 'Not collect yet.')

        user = User.query.get(2)
        user.collect(Photo.query.get(1))

        response = self.client.post(url_for('ajax.uncollect', photo_id=1))
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['message'], 'Collect canceled.')

    def test_follow(self):
        response = self.client.post(url_for('ajax.follow', username='admin'))
        data = response.get_json()
        self.assertEqual(response.status_code, 403)
        self.assertEqual(data['message'], 'Login required.')

        self.login(email='unconfirmed@helloflask.com', password='123')
        response = self.client.post(url_for('ajax.follow', username='admin'))
        data = response.get_json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['message'], 'Confirm account required.')
        self.logout()

        self.login()
        response = self.client.post(url_for('ajax.follow', username='normal'))
        data = response.get_json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['message'], 'Already followed.')

        response = self.client.post(url_for('ajax.follow', username='admin'))
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['message'], 'User followed.')

    def test_unfollow(self):
        response = self.client.post(url_for('ajax.unfollow', username='admin'))
        data = response.get_json()
        self.assertEqual(response.status_code, 403)
        self.assertEqual(data['message'], 'Login required.')

        self.login()
        response = self.client.post(url_for('ajax.unfollow', username='admin'))
        data = response.get_json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['message'], 'Not follow yet.')

        user = User.query.get(2)
        user.follow(User.query.get(1))

        response = self.client.post(url_for('ajax.unfollow', username='admin'))
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['message'], 'Follow canceled.')
