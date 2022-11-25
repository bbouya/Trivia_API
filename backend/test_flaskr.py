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





    # Delete question tests
    def test_delete_by_id_question(self):
        res = self.client().delete("/questions/20")
        response_data = json.loads(res.data)

        question = Question.query.filter(Question.id == 20).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(response_data["success"], True)
        self.assertEqual(response_data["deleted"], 20)
        self.assertTrue(response_data["total_questions"])
        self.assertTrue(len(response_data["questions"]))
        self.assertEqual(question, None)

    def test_if_question_does_not_exist_422(self):
        res = self.client().delete("/questions/5000")
        response_data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(response_data["success"], False)
        self.assertEqual(response_data["message"], "error 422")

    # create question tests
    def test_create_new_question(self):
        res = self.client().post("/questions", json=self.new_question)
        response_data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(response_data["success"], True)
        self.assertTrue(response_data["created"])
        self.assertTrue(len(response_data["questions"]))

    def test_405_if_question_creation_not_allowed(self):
        res = self.client().post("/questions/45", json=self.new_question)
        response_data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(response_data["success"], False)
        self.assertEqual(response_data["message"], "method not allowe")

    # search question tests
    def test_search_by_questions(self):
        res = self.client().post("/questions/search", json=self.new_search)
        response_data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(response_data["success"], True)
        self.assertTrue(response_data["total_questions"])
        self.assertTrue(len(response_data["questions"]))
        self.assertTrue(response_data["current_category"])

    # get questions based on category test
    def test_retrieve_category_questions(self):
        res = self.client().get("/categories/3/questions")
        response_data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(response_data["success"], True)
        self.assertTrue(response_data["total_questions"])
        self.assertTrue(len(response_data["questions"]))
        self.assertTrue(response_data["current_category"])

    # get quizz question test
    def test_quizz(self):
        res = self.client().post("/quizzes", json={"previous_questions": [5,4,3], "quiz_category":{"type": None, "id":0}})
        response_data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(response_data["success"], True)
        self.assertTrue(response_data["question"])

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()