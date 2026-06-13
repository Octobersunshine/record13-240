from similarity_detector import SimilarityDetector

STOP_WORDS = ['的', '了', '和', '是', '在', '我', '有', '这', '那', '什么', '怎么', '如何', '吗', '呢', '啊', '吧']

detector = SimilarityDetector(stop_words=STOP_WORDS)

test_questions = [
    {'id': 1, 'text': '计算 3 + 5 等于多少'},
    {'id': 2, 'text': '求解 4 + 6 的结果'},
    {'id': 3, 'text': '请问 8 - 2 是多少'},
    {'id': 4, 'text': '计算 3 × 5 的积'},
    {'id': 5, 'text': '3 + 5 等于多少'},
    {'id': 6, 'text': '求函数 y = x^2 + 2x + 1 的最小值'},
    {'id': 7, 'text': '求函数 y = x^2 + 3x + 2 的最小值'},
    {'id': 8, 'text': '李白是哪个朝代的诗人'},
    {'id': 9, 'text': '小明有10个苹果，吃了3个，还剩几个？'},
    {'id': 10, 'text': '小红有15个苹果，吃了5个，还剩几个？'},
    {'id': 11, 'text': '计算 12 ÷ 3 等于多少'},
    {'id': 12, 'text': '求解方程 2x + 3 = 7'},
    {'id': 13, 'text': '求解方程 3x + 5 = 11'},
]

for q in test_questions:
    detector.add_question(q['id'], q['text'])

print("=" * 70)
print("数字感知相似度检测 - 修复验证测试")
print("=" * 70)

test_cases = [
    ("计算 3 + 5 等于多少", 0.7, "相同数字相同运算符"),
    ("计算 4 + 6 等于多少", 0.7, "不同数字相同运算符"),
    ("计算 8 - 2 等于多少", 0.7, "不同数字不同运算符"),
    ("3 + 5 是多少", 0.7, "相同数字相似表述"),
    ("求函数 y = x^2 + 2x + 1 的最小值", 0.7, "数学函数题"),
    ("小明有10个苹果，吃了3个，还剩几个？", 0.7, "应用题数字相同"),
    ("小红有8个苹果，吃了2个，还剩几个？", 0.7, "应用题数字不同"),
    ("求解方程 2x + 3 = 7", 0.7, "方程题数字相同"),
    ("李白是哪个朝代的诗人", 0.7, "非数学题（无数字）"),
]

for input_text, threshold, desc in test_cases:
    print(f"\n{desc}")
    print(f"输入: {input_text}")
    print(f"阈值: {threshold}")
    results = detector.find_similar(input_text, top_k=5, threshold=threshold)
    if results:
        print(f"匹配到 {len(results)} 道相似题:")
        for qid, sim, meta in results:
            target_text = detector.questions[detector.question_ids.index(qid)]
            print(f"  - ID={qid:2d}  相似度={sim:.4f}  | {target_text}")
    else:
        print("未匹配到相似题目")

print("\n" + "=" * 70)
print("关键对比测试（修复前后对比）")
print("=" * 70)

print("\n1. 修复前问题: '8-2' vs '3+5' 原本相似度 0.7333（误判为相似）")
print("   输入: 计算 8 - 2 等于多少")
results = detector.find_similar("计算 8 - 2 等于多少", top_k=3, threshold=0.1)
for qid, sim, meta in results:
    target_text = detector.questions[detector.question_ids.index(qid)]
    print(f"   - ID={qid:2d}  相似度={sim:.4f}  | {target_text}")

print("\n2. 数字完全不同但结构相同:")
print("   输入: 计算 4 + 6 等于多少")
results = detector.find_similar("计算 4 + 6 等于多少", top_k=3, threshold=0.1)
for qid, sim, meta in results:
    target_text = detector.questions[detector.question_ids.index(qid)]
    print(f"   - ID={qid:2d}  相似度={sim:.4f}  | {target_text}")

print("\n3. 数字完全相同应该匹配:")
print("   输入: 3 + 5 等于多少")
results = detector.find_similar("3 + 5 等于多少", top_k=3, threshold=0.1)
for qid, sim, meta in results:
    target_text = detector.questions[detector.question_ids.index(qid)]
    print(f"   - ID={qid:2d}  相似度={sim:.4f}  | {target_text}")

print("\n" + "=" * 70)
print("测试完成")
print("=" * 70)
