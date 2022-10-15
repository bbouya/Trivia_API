import os
import unittest
import json
from urllib import response
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):

        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.db_user = 'postgres'
        self.db_pwd = '1234'
        self.db_host = 'localhost:5432'
        self.database_name = "trivia"
        self.database_path = "postgresql://{}:{}@{}/{}".format(
            self.db_user,
            self.db_pwd,
            self.db_host,
            self.database_name
            )
        setup_db(self.app, self.database_path)

        
        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

# ---------------------------------------#
# test paginated questions
# ---------------------------------------#

    def test_paginated_questions(self):
        response = self.client().get('/questions')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_questions"])
        self.assertTrue(len(data["categories"]))
        self.assertTrue(len(data["questions"]))


# ---------------------------------------#
# ~~~test bad request
# ---------------------------------------#
    def test_get_bad_request(self):
        response = self.client().get('/questions?page=9999')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Bad request')

# ---------------------------------------#
# ~~~test categories
# ---------------------------------------#
    def test_get_categories(self):
        response = self.client().get('/categories')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["categories"])

    def test_get_categories_not_allowed(self):
        response = self.client().delete('/categories')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 405)
        self.assertEqual(data["success"], False)

# ---------------------------------------#
# ~~~test delete questions
# ---------------------------------------#
    def test_delete_question(self):
        response = self.client().delete('/questions/9')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)

    def test_delete_question_not_found(self):
        response = self.client().delete('/questions/10000')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Page not found")

# ---------------------------------------#
# ~~~test create questions
# ---------------------------------------#
    def test_create_question(self):
        res = self.client().post('/questions', json={
            'question': 'what is your Country ?',
            'answer': 'Morroco',
            'difficulty': 2,
            'category': 1
        })
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)

# ---------------------------------------#
# ~~~test search questions
# ---------------------------------------#
    def test_search_question(self):
        response = self.client().post('questions/search',
                                 json={"searchTerm": "what"})
        data = json.loads(response.data)

        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])

    def test_search_not_found(self):
        search = {
            'searchTerm': 'blah',
        }
        response = self.client().post('/search', json=search)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Page not found')

# ---------------------------------------#
# ~~~test questions per category
# ---------------------------------------#
    def test_questions_per_category(self):
        response = self.client().get('/categories/1/questions')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertNotEqual(len(data['questions']), 0)
        self.assertEqual(data['current_category'], 'Science')

    def test_questions_per_category_not_found(self):
        response = self.client().get('/categories/100/questions')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)


#-----------------------------------------------------------
#-----------------------------------------------------------

    def test_play_quiz(self):
        response = self.client().post('/quizzes', json= {
            'previous_questions': [], 'quiz_category': {
                'type': 'Geography', 'id': 15}
        })
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

#-----------------------------------------------------------
#-----------------------------------------------------------

    def test_404_play_quiz(self):
        response = self.client().post('/quizzes', json={'previous_questions': []})
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")
# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()