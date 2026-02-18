from flask import Blueprint, request, jsonify
from app import db
from app.models import Achievement, UserAchievement, UserStats, Reward
from datetime import datetime

bp = Blueprint('rewards', __name__, url_prefix='/api/rewards')

@bp.route('/achievements/<int:user_id>', methods=['GET'])
def get_user_achievements(user_id):
    """Get user's achievements."""
    achievements = UserAchievement.query.filter_by(user_id=user_id).all()

    return jsonify({
        'achievements': [
            {
                'id': ua.achievement_id,
                'name': ua.Achievement.name if hasattr(ua, 'Achievement') else 'Unknown',
                'description': ua.Achievement.description if hasattr(ua, 'Achievement') else '',
                'badge_icon': ua.Achievement.badge_icon if hasattr(ua, 'Achievement') else '',
                'unlocked_at': ua.unlocked_at.isoformat()
            }
            for ua in achievements
        ]
    }), 200

@bp.route('/check-achievements/<int:user_id>', methods=['POST'])
def check_achievements(user_id):
    """Check if user has earned any new achievements."""
    stats = UserStats.query.filter_by(user_id=user_id).first()

    if not stats:
        return jsonify({'error': 'User not found'}), 404

    new_achievements = []

    # Check for streaks
    if stats.streak_days >= 7:
        achievement = Achievement.query.filter_by(
            condition_type='streak',
            condition_value=7
        ).first()
        if achievement:
            existing = UserAchievement.query.filter_by(
                user_id=user_id,
                achievement_id=achievement.id
            ).first()
            if not existing:
                ua = UserAchievement(user_id=user_id, achievement_id=achievement.id)
                db.session.add(ua)
                new_achievements.append(achievement.name)

    # Check for points milestones
    if stats.total_points >= 100:
        achievement = Achievement.query.filter_by(
            condition_type='points',
            condition_value=100
        ).first()
        if achievement:
            existing = UserAchievement.query.filter_by(
                user_id=user_id,
                achievement_id=achievement.id
            ).first()
            if not existing:
                ua = UserAchievement(user_id=user_id, achievement_id=achievement.id)
                db.session.add(ua)
                new_achievements.append(achievement.name)

    # Check for lessons completed
    if stats.total_lessons_completed >= 5:
        achievement = Achievement.query.filter_by(
            condition_type='lessons_completed',
            condition_value=5
        ).first()
        if achievement:
            existing = UserAchievement.query.filter_by(
                user_id=user_id,
                achievement_id=achievement.id
            ).first()
            if not existing:
                ua = UserAchievement(user_id=user_id, achievement_id=achievement.id)
                db.session.add(ua)
                new_achievements.append(achievement.name)

    try:
        db.session.commit()
        return jsonify({
            'new_achievements': new_achievements,
            'message': f'{len(new_achievements)} new achievement(s) unlocked!' if new_achievements else 'No new achievements'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/leaderboard', methods=['GET'])
def get_leaderboard():
    """Get top users by points."""
    limit = request.args.get('limit', 10, type=int)

    stats = UserStats.query.order_by(UserStats.total_points.desc()).limit(limit).all()

    return jsonify({
        'leaderboard': [
            {
                'rank': i + 1,
                'user_id': stat.user_id,
                'username': stat.user.username if stat.user else 'Unknown',
                'points': stat.total_points,
                'level': stat.level,
                'accuracy_rate': stat.accuracy_rate
            }
            for i, stat in enumerate(stats)
        ]
    }), 200

@bp.route('/user/<int:user_id>/rewards', methods=['GET'])
def get_user_rewards(user_id):
    """Get user's recent rewards."""
    limit = request.args.get('limit', 20, type=int)

    rewards = Reward.query.filter_by(user_id=user_id).order_by(
        Reward.created_at.desc()
    ).limit(limit).all()

    return jsonify({
        'rewards': [
            {
                'id': reward.id,
                'reward_type': reward.reward_type,
                'amount': reward.amount,
                'reason': reward.reason,
                'created_at': reward.created_at.isoformat()
            }
            for reward in rewards
        ]
    }), 200

