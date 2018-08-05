# -*- coding: utf-8 -*-
"""
    :author: Grey Li (李辉)
    :url: http://greyli.com
    :copyright: © 2018 Grey Li <withlihui@gmail.com>
    :license: MIT, see LICENSE for more details.
"""
from albumy.extensions import db
from albumy.models import Comment, Role, User, Photo, Tag
from tests.base import BaseTestCase


class CLITestCase(BaseTestCase):

    def setUp(self):
        super(CLITestCase, self).setUp()
        db.drop_all()

    def test_initdb_command(self):
        result = self.runner.invoke(args=['initdb'])
        self.assertIn('Initialized database.', result.output)

    def test_initdb_command_with_drop(self):
        result = self.runner.invoke(args=['initdb', '--drop'], input='y\n')
        self.assertIn('This operation will delete the database, do you want to continue?', result.output)
        self.assertIn('Drop tables.', result.output)

    def test_init_command(self):
        result = self.runner.invoke(args=['init'])
        self.assertIn('Initializing the database...', result.output)
        self.assertIn('Initializing the roles and permissions...', result.output)
        self.assertIn('Done.', result.output)
        self.assertEqual(Role.query.count(), 4)

    def test_forge_command(self):
        pass  # it will take too long time

    def test_forge_command_with_count(self):
        result = self.runner.invoke(args=['forge', '--user', '5', '--follow', '10',
                                          '--photo', '10', '--tag', '10', '--collect', '10',
                                          '--comment', '10'])

        self.assertIn('Initializing the roles and permissions...', result.output)

        self.assertEqual(User.query.count(), 6)
        self.assertIn('Generating the administrator...', result.output)

        self.assertIn('Generating 10 follows...', result.output)

        self.assertEqual(Photo.query.count(), 10)
        self.assertIn('Generating 10 photos...', result.output)

        self.assertEqual(Tag.query.count(), 10)
        self.assertIn('Generating 10 tags...', result.output)

        self.assertIn('Generating 10 collects...', result.output)

        self.assertEqual(Comment.query.count(), 10)
        self.assertIn('Generating 10 comments...', result.output)

        self.assertIn('Done.', result.output)
