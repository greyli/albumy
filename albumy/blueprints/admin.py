# -*- coding: utf-8 -*-
"""
    :author: Grey Li (李辉)
    :url: http://greyli.com
    :copyright: © 2018 Grey Li <withlihui@gmail.com>
    :license: MIT, see LICENSE for more details.
"""
from flask import render_template, flash, Blueprint, request, current_app
from flask_login import login_required

from albumy.decorators import admin_required, permission_required
from albumy.extensions import db
from albumy.forms.admin import EditProfileAdminForm
from albumy.models import Role, User, Tag, Photo, Comment
from albumy.utils import redirect_back

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/')
@login_required
@permission_required('MODERATE')
def index():
    user_count = User.query.count()
    locked_user_count = User.query.filter_by(locked=True).count()
    blocked_user_count = User.query.filter_by(active=False).count()
    photo_count = Photo.query.count()
    reported_photos_count = Photo.query.filter(Photo.flag > 0).count()
    tag_count = Tag.query.count()
    comment_count = Comment.query.count()
    reported_comments_count = Comment.query.filter(Comment.flag > 0).count()
    return render_template('admin/index.html', user_count=user_count, photo_count=photo_count,
                           tag_count=tag_count, comment_count=comment_count, locked_user_count=locked_user_count,
                           blocked_user_count=blocked_user_count, reported_comments_count=reported_comments_count,
                           reported_photos_count=reported_photos_count)


@admin_bp.route('/profile/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(user_id):
    user = User.query.get_or_404(user_id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.name = form.name.data
        role = Role.query.get(form.role.data)
        if role.name == 'Locked':
            user.lock()
        user.role = role
        user.bio = form.bio.data
        user.website = form.website.data
        user.confirmed = form.confirmed.data
        user.active = form.active.data
        user.location = form.location.data
        user.username = form.username.data
        user.email = form.email.data
        db.session.commit()
        flash('Profile updated.', 'success')
        return redirect_back()
    form.name.data = user.name
    form.role.data = user.role_id
    form.bio.data = user.bio
    form.website.data = user.website
    form.location.data = user.location
    form.username.data = user.username
    form.email.data = user.email
    form.confirmed.data = user.confirmed
    form.active.data = user.active
    return render_template('admin/edit_profile.html', form=form, user=user)


@admin_bp.route('/block/user/<int:user_id>', methods=['POST'])
@login_required
@permission_required('MODERATE')
def block_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.role.name in ['Administrator', 'Moderator']:
        flash('Permission denied.', 'warning')
    else:
        user.block()
        flash('Account blocked.', 'info')
    return redirect_back()


@admin_bp.route('/unblock/user/<int:user_id>', methods=['POST'])
@login_required
@permission_required('MODERATE')
def unblock_user(user_id):
    user = User.query.get_or_404(user_id)
    user.unblock()
    flash('Block canceled.', 'info')
    return redirect_back()


@admin_bp.route('/lock/user/<int:user_id>', methods=['POST'])
@login_required
@permission_required('MODERATE')
def lock_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.role.name in ['Administrator', 'Moderator']:
        flash('Permission denied.', 'warning')
    else:
        user.lock()
        flash('Account locked.', 'info')
    return redirect_back()


@admin_bp.route('/unlock/user/<int:user_id>', methods=['POST'])
@login_required
@permission_required('MODERATE')
def unlock_user(user_id):
    user = User.query.get_or_404(user_id)
    user.unlock()
    flash('Lock canceled.', 'info')
    return redirect_back()


@admin_bp.route('/delete/tag/<int:tag_id>', methods=['GET', 'POST'])
@login_required
@permission_required('MODERATE')
def delete_tag(tag_id):
    tag = Tag.query.get_or_404(tag_id)
    db.session.delete(tag)
    db.session.commit()
    flash('Tag deleted.', 'info')
    return redirect_back()


@admin_bp.route('/manage/user')
@login_required
@permission_required('MODERATE')
def manage_user():
    filter_rule = request.args.get('filter', 'all')  # 'all', 'locked', 'blocked', 'administrator', 'moderator'
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['ALBUMY_MANAGE_USER_PER_PAGE']
    administrator = Role.query.filter_by(name='Administrator').first()
    moderator = Role.query.filter_by(name='Moderator').first()

    if filter_rule == 'locked':
        filtered_users = User.query.filter_by(locked=True)
    elif filter_rule == 'blocked':
        filtered_users = User.query.filter_by(active=False)
    elif filter_rule == 'administrator':
        filtered_users = User.query.filter_by(role=administrator)
    elif filter_rule == 'moderator':
        filtered_users = User.query.filter_by(role=moderator)
    else:
        filtered_users = User.query

    pagination = filtered_users.order_by(User.member_since.desc()).paginate(page, per_page)
    users = pagination.items
    return render_template('admin/manage_user.html', pagination=pagination, users=users)


@admin_bp.route('/manage/photo', defaults={'order': 'by_flag'})
@admin_bp.route('/manage/photo/<order>')
@login_required
@permission_required('MODERATE')
def manage_photo(order):
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['ALBUMY_MANAGE_PHOTO_PER_PAGE']
    order_rule = 'flag'
    if order == 'by_time':
        pagination = Photo.query.order_by(Photo.timestamp.desc()).paginate(page, per_page)
        order_rule = 'time'
    else:
        pagination = Photo.query.order_by(Photo.flag.desc()).paginate(page, per_page)
    photos = pagination.items
    return render_template('admin/manage_photo.html', pagination=pagination, photos=photos, order_rule=order_rule)


@admin_bp.route('/manage/tag')
@login_required
@permission_required('MODERATE')
def manage_tag():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['ALBUMY_MANAGE_TAG_PER_PAGE']
    pagination = Tag.query.order_by(Tag.id.desc()).paginate(page, per_page)
    tags = pagination.items
    return render_template('admin/manage_tag.html', pagination=pagination, tags=tags)


@admin_bp.route('/manage/comment', defaults={'order': 'by_flag'})
@admin_bp.route('/manage/comment/<order>')
@login_required
@permission_required('MODERATE')
def manage_comment(order):
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['ALBUMY_MANAGE_COMMENT_PER_PAGE']
    order_rule = 'flag'
    if order == 'by_time':
        pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(page, per_page)
        order_rule = 'time'
    else:
        pagination = Comment.query.order_by(Comment.flag.desc()).paginate(page, per_page)
    comments = pagination.items
    return render_template('admin/manage_comment.html', pagination=pagination, comments=comments, order_rule=order_rule)
