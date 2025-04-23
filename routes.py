from flask import Flask, request, url_for, redirect, render_template, flash, session, current_app, jsonify
from flask_login import login_user, current_user, logout_user,login_required
from models import User, Subject, Chapter, Quiz, Questions, Scores
from app import db
from datetime import datetime, timedelta
import json
import os
import matplotlib.pyplot as plt
from sqlalchemy.sql import func







def register_routes(app, db, bcrypt):
    def create_admin():
        with app.app_context():
            username = "admin@gmail.com"
            password = bcrypt.generate_password_hash("admin").decode("utf-8")
            dob_string = '17-01-2006'
            dob = datetime.strptime(dob_string, "%d-%m-%Y").date()
            existing_admin = User.query.filter_by(username = username).first()
            if not existing_admin:
                new_admin = User(username = username, password = password, dob = dob, full_name = "Admin", qualification = "Admin", is_admin = True )
                db.session.add(new_admin)
                db.session.commit()
                print("Admin created")
            else:
                print("Admin alredy exist")
    create_admin()
    
        
    

    @app.route("/")
    def index():
        return render_template("index.html")
    
    @app.route("/signup", methods = ["GET", "POST"])
    def signup():    
        
        if request.method == "POST":
            username = request.form.get("username")
            password = bcrypt.generate_password_hash(request.form.get("password")).decode("utf-8")
            full_name = request.form.get("full_name")
            qualification = request.form.get("qualification")
            dob_str = request.form.get("dob")
            dob = datetime.strptime(dob_str, "%Y-%m-%d").date()

            if not username or not password or not full_name or not qualification or not dob:
                flash("All fields are required!", "danger")
                return redirect( url_for("signup") )
            existing_user = User.query.filter_by(username = username).first()
            if existing_user:
                flash("username alredy exist!", "danger")
                return redirect(url_for('signup'))

            
            user = User(username = username, password = password, full_name = full_name, qualification = qualification, dob = dob)
            db.session.add(user)
            db.session.commit()
            flash("Signup successful!, please log in", "success")
            return redirect(url_for("login"))
        
        return render_template("signup.html")
        



    @app.route("/login", methods = ["GET", "POST"])
    def login():
        if request.method == "POST":
            username = request.form.get("username")
            password = request.form.get("password")
            user = User.query.filter_by(username = username).first()
            if username and password:
                if user and bcrypt.check_password_hash(user.password, password):
                    login_user(user)
                    flash(f"Hello! {user.full_name} welcome to the app ", "success")
                    if user.is_admin:
                        return redirect(url_for("admin_dashboard"))
                    return redirect(url_for("user_dashboard", user_id = user.id))
                    
                else:
                    flash("Invalid username or password","danger")
                    return redirect(url_for('login'))
            else:
                flash("Enter username or password","danger")
                return redirect(url_for(login))
        return render_template("login.html")

    @app.route("/logout")
    def logout():
        logout_user()
        return redirect(url_for('login'))
    

    


    @app.route("/admin/dashboard")
    @login_required
    def admin_dashboard():
        if not current_user.is_admin:
            flash("Unauthorised access!" , "danger")
            return redirect(url_for('login'))
        subject = Subject.query.all()
        chapter = Chapter.query.all()
        return render_template("admin_dashboard.html", subject = subject, chapter = chapter)
    


    #Subjects
    @app.route("/admin/add_subjects", methods = ["GET", "POST"])
    @login_required
    def add_subject():
        if not current_user.is_admin:
            flash("Unauthorised access!" , "danger")
            return redirect(url_for('login'))
        if request.method == "POST":
            name = request.form.get("name")
            description = request.form.get("description")
            add_subjects = Subject(name = name, description = description)
            db.session.add(add_subjects)
            db.session.commit()
            flash("Added subjects successfully!", "success")
            return redirect(url_for("admin_dashboard"))
        return render_template("add_subjects.html")
    
    @app.route("/admin/update_subject/<int:subject_id>", methods = ["GET", "POST"])
    @login_required
    def update_subject(subject_id):
        if not current_user.is_admin:
            flash("Unauthorise access", "danger")
            return redirect(url_for("login"))
        subject = Subject.query.get(subject_id)
        if not subject:
            flash("subjects not found", "danger")
            return redirect(url_for('admin_dashboard'))
        if request.method == "POST":
            subject.name = request.form.get("name")
            subject.description = request.form.get("description")
            db.session.commit()
            flash("Subjects updated successfully", "success")
            return redirect(url_for("admin_dashboard"))
        return render_template("edit_subjects.html", subject = subject)

    @app.route("/admin/delete_subjects/<int:subject_id>", methods = ["GET"])
    @login_required
    def delete_subject(subject_id):
        if not current_user.is_admin:
            flash("Unauthorise access", "danger")
            return redirect(url_for("login"))
        
        subject = Subject.query.get(subject_id)
        if not subject:
            flash("subject not found", "danger")
            return redirect(url_for("admin_dashboard"))
        db.session.delete(subject)
        db.session.commit()
        flash("Successfully deleted subjects", "success")
        return redirect(url_for('admin_dashboard'))
    


    #Chapter
    @app.route("/admin/add_chapters/<int:subject_id>", methods = ["GET", "POST"])
    @login_required
    def add_chapter(subject_id):
        if not current_user.is_admin:
            flash("Unauthorise access", "danger")
            return redirect(url_for('login'))
        subject = Subject.query.get(subject_id)
        if not subject:
            flash("Add subject","danger")
            return redirect(url_for("admin_dashboard"))
        chapter = Chapter.query.filter_by(subject_id = subject_id).all()
        if request.method == "POST":
            name = request.form.get("name")
            description = request.form.get("description")
            add_chapter = Chapter(name = name, description = description, subject_id = subject.id)
            db.session.add(add_chapter)
            db.session.commit()
            flash("Chapter added successfully", "success")
            return redirect(url_for("admin_dashboard"))
        return render_template("add_chapters.html", subject = subject, chapter = chapter)

    @app.route("/admin/edit_chapter/<int:chapter_id>", methods = ["GET", "POST"])
    @login_required
    def edit_chapter(chapter_id):
        if not current_user.is_admin:
            flash("Unauthorise access", "danger")
            return redirect(url_for('login'))
        chapter = Chapter.query.get(chapter_id)
        if not chapter:
            flash("Chapter is not found", "danger")
            return redirect(url_for("admin_dashboard"))
        if request.method == "POST":
            chapter.name = request.form.get("name")
            chapter.description = request.form.get("description")
            db.session.commit()
            flash("Chapter Updated Successfully", "success")
            return redirect(url_for("admin_dashboard"))
        return render_template("edit_chapters.html", chapter = chapter)

    @app.route("/admin/delete_chapter/<int:chapter_id>", methods = ["GET"])
    @login_required
    def delete_chapter(chapter_id):
        if not current_user.is_admin:
            flash("Unauthorise access", "danger")
            return redirect(url_for("login"))
        chapter = Chapter.query.get(chapter_id)
        if not chapter:
            flash("Chapter is not found", "danger")
            return redirect(url_for("add_chapter", subject_id = chapter.subject_id))
        flash("Deleted chapter successfully", "success")
        db.session.delete(chapter)
        db.session.commit()
        return redirect(url_for('admin_dashboard'))




    #quiz
    @app.route("/quiz_management")
    @login_required
    def quiz_management():
        if not current_user.is_admin:
            flash("Unauthorise access", "danger")
            return redirect(url_for("login"))
        chapter = Chapter.query.all()
        for chap in chapter:
            chap.quiz = Quiz.query.filter_by(chapter_id = chap.id).all()
        return render_template("quiz_management.html", chapter = chapter)

    @app.route("/admin/add_quiz/<int:chapter_id>", methods = ["GET", "POST"])
    @login_required
    def add_quiz(chapter_id):
        if not current_user.is_admin:
            flash("Unauthorise access", "danger")
            return redirect(url_for('login'))
        chapter= Chapter.query.get(chapter_id)
        if not chapter:
            flash("Add Chapter", "danger")
            return redirect(url_for('add_chapter'))
        quiz = Quiz.query.filter_by(chapter_id = chapter_id).all()
        if request.method == "POST":
            date_str = request.form.get("date")
            quiz_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            duration = request.form.get("duration")
            quiz_duration = datetime.strptime(duration, "%H:%M").time()
            duration_str = quiz_duration.strftime('%H:%M')
            add_quizzes = Quiz(quiz_date = quiz_date, duration = duration_str, chapter_id = chapter_id)
            db.session.add(add_quizzes)
            db.session.commit()
            flash("Quiz added successfully", "success")
            return redirect(url_for("quiz_management"))
        return render_template("add_quiz.html", chapter = chapter, quiz = quiz, chapter_id = chapter_id)

    @app.route("/admin/edit_quiz/<int:quiz_id>", methods = ["GET", "POST"])
    @login_required
    def edit_quiz(quiz_id):
        if not current_user.is_admin:
            flash("Unauthorise access", "danger")
            return redirect(url_for('login'))
        quiz = Quiz.query.get(quiz_id)
        if not quiz :
            flash("quiz is not found", "danger")
            return redirect(url_for("admin_dashboard"))
        if request.method == "POST":
            quiz_str = request.form.get("date")
            quiz.quiz_date = datetime.strptime(quiz_str, "%Y-%m-%d").date()
            quiz.duration = request.form.get("duration")
            db.session.commit()
            flash("Quiz Updated Successfully", "success")
            return redirect(url_for("quiz_management"))
        return render_template("edit_quiz.html", quiz = quiz)

    @app.route("/admin/delete_quiz/<int:quiz_id>", methods = ["GET"])
    @login_required
    def delete_quiz(quiz_id):
        if not current_user.is_admin:
            flash("Unauthorise access", "danger")
            return redirect(url_for("login"))
        quiz = Quiz.query.get(quiz_id)
        if not quiz:
            flash("Quiz is not found", "danger")
            return redirect(url_for("admin_dashboard"))
        db.session.delete(quiz)
        db.session.commit()
        return redirect(url_for('quiz_management'))
    

    #question
    @app.route("/add_question/<int:quiz_id>", methods = ["GET", "POST"])
    @login_required
    def add_question(quiz_id):
        if not current_user.is_admin:
            flash("Unauthorise access", "danger")
            return redirect(url_for('login'))
        quiz = Quiz.query.get(quiz_id)
        if not quiz:
            flash("Quiz not found", "danger")
            return redirect(url_for('add_quiz'))
        question = Questions.query.filter_by(quiz_id = quiz_id).all()
        if request.method == "POST":
            question_title = request.form.get("question_title")
            question_statement = request.form.get("question_statement")
            option_1 = request.form.get("option_1")
            option_2 = request.form.get("option_2")
            option_3 = request.form.get("option_3")
            option_4 = request.form.get("option_4")
            correct_option = request.form.get("correct_option")
            add_question = Questions(question_title = question_title, question_statement = question_statement, option_1 = option_1, option_2 = option_2, option_3 = option_3, option_4 = option_4, correct_option = correct_option, quiz_id = quiz_id )
            db.session.add(add_question)
            db.session.commit()
            flash("Question added successfully", "success")
            return redirect(url_for("quiz_management"))
        return render_template("add_question.html", quiz = quiz, question = question, quiz_id = quiz_id)
    

    @app.route("/edit_question/<int:question_id>", methods = ["GET", "POST"])
    @login_required
    def edit_question(question_id):
        if not current_user.is_admin:
            flash("Unauthorise access", "danger")
            return redirect(url_for('login'))
        question = Questions.query.get(question_id)
        if not question:
            flash("Question not found", "danger")
            return redirect(url_for('quiz_management'))
        if request.method == "POST":
            question.question_title = request.form.get("question_title")
            question.question_statement = request.form.get("question_statement")
            question.option_1 = request.form.get("option_1", "").strip()
            question.option_2 = request.form.get("option_2", "").strip()
            question.option_3 = request.form.get("option_3", "").strip()
            question.option_4 = request.form.get("option_4", "").strip()
            question.correct_option = request.form.get("correct_option")
            db.session.commit()
            flash("Question edited successfully", "success")
            return redirect(url_for('quiz_dashboard') if not question.quiz_id else url_for('show_question', quiz_id = question.quiz_id ))
        return render_template("edit_question.html", question = question)

        
    @app.route("/delete_question/<int:question_id>", methods = ["GET"])
    @login_required
    def delete_question(question_id):
        if not current_user.is_admin:
            flash("Unauthorise access", "danger")
            return redirect(url_for("login"))
        question = Questions.query.get(question_id)
        if not question and not question.quiz_id:
            flash("Question is not found", "danger")
            return redirect(url_for("quiz_management"))
        db.session.delete(question)
        db.session.commit()
        flash("Question deleted successfully", "success")
        return redirect(url_for('quiz_dashboard') if not question.quiz_id else url_for('show_question', quiz_id = question.quiz_id ))
    
    @app.route("/show_question/<int:quiz_id>")
    @login_required
    def show_question(quiz_id):
        if not current_user.is_admin:
            flash("Unauthorise access", "danger")
            return redirect(url_for("login"))
        question = Questions.query.filter_by(quiz_id = quiz_id).all()
        if question:
            return render_template("show_question.html", question = question)
        else:
            flash("Add Questions first","danger")
            return redirect(url_for('quiz_management'))
        
    @app.route("/admin/summary")
    @login_required
    def admin_summary():
        if not current_user.is_admin:
            return redirect(url_for('login'))
        Subject_count = Subject.query.count()
        Chapter_count = Chapter.query.count()
        Quiz_count = Quiz.query.count()
        categories = ['Subjects', 'Chapters', 'Quizzes']
        values = [Subject_count, Chapter_count, Quiz_count]

        plt.figure(figsize=(8, 5))
        plt.bar(categories, values, color='skyblue')
        plt.xlabel("Categories")
        plt.ylabel("Count")
        plt.title("Admin Summary")
        plt.xticks(rotation=30)

        max_value = max(values) if max(values) > 0 else 1  
        plt.yticks(range(0, max_value + 1, 1))

        # **Save Plot to Static Folder**
        img_path = os.path.join("static", "admin_summary.png")
        plt.savefig(img_path)
        plt.close()

        return render_template('admin_summary.html', 
                            Subject_count=Subject_count, 
                            Chapter_count=Chapter_count, 
                            Quiz_count=Quiz_count,
                            img_path=img_path)

        
        
        
        

        
        
        


    

    #User
    @app.route("/user/dashboard/<int:user_id>")
    @login_required
    def user_dashboard(user_id):
        if  current_user.is_authenticated:
            user = User.query.get(user_id)
            subject = Subject.query.all()
            chapter = Chapter.query.all()
            quiz = Quiz.query.all()
            flash("Welcome to the app", "success")
            return render_template("user_dashboard.html", user = user, subject = subject, chapter= chapter, quiz = quiz)
        else:
            return "User Not Found", 404
    
    @app.route("/view/quiz/<int:quiz_id>")
    def view_quiz(quiz_id):
        if current_user.is_authenticated:
            quiz = Quiz.query.filter_by(id= quiz_id).all()
            return render_template("view_quiz.html", quiz = quiz, user = current_user)
        else:
            return "User Not Found", 404
        
    @app.route("/attempt/quiz/<int:quiz_id>", methods = ["GET", "POST"])
    @login_required
    def attempt_quiz(quiz_id):
        quiz = Quiz.query.get(quiz_id)
        questions = Questions.query.filter_by(quiz_id = quiz_id).all()
        #check if user already attempted the quiz
        existing_score = Scores.query.filter_by(user_id = current_user.id, quiz_id = quiz_id).first()
        if existing_score:
            flash('You are already attempted the quiz', 'danger')
            return redirect(url_for('quiz_review', score_id = existing_score.id ))
        if request.method == "POST":
            user_responses = {}
            score = 0
            for question in questions:
                q_id = str(question.id)
                selected_option = request.form.get(f'question_{question.id}')
                user_responses[q_id] = selected_option

                if selected_option and int(selected_option) == question.correct_option:
                    score += 1
            try:
                new_score = Scores(quiz_id = quiz_id, user_id = current_user.id, total_scored = score, user_response = user_responses)
                db.session.add(new_score)
                db.session.commit()
                return redirect(url_for('quiz_review', score_id = new_score.id ))
            except Exception as e:
                db.session.rollback()
                flash(f'Error submitting quiz: {str(e)}', 'danger')
                return redirect(url_for('attempt_quiz', quiz_id=quiz_id))
                
        #calculate the end time for the timer
        if isinstance(quiz.duration, str) and ':' in quiz.duration:
            # Split the time string into hours and minutes
            hours, minutes = quiz.duration.split(':')
            # Convert to total minutes
            duration = int(hours) * 60 + int(minutes)
        else:
            duration = int(quiz.duration)
        end_time = datetime.utcnow() + timedelta(minutes=duration)
        return render_template('quiz.html', quiz = quiz, questions = questions, end_time = end_time.isoformat())
    
    @app.route("/quiz/review/<int:score_id>")
    @login_required
    def quiz_review(score_id):
        score_record = Scores.query.get(score_id)
        quiz = Quiz.query.get(score_record.quiz_id)
        questions = Questions.query.filter_by(quiz_id = quiz.id).all()

        
        #question detail with user responses
        review_data = []
        user_responses = score_record.user_response
        if isinstance(user_responses, str):
            user_responses = json.loads(user_responses)
        for question in questions:
            q_id = str(question.id)
            review_data.append({
                'question': question,
                'user_answer': user_responses.get(q_id),
                'Correct_answer': question.correct_option
            })
        return render_template('review.html', score_record = score_record, review_data = review_data, quiz = quiz)
    
    
    
    @app.route("/user/summary")
    @login_required
    def user_summary():
        user_scores = db.session.query(User.username, func.sum(Scores.total_scored)).join(Scores).group_by(User.id).all()

        
        usernames = [user[0] for user in user_scores]  # Usernames
        total_scores = [user[1] if user[1] else 0 for user in user_scores]  # Total scores

        
        plt.figure(figsize=(10, 5))
        plt.bar(usernames, total_scores, color='green')

        
        plt.xlabel("Users")
        plt.ylabel("Total Score")
        plt.title("User Total Scores")
        plt.xticks(rotation=45)

        
        max_value = max(total_scores) if total_scores else 1
        plt.yticks(range(0, max_value + 1, 1))

        
        img_path = os.path.join(current_app.root_path, "static", "user_summary.png")
        plt.savefig(img_path)
        plt.close()

        return render_template("user_summary.html", img_path=url_for('static', filename='user_summary.png'))
        

        
        
        

    
 
    



        






        
            
        
        
        

    



            
        

        