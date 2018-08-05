# -*- coding: utf-8 -*-
"""
    :author: Grey Li (李辉)
    :url: http://greyli.com
    :copyright: © 2018 Grey Li <withlihui@gmail.com>
    :license: MIT, see LICENSE for more details.
"""
from flask import url_for

from albumy.extensions import db
from albumy.models import User, Photo, Comment, Notification, Tag
from tests.base import BaseTestCase


class MainTestCase(BaseTestCase):

    def test_index_page(self):
        response = self.client.get(url_for('main.index'))
        data = response.get_data(as_text=True)
        self.assertIn('Join Now', data)

        self.login()
        response = self.client.get(url_for('main.index'))
        data = response.get_data(as_text=True)
        self.assertNotIn('Join Now', data)
        self.assertIn('My Home', data)

    def test_explore_page(self):
        response = self.client.get(url_for('main.explore'))
        data = response.get_data(as_text=True)
        self.assertIn('Change', data)

    def test_search(self):
        response = self.client.get(url_for('main.search', q=''), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Enter keyword about photo, user or tag.', data)

        response = self.client.get(url_for('main.search', q='normal'))
        data = response.get_data(as_text=True)
        self.assertNotIn('Enter keyword about photo, user or tag.', data)
        self.assertIn('No results.', data)

        response = self.client.get(url_for('main.search', q='normal', category='tag'))
        data = response.get_data(as_text=True)
        self.assertNotIn('Enter keyword about photo, user or tag.', data)
        self.assertIn('No results.', data)

        response = self.client.get(url_for('main.search', q='normal', category='user'))
        data = response.get_data(as_text=True)
        self.assertNotIn('Enter keyword about photo, user or tag.', data)
        self.assertNotIn('No results.', data)
        self.assertIn('Normal User', data)

    def test_show_notifications(self):
        user = User.query.get(2)
        notification1 = Notification(message='test 1', is_read=True, receiver=user)
        notification2 = Notification(message='test 2', is_read=False, receiver=user)
        db.session.add_all([notification1, notification2])
        db.session.commit()

        self.login()
        response = self.client.get(url_for('main.show_notifications'))
        data = response.get_data(as_text=True)
        self.assertIn('test 1', data)
        self.assertIn('test 2', data)

        response = self.client.get(url_for('main.show_notifications', filter='unread'))
        data = response.get_data(as_text=True)
        self.assertNotIn('test 1', data)
        self.assertIn('test 2', data)

    def test_read_notification(self):
        user = User.query.get(2)
        notification1 = Notification(message='test 1', receiver=user)
        notification2 = Notification(message='test 2', receiver=user)
        db.session.add_all([notification1, notification2])
        db.session.commit()

        self.login(email='admin@helloflask.com', password='123')
        response = self.client.post(url_for('main.read_notification', notification_id=1))
        self.assertEqual(response.status_code, 403)

        self.logout()
        self.login()

        response = self.client.post(url_for('main.read_notification', notification_id=1), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Notification archived.', data)

        self.assertTrue(Notification.query.get(1).is_read)

    def test_read_all_notification(self):
        user = User.query.get(2)
        notification1 = Notification(message='test 1', receiver=user)
        notification2 = Notification(message='test 2', receiver=user)
        db.session.add_all([notification1, notification2])
        db.session.commit()

        self.login()

        response = self.client.post(url_for('main.read_all_notification'), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('All notifications archived.', data)

        self.assertTrue(Notification.query.get(1).is_read)
        self.assertTrue(Notification.query.get(2).is_read)

    def test_show_photo(self):
        response = self.client.get(url_for('main.show_photo', photo_id=1), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Delete', data)
        self.assertIn('test tag', data)
        self.assertIn('test comment body', data)

        self.login(email='admin@helloflask.com', password='123')
        response = self.client.get(url_for('main.show_photo', photo_id=1), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Delete', data)

    def test_photo_next(self):
        user = User.query.get(1)
        photo2 = Photo(filename='test.jpg', filename_s='test_s.jpg', filename_m='test_m.jpg',
                       description='Photo 2', author=user)
        photo3 = Photo(filename='test.jpg', filename_s='test_s.jpg', filename_m='test_m.jpg',
                       description='Photo 3', author=user)
        photo4 = Photo(filename='test.jpg', filename_s='test_s.jpg', filename_m='test_m.jpg',
                       description='Photo 4', author=user)
        db.session.add_all([photo2, photo3, photo4])
        db.session.commit()

        response = self.client.get(url_for('main.photo_next', photo_id=5), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Photo 3', data)

        response = self.client.get(url_for('main.photo_next', photo_id=4), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Photo 2', data)

        response = self.client.get(url_for('main.photo_next', photo_id=3), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Photo 1', data)

        response = self.client.get(url_for('main.photo_next', photo_id=1), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('This is already the last one.', data)

    def test_photo_prev(self):
        user = User.query.get(1)
        photo2 = Photo(filename='test.jpg', filename_s='test_s.jpg', filename_m='test_m.jpg',
                       description='Photo 2', author=user)
        photo3 = Photo(filename='test.jpg', filename_s='test_s.jpg', filename_m='test_m.jpg',
                       description='Photo 3', author=user)
        photo4 = Photo(filename='test.jpg', filename_s='test_s.jpg', filename_m='test_m.jpg',
                       description='Photo 4', author=user)
        db.session.add_all([photo2, photo3, photo4])
        db.session.commit()

        response = self.client.get(url_for('main.photo_previous', photo_id=1), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Photo 2', data)

        response = self.client.get(url_for('main.photo_previous', photo_id=3), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Photo 3', data)

        response = self.client.get(url_for('main.photo_previous', photo_id=4), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Photo 4', data)

        response = self.client.get(url_for('main.photo_previous', photo_id=5), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('This is already the first one.', data)

    def test_collect(self):
        photo = Photo(filename='test.jpg', filename_s='test_s.jpg', filename_m='test_m.jpg',
                      description='Photo 3', author=User.query.get(2))
        db.session.add(photo)
        db.session.commit()
        self.assertEqual(Photo.query.get(3).collectors, [])

        self.login()
        response = self.client.post(url_for('main.collect', photo_id=3), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Photo collected.', data)

        self.assertEqual(Photo.query.get(3).collectors[0].collector.name, 'Normal User')

        response = self.client.post(url_for('main.collect', photo_id=3), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Already collected.', data)

    def test_uncollect(self):
        self.login()
        self.client.post(url_for('main.collect', photo_id=1), follow_redirects=True)

        response = self.client.post(url_for('main.uncollect', photo_id=1), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Photo uncollected.', data)

        response = self.client.post(url_for('main.uncollect', photo_id=1), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Not collect yet.', data)

    def test_report_comment(self):
        self.assertEqual(Comment.query.get(1).flag, 0)

        self.login()
        response = self.client.post(url_for('main.report_comment', comment_id=1), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Comment reported.', data)
        self.assertEqual(Comment.query.get(1).flag, 1)

    def test_report_photo(self):
        self.assertEqual(Photo.query.get(1).flag, 0)

        self.login()
        response = self.client.post(url_for('main.report_photo', photo_id=1), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Photo reported.', data)
        self.assertEqual(Photo.query.get(1).flag, 1)

    def test_show_collectors(self):
        user = User.query.get(2)
        user.collect(Photo.query.get(1))
        response = self.client.get(url_for('main.show_collectors', photo_id=1), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('1 Collectors', data)
        self.assertIn('Normal User', data)

    def test_edit_description(self):
        self.assertEqual(Photo.query.get(2).description, 'Photo 2')

        self.login()
        response = self.client.post(url_for('main.edit_description', photo_id=2), data=dict(
            description='test description.'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Description updated.', data)
        self.assertEqual(Photo.query.get(2).description, 'test description.')

    def test_new_comment(self):
        self.login()
        response = self.client.post(url_for('main.new_comment', photo_id=1), data=dict(
            body='test comment from normal user.'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Comment published.', data)
        self.assertEqual(Photo.query.get(1).comments[1].body, 'test comment from normal user.')

    def test_new_tag(self):
        self.login(email='admin@helloflask.com', password='123')

        response = self.client.post(url_for('main.new_tag', photo_id=1), data=dict(
            tag='hello dog pet happy'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Tag added.', data)
        self.assertEqual(Photo.query.get(1).tags[1].name, 'hello')
        self.assertEqual(Photo.query.get(1).tags[2].name, 'dog')
        self.assertEqual(Photo.query.get(1).tags[3].name, 'pet')
        self.assertEqual(Photo.query.get(1).tags[4].name, 'happy')

    def test_set_comment(self):
        self.login()
        response = self.client.post(url_for('main.set_comment', photo_id=1), follow_redirects=True)
        self.assertEqual(response.status_code, 403)

        self.logout()
        self.login(email='admin@helloflask.com', password='123')
        response = self.client.post(url_for('main.set_comment', photo_id=1), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Comment disabled', data)
        self.assertFalse(Photo.query.get(1).can_comment)

        response = self.client.post(url_for('main.set_comment', photo_id=1), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Comment enabled', data)
        self.assertTrue(Photo.query.get(1).can_comment)

    def test_reply_comment(self):
        self.login()
        response = self.client.get(url_for('main.reply_comment', comment_id=1), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Reply to', data)

    def test_delete_photo(self):
        self.login()
        response = self.client.post(url_for('main.delete_photo', photo_id=2), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Photo deleted.', data)
        self.assertIn('Normal User', data)

    def test_delete_comment(self):
        self.login()
        response = self.client.post(url_for('main.delete_comment', comment_id=1), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Comment deleted.', data)

    def test_show_tag(self):
        response = self.client.get(url_for('main.show_tag', tag_id=1))
        data = response.get_data(as_text=True)
        self.assertIn('Order by time', data)

        response = self.client.get(url_for('main.show_tag', tag_id=1, order='by_collects'))
        data = response.get_data(as_text=True)
        self.assertIn('Order by collects', data)

    def test_delete_tag(self):
        photo = Photo.query.get(2)
        tag = Tag(name='test')
        photo.tags.append(tag)
        db.session.commit()

        self.login()
        response = self.client.post(url_for('main.delete_tag', photo_id=2, tag_id=2), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Tag deleted.', data)

        self.assertEqual(photo.tags, [])
        self.assertIsNone(Tag.query.get(2))
