import json
from question_bank import QuestionBank

STOP_WORDS = ['的', '了', '和', '是', '在', '我', '有', '这', '那', '什么', '怎么', '如何', '吗', '呢', '啊', '吧']

bank = QuestionBank(data_file='questions.json', stop_words=STOP_WORDS)
bank.clear()

with open('sample_questions.json', 'r', encoding='utf-8') as f:
    sample_questions = json.load(f)

count = bank.add_questions(sample_questions)
print(f"成功添加 {count} 道题目\n")

print("=" * 60)
print("测试1: 检测数学函数相似题")
print("=" * 60)
test_text1 = "求函数 y = x² + 2x + 1 的最小值"
similar = bank.find_similar_questions(test_text1, top_k=3, threshold=0.7)
print(f"输入题干: {test_text1}")
print(f"找到 {len(similar)} 道相似题目:")
for item in similar:
    print(f"  - ID:{item['id']} 相似度:{item['similarity']:.4f} | {item['text']}")

print("\n" + "=" * 60)
print("测试2: 检测李白朝代的重复题")
print("=" * 60)
test_text2 = "李白是什么朝代的诗人"
result = bank.check_duplicate(test_text2, threshold=0.8)
print(f"输入题干: {test_text2}")
print(f"是否重复: {result['is_duplicate']}")
if result['duplicates']:
    print("重复题目:")
    for item in result['duplicates']:
        print(f"  - ID:{item['id']} 相似度:{item['similarity']:.4f} | {item['text']}")

print("\n" + "=" * 60)
print("测试3: 检测光合作用的近似题")
print("=" * 60)
test_text3 = "请描述一下光合作用的过程"
similar = bank.find_similar_questions(test_text3, top_k=5, threshold=0.6)
print(f"输入题干: {test_text3}")
print(f"找到 {len(similar)} 道相似题目:")
for item in similar:
    print(f"  - ID:{item['id']} 相似度:{item['similarity']:.4f} | {item['text']}")

print("\n" + "=" * 60)
print("测试4: 全新题目检测（应该无相似）")
print("=" * 60)
test_text4 = "牛顿第二定律的内容是什么"
similar = bank.find_similar_questions(test_text4, top_k=3, threshold=0.6)
print(f"输入题干: {test_text4}")
print(f"找到 {len(similar)} 道相似题目")

print("\n" + "=" * 60)
print("测试5: 批量检测")
print("=" * 60)
test_texts = [
    "求函数 f(x) = x² + 2x + 1 的最小值",
    "光合作用是如何进行的",
    "水的化学式是什么"
]
for i, text in enumerate(test_texts, 1):
    similar = bank.find_similar_questions(text, top_k=2, threshold=0.7)
    print(f"{i}. {text}")
    if similar:
        for item in similar:
            print(f"     相似: {item['similarity']:.4f} | {item['text']}")
    else:
        print(f"     无相似题目")

print("\n" + "=" * 60)
print(f"题库总题数: {len(bank)}")
print("=" * 60)
