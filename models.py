from flask_login import UserMixin
from app import db
from datetime import datetime



class User(db.Model , UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(50), nullable = False, unique = True)
    password = db.Column(db.String(255), nullable = False)
    full_name = db.Column(db.String, nullable = False)
    qualification = db.Column(db.String, nullable = False)
    dob = db.Column(db.Date, nullable = False)
    is_admin = db.Column(db.Boolean)
    scores = db.relationship("Scores", backref = "user", lazy = True)

class Subject(db.Model):
    __tablename__ = 'subject'
    id = db.Column(db.Integer, primary_key = True, nullable = False)
    name = db.Column(db.String, nullable = False)
    description = db.Column(db.Text)
    chapter = db.relationship("Chapter", backref = "subject", lazy = True )

class Chapter(db.Model):
    __tablename__ = 'chapter'
    id = db.Column(db.Integer, primary_key = True, nullable = False)
    name = db.Column(db.String, nullable = False)
    description = db.Column(db.Text, nullable = False)
    subject_id = db.Column(db.Integer, db.ForeignKey("subject.id"))
    quiz = db.relationship("Quiz", backref = "chapter", lazy =True)


class Quiz(db.Model):
    __tablename__ = 'quiz'
    id = db.Column(db.Integer, primary_key = True, nullable = False )
    chapter_id = db.Column(db.Integer, db.ForeignKey("chapter.id"))
    quiz_date = db.Column(db.DateTime, default = datetime.utcnow)
    duration = db.Column(db.Integer)
    remarks = db.Column(db.Text)
    questions = db.relationship("Questions", backref = "quiz", lazy = True)
    scores = db.relationship("Scores", backref = "quiz", lazy = True)

class Questions(db.Model):
    __tablename__ = 'question'
    id = db.Column(db.Integer, primary_key = True, nullable = False)
    quiz_id = db.Column(db.Integer, db.ForeignKey("quiz.id"), nullable = False)
    question_title = db.Column(db.String(50))
    question_statement = db.Column(db.Text, nullable = False)
    option_1 = db.Column(db.Text, nullable = False)
    option_2 = db.Column(db.Text, nullable = False)
    option_3 = db.Column(db.Text, nullable = False)
    option_4 = db.Column(db.Text, nullable = False)
    correct_option = db.Column(db.Integer, nullable = False)
    
    
class Scores(db.Model):
    __tablename__ = 'scores'
    id = db.Column(db.Integer, primary_key = True, nullable = False)
    quiz_id = db.Column(db.Integer, db.ForeignKey("quiz.id"), nullable = False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable = False)
    time_stamp_for_attempt =db.Column(db.DateTime, default = datetime.utcnow)
    total_scored = db.Column(db.Integer)
    user_response = db.Column(db.JSON, nullable = False)

    def __init__(self, quiz_id, user_id, total_scored, user_response = None):
        self.quiz_id = quiz_id
        self.user_id = user_id
        self.total_scored = total_scored
        self.user_response = user_response







