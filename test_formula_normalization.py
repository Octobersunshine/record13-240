from formula_normalizer import FormulaNormalizer
from question_bank import QuestionBank

STOP_WORDS = ['的', '了', '和', '是', '在', '我', '有', '这', '那', '什么', '怎么', '如何', '吗', '呢', '啊', '吧']

normalizer = FormulaNormalizer()

print("=" * 70)
print("测试1: 公式规范化功能")
print("=" * 70)

test_formulas = [
    ("$x^2$", "基本上标"),
    ("$x²$", "Unicode上标"),
    ("$x^{2}$", "带花括号上标"),
    ("$x_1$", "下标"),
    ("$x₁$", "Unicode下标"),
    ("$3×5$", "乘号"),
    ("$3÷5$", "除号"),
    ("$a≠b$", "不等号"),
    ("$a≤b$", "小于等于"),
    ("$a≥b$", "大于等于"),
    ("$α+β$", "希腊字母"),
    ("$sin(x)$", "三角函数"),
    ("$sqrt(2)$", "平方根函数"),
    ("$3/4$", "分数"),
    ("$x^2 + 2x + 1$", "多项式"),
    ("$x²+2x+1$", "无空格多项式"),
]

for formula, desc in test_formulas:
    normalized = normalizer.normalize_formula(formula)
    print(f"\n{desc}:")
    print(f"  原始: {formula}")
    print(f"  规范化: {normalized}")

print("\n" + "=" * 70)
print("测试2: 等价公式判定")
print("=" * 70)

equivalent_pairs = [
    ("$x^2$", "$x²$", "上标写法不同"),
    ("$x^{2}$", "$x²$", "花括号 vs Unicode"),
    ("$x_1$", "$x₁$", "下标写法不同"),
    ("$3×5$", "$3\\times5$", "乘号写法不同"),
    ("$sin(x)$", "$\\sin(x)$", "函数写法不同"),
    ("$x^2 + 2x + 1$", "$x²+2x+1$", "空格不同"),
]

for f1, f2, desc in equivalent_pairs:
    is_equiv = normalizer.are_formulas_equivalent(f1, f2)
    sim = normalizer.formula_similarity(f1, f2)
    print(f"\n{desc}:")
    print(f"  公式1: {f1}")
    print(f"  公式2: {f2}")
    print(f"  等价: {is_equiv}, 相似度: {sim:.4f}")

print("\n" + "=" * 70)
print("测试3: 不等价公式判定")
print("=" * 70)

different_pairs = [
    ("$x^2$", "$x^3$", "指数不同"),
    ("$x+1$", "$x-1$", "运算符不同"),
    ("$x^2 + 2x + 1$", "$x^2 + 3x + 2$", "系数不同"),
    ("$sin(x)$", "$cos(x)$", "函数不同"),
]

for f1, f2, desc in different_pairs:
    is_equiv = normalizer.are_formulas_equivalent(f1, f2)
    sim = normalizer.formula_similarity(f1, f2)
    print(f"\n{desc}:")
    print(f"  公式1: {f1}")
    print(f"  公式2: {f2}")
    print(f"  等价: {is_equiv}, 相似度: {sim:.4f}")

print("\n" + "=" * 70)
print("测试4: 包含公式的题目相似度检测")
print("=" * 70)

bank = QuestionBank(data_file='test_formulas.json', stop_words=STOP_WORDS)
bank.clear()

test_questions = [
    {"id": 1, "text": "求方程 $x^2 + 2x + 1 = 0$ 的解", "subject": "数学"},
    {"id": 2, "text": "求方程 $x² + 2x + 1 = 0$ 的根", "subject": "数学"},
    {"id": 3, "text": "求方程 $x^{2} + 2x + 1 = 0$ 的解", "subject": "数学"},
    {"id": 4, "text": "求方程 $x^2 + 3x + 2 = 0$ 的解", "subject": "数学"},
    {"id": 5, "text": "计算 $3×5$ 的结果", "subject": "数学"},
    {"id": 6, "text": "计算 $3\\times5$ 等于多少", "subject": "数学"},
    {"id": 7, "text": "计算 $3+5$ 的结果", "subject": "数学"},
    {"id": 8, "text": "已知 $sin(α) = 0.5$，求 $α$ 的值", "subject": "数学"},
    {"id": 9, "text": "已知 $\\sin(\\alpha) = 0.5$，求 $\\alpha$", "subject": "数学"},
    {"id": 10, "text": "求 $sqrt(2)$ 的近似值", "subject": "数学"},
    {"id": 11, "text": "求 $\\sqrt{2}$ 约等于多少", "subject": "数学"},
]

count = bank.add_questions(test_questions)
print(f"添加了 {count} 道测试题目\n")

test_cases = [
    ("求方程 $x² + 2x + 1 = 0$ 的解", "相同公式不同写法", [1, 2, 3]),
    ("求方程 $x^2 + 3x + 2 = 0$ 的解", "系数不同的公式", [4]),
    ("计算 $3×5$ 等于多少", "乘号不同写法", [5, 6]),
    ("计算 $3+5$", "运算符不同", [7]),
    ("已知 $sin(α) = 0.5$，求 $α$", "希腊字母和函数写法", [8, 9]),
    ("求 $sqrt(2)$ 的值", "平方根写法", [10, 11]),
]

for test_text, desc, expected_ids in test_cases:
    print(f"\n测试: {desc}")
    print(f"输入: {test_text}")
    similar = bank.find_similar_questions(test_text, top_k=5, threshold=0.6)
    print(f"找到 {len(similar)} 道相似题目:")
    for item in similar:
        flag = "✓" if item['id'] in expected_ids else "✗"
        print(f"  {flag} [{item['similarity']:.4f}] ID:{item['id']} | {item['text']}")

print("\n" + "=" * 70)
print("测试5: 文本中包含多个公式")
print("=" * 70)

test_text = "已知 $x^2 + y^2 = r^2$，当 $r=5$ 且 $x=3$ 时，求 $y$ 的值"
print(f"输入: {test_text}")
normalized = normalizer.normalize(test_text)
print(f"规范化: {normalized}")

print("\n" + "=" * 70)
print("测试完成")
print("=" * 70)
