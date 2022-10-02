from ast import Return
from crypt import methods
import json
import os
from tkinter import N
from unicodedata import category
from uuid import RESERVED_FUTURE
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def question_pagination(request, selec):
    page = request.args.get('page', 1 , type = int)
    start = (page-1)* QUESTIONS_PER_PAGE
    end= start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selec]
    current_quest = questions[start: end]
    return current_quest


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    # set up cors Allow '*' for origins
    CORS(app,resources={'/':{'origins': '*'}})

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    def after_request(response):
        response.headers.add(
            'Access-Control-Allow-Headers','Content-Type,Authorization,true')
        response.headers.add(
            'Access-Control-Allow-Methods','GET,PUT,POST,DELETE,OPTIONS')
        
        return response
    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories', methods=['GET'])

    def retrieve_allcategories():
        categories = Category.query.all()
        if len(categories) == 0:
            abort(404)
        categories_all = [categorie.format() for categorie in categories]

        return jsonify({
            'categories': categories_all,
            'success' : True
        })

    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """

    @app.route('/questions',methods = ['GET'])
    def Get_All_Question():
        allquestion = Question.query.all()
        questionperpage = question_pagination(request, allquestion)
        categorys = retrieve_allcategories()

        if len(question_pagination) == 0:
            abort(404)
        
        return jsonify({
            'success': True,
            'Total_questions': len(allquestion),
            'categories': categorys,
            'questions': questionperpage
        })

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """

    @app.route('/questions/<question_id>', methods=['DELETE'])
    def Delete_One_Question(question_id):
        delete_question = Question.query.filter(Question.id==question_id).one_or_none()
        if delete_question is None:
            abort(422)
        try:
            delete_question.delete()
            return jsonify({
                'success': True,
                'deleted': question_id,
                'totalquestions': len(Question.query.all())
            })
        except :
            abort(422)
    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    app.route('/questions', methods = ['POST'])
    def add_question():
        body = request.get_json()
        question_new = body.get('question', None)
        response_new = body.get('answer', None)
        category = body.get('category', None)
        difficulty = body.get('difficulty', None)
        searchTerm = body.get('searchTerm', None)

        try:
            if question_new is None or response_new is None or difficulty is None or category is None:
                abort(422)
            else:
                question = Question(question=question_new, answer=response_new,
                                difficulty=difficulty,
                                category=category)
                question.insert()
                return jsonify({
                'success': True,
                'new_question_id': question.id,
                'new_question': question.question,
                'total_questions': len(Question.query.all()),
            })
        except:
            abort(422)

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route('/questions/search', methods=['POST'])
    def search_question():
        search = request.args.get('search')
        selection = Question.query.filter(Question.question.ilike('%{}%'.format(search))).all()
        search_questions = question_pagination(request, selection)
        if search is None:
            abort(404)
        
        return jsonify(
            {
                'success': True,
                'questions': list(search_questions),
                "total_question": len(selection)
            }
        )



    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<int:category_id>/questions')
    def category_per_question(category_id):
        category = Category.query.filter_by(id=category_id).one_or_none()
        if category is not None:
            question_per_category = Question.query.filter_by(
                category = str(category_id)).all()
                
            if question_per_category is not None:
                paginated_question = paginated_question(request, question_per_category)

                return jsonify(
                    {
                        'success': True,
                        'questions':paginated_question,
                        'total_questions': len(question_per_category),
                        'current_category': category.type
                    }
                )
            abort(404)
        abort(404)


    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route('/quizzes', methods=['POST'])
    def get_quiz():

    
        try:
                
            data = request.json
            category_id = data["quiz_category"]["id"]
            previous_questions_id = data["previous_questions"]

            if category_id != 0:
                questions_left_in_category = Question.query.filter(
                    Question.category == category_id).filter(
                        Question.id.notin_(previous_questions_id)).all()
            else:
                questions_left_in_category = Question.query.filter(
                    Question.id.notin_(previous_questions_id)).all()

            question = random.choice(questions_left_in_category).format() if len(
                questions_left_in_category) else False

            return jsonify({"question" : question})
        except Exception:
                abort(422)

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
        "success":False,
        "error":404,
        "message": "not found"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
        "success":False,
        "error":422,
        "message": "unprocessable"
        }), 422

    return app

