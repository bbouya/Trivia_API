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

        # for test
        self.new_question = {"question": "What is your favorite subject in school???",
                             "answer": "new answers", 
                             "difficulty": "1", 
                             "category": "1"}

        self.quiz = {'previous_questions': [],
                     'quiz_category': {'type': 'Science', 'id': '1'}}


        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass





# Test categories : 
    def test_get_categories_success(self):
        res = self.client().get('/categories')
        response_data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(response_data['success'])

# Test questions  :
    def test_get_question(self):
        res = self.client().get('/questions')
        response_data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(response_data['success', True])

    def test_get_question_erro(self):
        res = self.client().get('/questions?page=2000')
        response_data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(response_data['success'], False)

    # Test delete question with id 1
    def test_delete_question(self):
        res = self.client().delete('/questions/1')
        response_data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['success'], True)
        self.assertEqual(res.data['delete'], 1)

    # test delete question with id in not exist
    def test_delete_question_id_404(self):
        res = self.client().delete('questions/5000')
        response_data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)

    # Test creation of question 
    def test_create_question(self):
        res = self.client().post('/questions', json=self.new_question)
        response_data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(response_data['success'], True)

    def test_question_creation_not_allowed_405(self):
        res = self.client().post('/questions/45', json=self.new_question)
        response_data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(response_data['success'], False)
        self.assertEqual(response_data['message'], 'not allowed')


    # Test ssearch
    
    def test_search_post(self):
        response = self.client().post('/questions', json={'searchTerm': 'invented'})

        response_data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['success'], True)

    def test_search_without_results_post(self):
        response = self.client().post('/questions', json={'searchTerm':'ayoub'})

        response_data = json.loads(response.data)

        self.assertEqual(response_data['total_questions'],0)
        self.assertEqual(response_data['success'], True)
    

    # test get questions by categorys
    def test_get_questions_by_categorys(self):
        response = self.client().get('/categories/1/questions')
        response_data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['current_category'], 'Science')
        self.assertEqual(response_data['success'], True)

    def test_get_questions_by_categorys_404(self):
        response = self.client().get('/categories/1000/questions')
        response_data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response_data['message'], 'not found')
        self.assertEqual(response_data['success'], False)

    # test quiz
    def test_quiz(self):
        quiz_round = {'previous_questions': [], 'quiz_category': {'type': 'science', 'id': 55}}
        response = self.client().post('/play', json=quiz_round)
        response_data = json.loads(response.data)

        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['success'], True)

    def test_422_quiz(self):
        response = self.client().post('/play', json={})
        response_data = json.loads(response.data)

        self.assertEqual(response.status_code, 422)
        self.assertEqual(response_data['success'], False)
        self.assertEqual(response_data['message'], '422 quiz')

if __name__ == "__main__":
    unittest.main()