import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

# =============================================================================
# Pagination question
# =============================================================================
def paginate_questions(request, selection):
    pages = request.args.get("page", 1, type=int)
    start = (pages - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions_list = [question.format() for question in selection]
    current_questions = questions_list[start:end]

    return current_questions
# Get current category : 
def get_current_category(questions_categories, all_categories):
    cat_sample = 0
    count = 0
    current_category = ""
    for cat in questions_categories:
        if count > 0:
            if (cat != cat_sample):
                current_category = "All"
                break
            else:
                current_category = all_categories[0].type
        else:
            cat_sample = cat
            count += 1
    return current_category

def get_next_question(selection, previous_questions):    
    new_question = None
    new_question_bool = False

    for question in selection:
        new_question_bool = True

        for pq_id in previous_questions:
            if (question["id"] == pq_id):
                new_question_bool = False
                break

        if new_question_bool :
            new_question = question
            break
    
    return new_question


# =============================================================================
# TRIVIA APP START
# =============================================================================
def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app)

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        return response

    """
    @done:
    Create an endpoint to handle GET requests
    for all available categories.
    ok
    """
    @app.route("/categories", methods=['GET'])
    def retrieve_all_categories():

        categories_list_data = [category.format2() for category in Category.query.all()] # format2 is defined in models.py

        categories = {}
        for categorys in categories_list_data:
            categories.update(categorys)

        if len(categories) == 0:
            abort(404)

        return jsonify(
            {
                "success": True,
                "categories": categories,
                "total_categories": len(Category.query.all())
            }
        )



    """
    @done:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    oki
    """
    

    @app.route('/questions',methods = ['GET'])
    def Get_All_Question():
        selections = Question.query.order_by(Question.id).all()
        question = paginate_questions(request, selections)
        categories_query = retrieve_all_categories().get_json('categories')
        categories = categories_query['categories']
        

        if not len(question):
            abort(404)
        else:
            return jsonify(
                {
                    "success": True,
                    "questions": question,
                    "total_questions": len(selections),
                    "categories": categories,
                    "current_category" : list(categories.items())[0][1] # get the value of the first element (in case categorie id 1 doesnt exist)
                }
        )


    """
    @done:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def delete_question_by_id(question_id):
        try:
            question_id = Question.query.filter(Question.id == question_id).one_or_none()

            if question_id is None:
                abort(404)

            question_id.delete()
            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)

            return jsonify(
                {
                    "success": True,
                    "deleted": question_id,
                    "questions": current_questions,
                    "total_questions": len(Question.query.all()),
                }
            )

        except:
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
    @app.route("/questions", methods=["POST"])
    def create_new_question():
        body = request.get_json()

        new_questions = body.get("question", None)
        new_answers = body.get("answer", None)
        new_difficultys = body.get("difficulty", None)
        new_categorys = body.get("category", None)

        try:
            questions = Question(
                question=new_questions, 
                answer=new_answers, 
                difficulty=new_difficultys, 
                category=new_categorys
                )

            questions.insert()

            selections = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selections)

            return jsonify(
                {
                    "success": True,
                    "created": questions.id,
                    "questions": current_questions,
                    "total_questions": len(Question.query.all()),
                }
            )

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
    

    @app.route("/questions/search", methods=["POST"])
    def search_questions():        
        body = request.get_json()

        search_terms = body.get("searchTerm", None).lower()

        totalQuestion = 0
        found_question = []
        all_categorie = Category.query.order_by(Category.id).all()
        questions_categorie = []

        for one_question in Question.query.order_by(Question.id).all():
            if (one_question.question.lower().find(search_terms) != -1):
                totalQuestion += 1
                found_question.append(one_question.format())
                questions_categorie.append(one_question.category)

        current_category = get_current_category(questions_categorie, all_categorie)
        
        return jsonify(
                {
                    "success": True,
                    "questions": found_question,
                    "current_category": current_category,
                    "total_questions": totalQuestion,
                }
            )
    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route("/categories/<int:category_id>/questions")
    def retrieve_category_questions(category_id):
        selections = Question.query.filter_by(category = category_id).order_by(Question.id).all()
        current_question = paginate_questions(request, selections)

        current_category = Category.query.get(category_id).type

        if len(current_question) == 0:
            abort(404)

        return jsonify(
            {
                "success": True,
                "questions": current_question,
                "current_category": current_category,
                "total_questions": len(selections),
            }
        )

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
    @app.route("/quizzes", methods=["POST"])
    def get_quizz():        
        body = request.get_json()

        previous_question = body.get("previous_questions", None)
        quiz_categories = body.get("quiz_category", None)

        if quiz_categories["id"] == 0:
            selection = Question.query.order_by(Question.id).all()
        else:
            selection = Question.query.filter_by(category = quiz_categories["id"]).order_by(Question.id).all()

        selection = [question.format() for question in selection]

        new_question = get_next_question(selection, previous_question)
        
        
        return jsonify(
                {
                    "success": True,
                    "question": new_question
                }
            )

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 404, "message": "resource not found"}),
            404,
        )

    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify({"success": False, "error": 422, "message": "unprocessable"}),
            422,
        )

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"success": False, "error": 400, "message": "bad request"}), 400

    @app.errorhandler(405)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 405, "message": "method not allowed"}),
            405,
        )
    
    @app.errorhandler(500)
    def internal_error_server(error):
        return (
            jsonify({"success": False, "error": 405, "message": "the server encountered."}),
            500,
        )

    return app

