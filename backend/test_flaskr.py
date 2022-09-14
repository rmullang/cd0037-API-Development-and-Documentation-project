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
        self.database_path = "postgres://{}/{}".format(
            'localhost:5432', self.database_name)
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
    # test get categories

    def test_retrieve_categories(self):

        res = self.client().get('/api/v1/categories')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
     
    # try to get catetory not existings
    def test_404retrieve_categories(self):

        res = self.client().get('/api/v1/categories/999999999')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)


    # test retrieve_questions

    def test_retrieve_questions(self):

        res = self.client().get('/api/v1/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])

    def test_404retrieve_questions(self):

        res = self.client().get('/api/v1/questions?page=9999999999')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)

            
    # test_delete_questions

    def test_delete_question(self):

        # insert a question and then delete it to make sure the test case
        # always works
        question = Question("What is sum of 2 and 3", "5", 1, 1)
        question.insert()
        print(question)
        id = format(question.id)

        print(id)
        res = self.client().delete("/api/v1/questions/" + id)
        data = json.loads(res.data)
        print(res.status_code)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['deleted'])
    
    # test 404 for delete question
    def test_404delete_question(self):

        #set id as string so it will not be found
        id="abcd"
        res = self.client().delete("/api/v1/questions/" + id)
        data = json.loads(res.data)
        print(res.status_code)
        self.assertEqual(res.status_code, 404)

    
    # test add question
    def test_add_question(self):

        res = self.client().post(
            "/api/v1/questions",
            json={
                "question": "test",
                "answer": "test12233",
                "difficulty": 1,
                "category": 1})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_422add_question(self):

        res = self.client().post(
            "/api/v1/questions",
            json={
                "question": "test",
                "difficulty": 1,
                "category": 1})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)

    # test search for question
    def test_searchfor_questions(self):

        res = self.client().post(
            "/api/v1/questions/search",
            json={
                "searchTerm": "test"})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])

    def test_404searchfor_questions(self):

        res = self.client().post(
            "/api/v1/questions/search",
            json={})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)


    def test_get_category_questions(self):

        res = self.client().get("/api/v1/categories/1/questions")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
    
    def test_get_404category_questions(self):

        res = self.client().get("/api/v1/categories/somecategory/questions")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)

    def test_get_quiz(self):

        res = self.client().post(
            "/api/v1/quizzes",
            json={
                "previous_questions": [
                    1,
                    2,
                    3],
                "quiz_category": {
                    "id": 1,
                    "type": "Science"}})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])

   
    def test_422get_quiz(self):

        res = self.client().post(
            "/api/v1/quizzes",
            json={
                "quiz_category": {
                    "id": 1,
                    "type": "Science"}})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
