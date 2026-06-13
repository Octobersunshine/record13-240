from flask import Flask, request, jsonify
from question_bank import QuestionBank

app = Flask(__name__)

STOP_WORDS = ['的', '了', '和', '是', '在', '我', '有', '这', '那', '什么', '怎么', '如何', '吗', '呢', '啊', '吧']
question_bank = QuestionBank(data_file='questions.json', stop_words=STOP_WORDS)


@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'ok',
        'questions_count': len(question_bank)
    })


@app.route('/api/questions', methods=['GET'])
def get_all_questions():
    questions = question_bank.get_all_questions()
    return jsonify({
        'count': len(questions),
        'questions': questions
    })


@app.route('/api/questions/<int:question_id>', methods=['GET'])
def get_question(question_id):
    question = question_bank.get_question(question_id)
    if question:
        return jsonify(question)
    return jsonify({'error': 'Question not found'}), 404


@app.route('/api/questions', methods=['POST'])
def add_question():
    data = request.get_json()
    if not data or 'id' not in data or 'text' not in data:
        return jsonify({'error': 'Missing required fields: id and text'}), 400

    question_id = data['id']
    text = data['text']
    meta = {k: v for k, v in data.items() if k not in ['id', 'text']}

    success = question_bank.add_question(question_id, text, **meta)
    if success:
        return jsonify({
            'message': 'Question added successfully',
            'id': question_id
        }), 201
    return jsonify({'error': 'Question with this id already exists'}), 409


@app.route('/api/questions/batch', methods=['POST'])
def add_questions_batch():
    data = request.get_json()
    if not data or 'questions' not in data:
        return jsonify({'error': 'Missing required field: questions'}), 400

    questions = data['questions']
    count = question_bank.add_questions(questions)
    return jsonify({
        'message': f'Added {count} questions',
        'added_count': count
    }), 201


@app.route('/api/questions/<int:question_id>', methods=['PUT'])
def update_question(question_id):
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({'error': 'Missing required field: text'}), 400

    text = data['text']
    meta = {k: v for k, v in data.items() if k not in ['id', 'text']}

    success = question_bank.update_question(question_id, text, **meta)
    if success:
        return jsonify({
            'message': 'Question updated successfully',
            'id': question_id
        })
    return jsonify({'error': 'Question not found'}), 404


@app.route('/api/questions/<int:question_id>', methods=['DELETE'])
def delete_question(question_id):
    success = question_bank.remove_question(question_id)
    if success:
        return jsonify({'message': 'Question deleted successfully'})
    return jsonify({'error': 'Question not found'}), 404


@app.route('/api/detect/similar', methods=['POST'])
def detect_similar():
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({'error': 'Missing required field: text'}), 400

    text = data['text']
    top_k = data.get('top_k', 5)
    threshold = data.get('threshold', 0.7)

    similar_questions = question_bank.find_similar_questions(text, top_k, threshold)
    return jsonify({
        'input_text': text,
        'similar_count': len(similar_questions),
        'similar_questions': similar_questions
    })


@app.route('/api/detect/duplicate', methods=['POST'])
def detect_duplicate():
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({'error': 'Missing required field: text'}), 400

    text = data['text']
    threshold = data.get('threshold', 0.9)

    result = question_bank.check_duplicate(text, threshold)
    return jsonify({
        'input_text': text,
        **result
    })


@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
