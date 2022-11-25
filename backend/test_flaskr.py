import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia"
        self.database_path = 'postgresql://{}:{}@{}/{}'.format('postgres', '1234','localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        self.new_question = {"question": "Hi", "answer": "Are you fine", "difficulty": 1, "category": 5}

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    # Get categories tests
    def test_retrieve_categorie(self):
        res = self.client().get("/categories")
        response_data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(response_data["success"], True)
        self.assertTrue(response_data["categories"])
        self.assertTrue(len(response_data["categories"]))
    
    # Get questions tests
    def test_retrieve_question(self):
        res = self.client().get("/questions")
        response_data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(response_data["success"], True)
        self.assertTrue(response_data["total_questions"])
        self.assertTrue(len(response_data["questions"]))
        self.assertTrue(response_data["categories"])
        self.assertTrue(response_data["current_category"])
        

    # TEST GET QUESTIONS BY CATEGORY
    def test_get_questions_by_category(self):
        res = self.client().get("/categories/5/questions")
        data = json.loads(res.data)
        self.assertTrue(len(data["questions"]))
        self.assertTrue(data["total_questions"])
        self.assertTrue(data["current_category"])
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)



    # TEST POST CREATE NEW QUESTION
    
    def test_create_new_question(self):
        res = self.client().post("/questions", json=self.new_question)
        data = json.loads(res.data)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['created (id)'])

    # Delete question tests
    def test_delete_by_id_question(self):
        question_id = Question.query.order_by(Question.id.desc()).first().id # last record id
        res = self.client().delete(f'/questions/{question_id}')
        response_data = json.loads(res.data)
        question = Question.query.filter(Question.id == question_id).one_or_none()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(response_data['success'], True)
        self.assertEqual(response_data['deleted (id)'], question_id)
        self.assertEqual(question, None)


    # TEST POST SEARCH QUESTIONS WITH RESULTS
    
    def test_get_question_search_results(self):
        res = self.client().post("/questions", json={"searchTerm": ""})
        response_data = json.loads(res.data)
        self.assertTrue(len(response_data["questions"]))
        self.assertTrue(response_data["total_questions"])
        self.assertTrue(response_data["current_category"])
        self.assertEqual(res.status_code, 200)
        self.assertEqual(response_data["success"], True)



    # TEST POST SEARCH QUESTIONS WITHOUT RESULT
    # SUCCESS 0
    def test_get_question_search_without_results(self):
        res = self.client().post("/questions", json={"searchTerm": "ayoub"})
        response_data = json.loads(res.data)
        self.assertEqual(len(response_data["questions"]),0)
        self.assertEqual(response_data["total_questions"], 0)
        self.assertTrue(response_data["current_category"])
        self.assertEqual(res.status_code, 200)
        self.assertEqual(response_data["success"], True)


    # TEST GET NEXT QUIZ QUESTION
    # SUCCESS
    def test_get_next_question_ifexist(self):
        previous_questions = [16,17,18]
        quiz_category = {'id': 2, 'type': "test"}
        res = self.client().post("/quizzes", json={"previous_questions": previous_questions, 'quiz_category': quiz_category})
        response_data = json.loads(res.data)
        self.assertTrue((response_data["question"]))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(response_data["success"], True)




    # TEST GET NO MORE QUIZES QUESTIONSS
    # SUCCESS 0
    def test_no_next_question(self):
        previous_questions = [16,17,18,19]
        quiz_category = {'id': 2, 'type': "test"}
        response_data = self.client().post("/quizzes", json={"previous_questions": previous_questions, 'quiz_category': quiz_category})
        data = json.loads(response_data.data)
        self.assertEqual(data["success"], True)

    # TEST DELETE delete question not processable
    # ERROR 422
    def test_unprocessable8422(self):
        res = self.client().delete("/questions/10000")
        response_data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(response_data["success"], False)
        self.assertEqual(response_data["message"], "unprocessable")

    # TEST POST BAD REQUEST
    # ERROR BAD 400
    def test_bad_request(self):
        res = self.client().post("/questions", json={"invalidkey": "Y"})
        response_data = json.loads(res.data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(response_data["success"], False)
        self.assertEqual(response_data["message"], "bad request")

    # TEST GET QUESTIONS INVALID PAGES
    # ERROR 404
    def test_sent_requesting_beyond_valid_page(self):
        res = self.client().get("/questions?page=100")
        response_data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(response_data["success"], False)
        self.assertEqual(response_data["message"], "resource not found")

    # TEST GET INVALID CATEGORIES
    # ERROR 404
    def test_invalid_categories(self):
        res = self.client().get("/categories/1000")
        response_data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(response_data["success"], False)
        self.assertEqual(response_data["message"], "resource not found")


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()