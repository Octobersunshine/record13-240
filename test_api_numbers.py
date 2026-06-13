import json
import requests

BASE_URL = 'http://localhost:5000'


def test_number_difference_api():
    print("=" * 60)
    print("API 数字差异测试")
    print("=" * 60)

    print("\n1. 清空现有题目")
    resp = requests.get(f'{BASE_URL}/api/questions')
    for q in resp.json()['questions']:
        requests.delete(f'{BASE_URL}/api/questions/{q["id"]}')

    print("\n2. 添加数字测试题目")
    test_questions = [
        {"id": 1, "text": "3+5等于多少？", "subject": "数学"},
        {"id": 2, "text": "4+6等于多少？", "subject": "数学"},
        {"id": 3, "text": "计算3+5的结果", "subject": "数学"},
        {"id": 4, "text": "3×5等于多少？", "subject": "数学"},
        {"id": 5, "text": "求x²+2x+1=0的解", "subject": "数学"},
        {"id": 6, "text": "求x²+3x+2=0的解", "subject": "数学"},
    ]
    resp = requests.post(f'{BASE_URL}/api/questions/batch', json={'questions': test_questions})
    print(f"   状态: {resp.status_code}, 添加了 {resp.json()['added_count']} 道题")

    print("\n3. 测试: '3+5等于多少？' 不匹配 '4+6等于多少？'")
    detect_data = {
        'text': '3+5等于多少？',
        'top_k': 10,
        'threshold': 0.1
    }
    resp = requests.post(f'{BASE_URL}/api/detect/similar', json=detect_data)
    data = resp.json()
    print(f"   输入: {data['input_text']}")
    print(f"   匹配结果:")
    for item in data['similar_questions']:
        flag = "✓" if item['id'] in [1, 3] else "✗"
        print(f"     {flag} [{item['similarity']:.4f}] ID:{item['id']} | {item['text']}")

    print("\n4. 测试: '3+5等于多少？' 不匹配 '3×5等于多少？'（运算符不同）")
    detect_data = {
        'text': '3+5等于多少？',
        'top_k': 10,
        'threshold': 0.6
    }
    resp = requests.post(f'{BASE_URL}/api/detect/similar', json=detect_data)
    data = resp.json()
    has_multiply = any('×' in item['text'] for item in data['similar_questions'])
    print(f"   输入: {data['input_text']}")
    print(f"   阈值0.6以上匹配数: {data['similar_count']}")
    print(f"   是否包含乘法题: {'是' if has_multiply else '否'}")
    if not has_multiply:
        print("   ✓ 正确: 运算符不同的题目未被匹配")

    print("\n5. 测试: 'x²+2x+1=0' 不匹配 'x²+3x+2=0'")
    detect_data = {
        'text': '求x²+2x+1=0的解',
        'top_k': 10,
        'threshold': 0.5
    }
    resp = requests.post(f'{BASE_URL}/api/detect/similar', json=detect_data)
    data = resp.json()
    print(f"   输入: {data['input_text']}")
    print(f"   匹配结果:")
    for item in data['similar_questions']:
        flag = "✓" if item['id'] == 5 else "✗"
        print(f"     {flag} [{item['similarity']:.4f}] ID:{item['id']} | {item['text']}")

    print("\n6. 测试: 相同数字不同表述仍能匹配")
    detect_data = {
        'text': '请问3+5等于几？',
        'top_k': 5,
        'threshold': 0.6
    }
    resp = requests.post(f'{BASE_URL}/api/detect/similar', json=detect_data)
    data = resp.json()
    print(f"   输入: {data['input_text']}")
    print(f"   匹配结果:")
    for item in data['similar_questions']:
        flag = "✓" if '3+5' in item['text'] else "✗"
        print(f"     {flag} [{item['similarity']:.4f}] ID:{item['id']} | {item['text']}")

    print("\n" + "=" * 60)
    print("API 数字差异测试完成")
    print("=" * 60)


if __name__ == '__main__':
    try:
        test_number_difference_api()
    except requests.exceptions.ConnectionError:
        print("错误: 无法连接到服务器，请先运行 python app.py 启动服务")
