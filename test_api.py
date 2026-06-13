import json
import requests

BASE_URL = 'http://localhost:5000'


def test_api():
    print("=" * 60)
    print("API 功能测试")
    print("=" * 60)

    print("\n1. 健康检查")
    resp = requests.get(f'{BASE_URL}/api/health')
    print(f"   状态: {resp.status_code}, 响应: {resp.json()}")

    print("\n2. 批量添加测试题目")
    with open('sample_questions.json', 'r', encoding='utf-8') as f:
        questions = json.load(f)
    resp = requests.post(f'{BASE_URL}/api/questions/batch', json={'questions': questions})
    print(f"   状态: {resp.status_code}, 响应: {resp.json()}")

    print("\n3. 获取所有题目")
    resp = requests.get(f'{BASE_URL}/api/questions')
    data = resp.json()
    print(f"   状态: {resp.status_code}, 题目总数: {data['count']}")

    print("\n4. 添加单个新题目")
    new_q = {
        'id': 100,
        'text': '测试题目：1+1等于几？',
        'subject': '数学',
        'type': '选择题',
        'difficulty': '简单'
    }
    resp = requests.post(f'{BASE_URL}/api/questions', json=new_q)
    print(f"   状态: {resp.status_code}, 响应: {resp.json()}")

    print("\n5. 获取单个题目 (ID=1)")
    resp = requests.get(f'{BASE_URL}/api/questions/1')
    print(f"   状态: {resp.status_code}, 题目: {resp.json().get('text', 'N/A')}")

    print("\n6. 更新题目 (ID=100)")
    update_q = {
        'text': '更新后：1+1等于多少？',
        'subject': '数学',
        'type': '填空题',
        'difficulty': '入门'
    }
    resp = requests.put(f'{BASE_URL}/api/questions/100', json=update_q)
    print(f"   状态: {resp.status_code}, 响应: {resp.json()}")

    print("\n7. 相似题目检测")
    detect_data = {
        'text': '求函数 y = x² + 2x + 1 的最小值',
        'top_k': 3,
        'threshold': 0.7
    }
    resp = requests.post(f'{BASE_URL}/api/detect/similar', json=detect_data)
    data = resp.json()
    print(f"   状态: {resp.status_code}")
    print(f"   输入: {data['input_text']}")
    print(f"   相似题数: {data['similar_count']}")
    for item in data['similar_questions']:
        print(f"     - ID:{item['id']} 相似度:{item['similarity']:.4f} | {item['text']}")

    print("\n8. 重复题目检测")
    dup_data = {
        'text': '李白是什么朝代的诗人',
        'threshold': 0.85
    }
    resp = requests.post(f'{BASE_URL}/api/detect/duplicate', json=dup_data)
    data = resp.json()
    print(f"   状态: {resp.status_code}")
    print(f"   输入: {data['input_text']}")
    print(f"   是否重复: {data['is_duplicate']}")
    for item in data['duplicates']:
        print(f"     - ID:{item['id']} 相似度:{item['similarity']:.4f} | {item['text']}")

    print("\n9. 删除题目 (ID=100)")
    resp = requests.delete(f'{BASE_URL}/api/questions/100')
    print(f"   状态: {resp.status_code}, 响应: {resp.json()}")

    print("\n" + "=" * 60)
    print("API 测试完成")
    print("=" * 60)


if __name__ == '__main__':
    try:
        test_api()
    except requests.exceptions.ConnectionError:
        print("错误: 无法连接到服务器，请先运行 python app.py 启动服务")
