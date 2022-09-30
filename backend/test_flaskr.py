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
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
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

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_paginated_questions(self):
        response = self.client().get('/categories')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_questions"])
        self.assertTrue(len(data["categories"]))
        self.assertTrue(len(data["questions"]))

    # Test request 404
    def test_bad_request(self):
        response = self.client().get('/questions?page=1000')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
    
    # test all categories
    def test_categories(self):
        response = self.client().get('/categories')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["categories"])

    def test_categories_not_allowed(self):
        response = self.client().delete('/categories')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 405)
        self.assertEqual(data["success"], False)

    # Test delete question
    def test_delete_questions(self):
        response = self.client().delete('/questions/9')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)

    def test_delete_questions_not_found(self):
        response = self.client().delete('/questions/10000')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Page not found")
    
    # Test create questions : 
    def test_create_question(self):
        new_Question = {
            'question': 'what is your Country?',
            'answer': 'Tunisia',
            'difficulty': 2,
            'category': 1
        }
        res = self.client().post('/questions', json=new_Question)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()