import json
from question_bank import QuestionBank

STOP_WORDS = ['的', '了', '和', '是', '在', '我', '有', '这', '那', '什么', '怎么', '如何', '吗', '呢', '啊', '吧']

bank = QuestionBank(data_file='test_numbers.json', stop_words=STOP_WORDS)
bank.clear()

test_questions = [
    {"id": 1, "text": "3+5等于多少？", "subject": "数学"},
    {"id": 2, "text": "4+6等于多少？", "subject": "数学"},
    {"id": 3, "text": "计算3+5的结果", "subject": "数学"},
    {"id": 4, "text": "请问3+5等于几？", "subject": "数学"},
    {"id": 5, "text": "10-7等于多少？", "subject": "数学"},
    {"id": 6, "text": "3×5等于多少？", "subject": "数学"},
    {"id": 7, "text": "求x²+2x+1=0的解", "subject": "数学"},
    {"id": 8, "text": "求x²+3x+2=0的解", "subject": "数学"},
]

count = bank.add_questions(test_questions)
print(f"添加了 {count} 道测试题目\n")

print("=" * 70)
print("测试: 数字不同的题目是否被正确区分")
print("=" * 70)

test_cases = [
    ("3+5等于多少？", 0.7),
    ("4+6等于多少？", 0.7),
    ("3+5等于几？", 0.7),
    ("计算3+5", 0.7),
    ("10-7等于多少？", 0.7),
    ("3×5等于多少？", 0.7),
    ("求x²+2x+1=0的解", 0.7),
]

for test_text, threshold in test_cases:
    print(f"\n输入: {test_text}")
    print(f"阈值: {threshold}")
    similar = bank.find_similar_questions(test_text, top_k=5, threshold=threshold)
    print(f"找到 {len(similar)} 道相似题目:")
    for item in similar:
        print(f"  [{item['similarity']:.4f}] ID:{item['id']} | {item['text']}")

print("\n" + "=" * 70)
print("关键验证: '3+5' vs '4+6' 应该不相似")
print("=" * 70)

test_text = "3+5等于多少？"
similar = bank.find_similar_questions(test_text, top_k=10, threshold=0.1)
print(f"输入: {test_text}")
print("所有匹配结果（含低相似度）:")
for item in similar:
    flag = "✓" if item['id'] in [1, 3, 4] else "✗"
    print(f"  {flag} [{item['similarity']:.4f}] ID:{item['id']} | {item['text']}")

print("\n" + "=" * 70)
print("关键验证: 'x²+2x+1=0' vs 'x²+3x+2=0' 应该不相似")
print("=" * 70)

test_text = "求x²+2x+1=0的解"
similar = bank.find_similar_questions(test_text, top_k=10, threshold=0.1)
print(f"输入: {test_text}")
print("所有匹配结果（含低相似度）:")
for item in similar:
    flag = "✓" if item['id'] == 7 else "✗"
    print(f"  {flag} [{item['similarity']:.4f}] ID:{item['id']} | {item['text']}")
