# -*- coding: utf-8 -*-
"""
    :author: Grey Li (李辉)
    :url: http://greyli.com
    :copyright: © 2018 Grey Li <withlihui@gmail.com>
    :license: MIT, see LICENSE for more details.
"""
from flask import url_for

from albumy.extensions import db
from albumy.models import User, Role, Tag
from tests.base import BaseTestCase


class AdminTestCase(BaseTestCase):

    def setUp(self):
        super(AdminTestCase, self).setUp()
        self.login(email='admin@helloflask.com', password='123')

    def test_index_page(self):
        response = self.client.get(url_for('admin.index'))
        data = response.get_data(as_text=True)
        self.assertIn('Albumy Dashboard', data)

    def test_bad_permission(self):
        self.logout()
        response = self.client.get(url_for('admin.index'), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Please log in to access this page.', data)
        self.assertNotIn('Albumy Dashboard', data)

        self.login()  # normal user, without MODERATOR permission
        response = self.client.get(url_for('admin.index'))
        data = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 403)
        self.assertNotIn('Albumy Dashboard', data)

    def test_edit_profile_admin(self):
        role_id = Role.query.filter_by(name='Locked').first().id
        response = self.client.post(url_for('admin.edit_profile_admin', user_id=2), data=dict(
            username='newname',
            role=role_id,
            confirmed=True,
            active=True,
            name='New Name',
            email='new@helloflask.com'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Profile updated.', data)
        user = User.query.get(2)
        self.assertEqual(user.name, 'New Name')
        self.assertEqual(user.username, 'newname')
        self.assertEqual(user.email, 'new@helloflask.com')
        self.assertEqual(user.role.name, 'Locked')

    def test_block_user(self):
        response = self.client.post(url_for('admin.block_user', user_id=2), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Account blocked.', data)
        user = User.query.get(2)
        self.assertEqual(user.active, False)

    def test_unblock_user(self):
        user = User.query.get(2)
        user.active = False
        db.session.commit()
        self.assertEqual(user.active, False)

        response = self.client.post(url_for('admin.unblock_user', user_id=2), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Block canceled.', data)
        user = User.query.get(2)
        self.assertEqual(user.active, True)

    def test_lock_user(self):
        response = self.client.post(url_for('admin.lock_user', user_id=2), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Account locked.', data)
        user = User.query.get(2)
        self.assertEqual(user.role.name, 'Locked')

    def test_unlock_user(self):
        user = User.query.get(2)
        user.role = Role.query.filter_by(name='Locked').first()
        db.session.commit()
        self.assertEqual(user.role.name, 'Locked')

        response = self.client.post(url_for('admin.unlock_user', user_id=2), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Lock canceled.', data)
        user = User.query.get(2)
        self.assertEqual(user.role.name, 'User')

    def test_delete_tag(self):
        tag = Tag()
        db.session.add(tag)
        db.session.commit()
        self.assertIsNotNone(Tag.query.get(1))

        response = self.client.post(url_for('admin.delete_tag', tag_id=1), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Tag deleted.', data)
        self.assertEqual(Tag.query.get(1), None)

    def test_manage_user_page(self):
        response = self.client.get(url_for('admin.manage_user'))
        data = response.get_data(as_text=True)
        self.assertIn('Manage Users', data)
        self.assertIn('Admin', data)
        self.assertIn('Locked', data)
        self.assertIn('Normal', data)

        response = self.client.get(url_for('admin.manage_user', filter='locked'))
        data = response.get_data(as_text=True)
        self.assertIn('Manage Users', data)
        self.assertIn('Locked User', data)
        self.assertNotIn('Normal User', data)

        response = self.client.get(url_for('admin.manage_user', filter='blocked'))
        data = response.get_data(as_text=True)
        self.assertIn('Manage Users', data)
        self.assertIn('Blocked User', data)
        self.assertNotIn('Locked User', data)
        self.assertNotIn('Normal User', data)

        response = self.client.get(url_for('admin.manage_user', filter='administrator'))
        data = response.get_data(as_text=True)
        self.assertIn('Manage Users', data)
        self.assertIn('Admin', data)
        self.assertNotIn('Blocked User', data)
        self.assertNotIn('Locked User', data)
        self.assertNotIn('Normal User', data)

        response = self.client.get(url_for('admin.manage_user', filter='moderator'))
        data = response.get_data(as_text=True)
        self.assertIn('Manage Users', data)
        self.assertIn('Admin', data)
        self.assertNotIn('Blocked User', data)
        self.assertNotIn('Locked User', data)
        self.assertNotIn('Normal User', data)

    def test_manage_photo_page(self):
        response = self.client.get(url_for('admin.manage_photo'))
        data = response.get_data(as_text=True)
        self.assertIn('Manage Photos', data)
        self.assertIn('Order by flag <span class="oi oi-elevator"></span>', data)

        response = self.client.get(url_for('admin.manage_photo', order='by_time'))
        data = response.get_data(as_text=True)
        self.assertIn('Manage Photos', data)
        self.assertIn('Order by time <span class="oi oi-elevator"></span>', data)

    def test_manage_tag_page(self):
        response = self.client.get(url_for('admin.manage_tag'))
        data = response.get_data(as_text=True)
        self.assertIn('Manage Tags', data)

    def test_manage_comment_page(self):
        response = self.client.get(url_for('admin.manage_comment'))
        data = response.get_data(as_text=True)
        self.assertIn('Manage Comments', data)
        self.assertIn('Order by flag <span class="oi oi-elevator"></span>', data)

        response = self.client.get(url_for('admin.manage_comment', order='by_time'))
        data = response.get_data(as_text=True)
        self.assertIn('Manage Comments', data)
        self.assertIn('Order by time <span class="oi oi-elevator"></span>', data)
