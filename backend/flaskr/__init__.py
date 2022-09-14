import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate_questions(request, selection):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    # CORS for all origins *
    #CORS(app, resources={r"/*": {"origins": "*"}})
    #CORS(app, support_credentials=True)
    CORS(app)
    #app.config['CORS_HEADERS'] = 'Content-Type'

    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add(
            'Access-Control-Allow-Headers', 'Content-Type, Authorization, true'
        )
        response.headers.add(
            'Access-Control-Allow-Methods', 'GET,PUT,POST, DELETE, OPTIONS'
        )
        response.headers.add(
            'Access-Control-Allow-Origin', '*'
        )
        return response

    # End point returns all available categories.

    @app.route("/api/v1/categories")
    def retrieve_categories():
        categories = Category.query.all()

        if len(categories) == 0:
            abort(404)

        return jsonify({"success": True,
                        "categories": {category.id: category.type for category in categories},
                        "total_categories": len(categories)})

    # Endpoint to returens  questions,
    # including pagination (every 10 questions).
    # This endpoint will return a list of questions,
    # number of total questions, current category, categories.

    @app.route("/api/v1/questions", methods=["GET"])
    def retrieve_questions():
        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, selection)
        categories = Category.query.order_by(Category.type).all()

        if len(current_questions) == 0:
            abort(404)

        return jsonify({"success": True,
                        "questions": current_questions,
                        "total_questions": len(Question.query.all()),
                        "categories": {category.id: category.type for category in categories},
                        "current_category": None})

    # Endpoint to DELETE question using a question ID.

    @app.route("/api/v1/questions/<int:question_id>", methods=["DELETE"])
    def delete_question(question_id):
        try:
            question = Question.query.filter(
                Question.id == question_id).one_or_none()

            if question is None:
                return jsonify({
                    "success": False,
                    "error": 404,
                    "message": "Resource not found"
                })

            question.delete()
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

        except Exception as e:
            print(e)
            abort(422)

    # endpoint to POST a new question,
    # which will require the question and answer text,
    # category, and difficulty score.

    @app.route("/api/v1/questions", methods=['POST'])
    @cross_origin(origin='*')
    def add_question():

        try:

            requestBody = request.get_json()

            if not (
                    'question' in requestBody and 'answer' in requestBody and 'difficulty' in requestBody and 'category' in requestBody):
                abort(422)

            question = Question(
                question=requestBody.get('question'),
                answer=requestBody.get('answer'),
                difficulty=requestBody.get('difficulty'),
                category=requestBody.get('category'))

            # insertquestion to database
            question.insert()

            # return sucesswith
            return jsonify({'success': True})

        except BaseException:
            abort(422)

    # GET questions based on search term

    @app.route('/api/v1/questions/search', methods=['POST'])
    def searchfor_questions():

        requestBody = request.get_json()
        searchTerm = requestBody.get('searchTerm', None)
        try:
            if searchTerm:
                selection = Question.query.filter(Question.question.ilike
                                                  (f'%{searchTerm}%')).all()

            results = paginate_questions(request, selection)

            return jsonify({
                'success': True,
                'questions': results,
                'total_questions': len(selection),
                'current_category': None
            })
        except BaseException:
            abort(404)

    # GET questions based on category

    @app.route('/api/v1/categories/<int:id>/questions')
    def get_category_questions(id):
        category = Category.query.filter_by(id=id).one_or_none()

        try:
            selection = Question.query.filter_by(category=category.id).all()

            results = paginate_questions(request, selection)

            return jsonify({
                'success': True,
                'questions': results,
                'total_questions': len(Question.query.all()),
                'current_category': category.type
            })
        except BaseException:
            abort(400)

     # POST quiz responses

    @app.route('/api/v1/quizzes', methods=['POST'])
    def get_quiz():
        try:
            body = request.get_json()
            # get category information form request
            category = body.get('quiz_category')
            # get previous questions from request
            previousQuestions = body.get('previous_questions')

            # if not category is selected then filter on preivous questions
            # if category selected then filter on both category and
            # previousquestions
            if category['id'] == 0:
                availableQuestions = Question.query.filter(
                    Question.id.notin_(previousQuestions)).all()

            else:
                availableQuestions = Question.query.filter(
                    Question.id.notin_(previousQuestions)).filter_by(
                    category=category['id']).all()

            randomQuestionNumber = random.randint(
                0, len(availableQuestions) - 1)

            newQuestion = availableQuestions[randomQuestionNumber]

            return jsonify({
                'success': True,
                'question': newQuestion.format()
            })
        except Exception as e:
            print(e)
            abort(422)

    @app.errorhandler(400)
    def bad_request_error(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "Bad request"
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "Resource not found"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "Unprocessable"
        }), 422

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "Internal server error"
        }), 500

    return app
