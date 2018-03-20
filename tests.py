import unittest
from datetime import datetime, timedelta

from app import create_app, db
from app.models import User, Post, PostVersion
from config import Config


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'


class UserModelCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        
    def test_password_hashing(self):
        u = User(username='nika')
        u.set_password('cat')
        self.assertFalse(u.check_password('dog'))
        self.assertTrue(u.check_password('cat'))
        
    def test_avatar(self):
        u = User(username='tomek', email='tomek@expl.com')
        self.assertEqual(
            u.avatar(128),
            ('https://www.gravatar.com/avatar/'
            '06251e79e281a26eb83831d20ed885ed'
            '?d=identicon&s=128'))
            
    def test_follow(self):
        u1 = User(username='tomek', email='tomek@expl.com')
        u2 = User(username='nika', email='nika@expl.com')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        self.assertEqual(u1.followed.all(), [])
        self.assertEqual(u1.followers.all(), [])
        
        u1.follow(u2)
        db.session.commit()
        self.assertTrue(u1.is_following(u2))
        self.assertEqual(u1.followed.count(), 1)
        self.assertEqual(u1.followed.first().username, 'nika')
        self.assertEqual(u2.followers.count(), 1)
        self.assertEqual(u2.followers.first().username, 'tomek')
        
        u1.unfollow(u2)
        db.session.commit()
        self.assertFalse(u1.is_following(u2))
        self.assertEqual(u1.followed.count(), 0)
        self.assertEqual(u2.followers.count(), 0)
        
    def test_follow_posts(self):
        u1 = User(username='tomek', email='tomek@expl.com')
        u2 = User(username='nika', email='nika@expl.com')
        u3 = User(username='alexis', email='alexis@expl.com')
        u4 = User(username='jana', email='jana@expl.com')
        db.session.add_all([u1, u2, u3, u4])
        
        now = datetime.utcnow()
        p1 = Post(body='from tomek', author=u1,
                timestamp=now + timedelta(seconds=1))
        p2 = Post(body='from nika', author=u2,
                timestamp=now + timedelta(seconds=4))
        p3 = Post(body='from alexis', author=u3,
                timestamp=now + timedelta(seconds=3))
        p4 = Post(body='from jana', author=u4,
                timestamp=now + timedelta(seconds=2))
        db.session.add_all([p1, p2, p3, p4])
        db.session.commit()
        
        u1.follow(u2)
        u1.follow(u4)
        u2.follow(u3)
        u3.follow(u2)
        db.session.commit()
        
        f1 = u1.followed_posts().all()
        f2 = u2.followed_posts().all()
        f3 = u3.followed_posts().all()
        f4 = u4.followed_posts().all()
        self.assertEqual(f1, [p2, p4, p1])
        self.assertEqual(f2, [p2, p3])
        self.assertEqual(f3, [p2, p3])
        self.assertEqual(f4, [p4])
        
    def test_post_history(self):
        u = User(username='tomek', email='tomek@expl.com')
        db.session.add(u)

        p = Post(body='from tomek', author=u)
        db.session.add(p)
        
        now = datetime.utcnow()
        
        pv = PostVersion(
            body='from tomek edited', 
            timestamp=now,
            original=p)
        db.session.add(pv)
        
        db.session.commit()
        
        version = PostVersion.query.filter_by(original=p).first()
        self.assertEqual(version.body, 'from tomek edited')
        self.assertEqual(version.original.body, 'from tomek')
        self.assertEqual(version.original.author, u)
        self.assertDictEqual(
            version.serialize(),
            {'body': 'from tomek edited', 'timestamp': now})
            
if __name__ == '__main__':
    unittest.main(verbosity=2)
