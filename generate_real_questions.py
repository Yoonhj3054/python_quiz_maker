import json
import random

questions = []
global_id = 1

def add_q(diff, topic, q_text, code, correct, fakes, explanation):
    global global_id
    opts = [str(correct)]
    for f in fakes:
        sf = str(f)
        if sf not in opts:
            opts.append(sf)
    
    # Pad to 5 if needed
    attempts = 0
    while len(opts) < 5 and attempts < 100:
        if isinstance(correct, int):
            f = str(correct + random.randint(-15, 15))
        elif isinstance(correct, str) and correct in ["True", "False"]:
            f = random.choice(["None", "0", "1", "Error"])
        else:
            f = random.choice(["None", "Error", "TypeError", "SyntaxError", "0", "1", "[]", "{}"])
        if f not in opts:
            opts.append(f)
        attempts += 1
        
    if len(opts) < 5:
        padding = ["Error", "None", "0", "1", "-1", "[]", "{}"]
        for p in padding:
            if p not in opts:
                opts.append(p)
            if len(opts) == 5:
                break
                
    random.shuffle(opts)
    correct_idx = opts.index(str(correct))
    
    questions.append({
        "id": global_id,
        "difficulty": diff,
        "topic": topic,
        "question": q_text,
        "codeSnippet": code,
        "options": opts,
        "correctAnswer": correct_idx,
        "explanation": explanation
    })
    global_id += 1

# === BEGINNER (초급) ===
def gen_beg_code():
    t = random.choice(["math", "string", "list_idx", "bool"])
    if t == "math":
        a = random.randint(1, 20)
        b = random.randint(1, 20)
        op = random.choice(['+', '-', '*'])
        code = f"a = {a}\nb = {b}\nprint(a {op} b)"
        ans = eval(f"{a} {op} {b}")
        fakes = [ans+1, ans-1, a+b if op!='+' else a*b, f"{a}{b}"]
        add_q("초급", "기본 연산", "다음 코드의 출력 결과는?", code, ans, fakes, f"파이썬의 {op} 연산자 결과입니다.")
    elif t == "string":
        s = random.choice(["apple", "banana", "python", "hello", "world"])
        code = f"s = '{s}'\nprint(len(s))"
        ans = len(s)
        fakes = [ans-1, ans+1, 0, len(s)*2]
        add_q("초급", "문자열 길이", "다음 코드의 출력 결과는?", code, ans, fakes, "len() 함수는 문자열의 길이를 반환합니다.")
    elif t == "list_idx":
        lst = [random.randint(1,10) for _ in range(4)]
        idx = random.randint(0, 3)
        code = f"arr = {lst}\nprint(arr[{idx}])"
        ans = lst[idx]
        fakes = [lst[(idx+1)%4], lst[idx]-1, idx, "Error"]
        add_q("초급", "리스트 인덱싱", "다음 코드의 출력 결과는?", code, ans, fakes, "파이썬 리스트는 0부터 인덱싱이 시작됩니다.")
    elif t == "bool":
        a = random.randint(1, 10)
        b = random.randint(1, 10)
        while a == b: b = random.randint(1, 10)
        op = random.choice(['>', '<', '==', '!='])
        code = f"print({a} {op} {b})"
        ans = eval(f"{a} {op} {b}")
        fakes = [not ans, "Error", a, b]
        add_q("초급", "비교 연산", "다음 코드의 출력 결과는?", code, ans, fakes, "비교 연산자의 결과는 불리언(True/False)입니다.")

def gen_beg_theory():
    t = random.choice([
        ("변수", "파이썬에서 변수를 선언할 때 올바른 방법은?", "", "x = 10", ["int x = 10", "var x = 10", "10 = x", "let x = 10"], "파이썬은 동적 타이핑을 지원하므로 '변수명 = 값' 형태로 선언합니다."),
        ("자료형", "다음 중 파이썬의 기본 자료형이 아닌 것은?", "", "double", ["int", "float", "str", "bool"], "파이썬에서 실수는 float이며 double이라는 키워드는 사용하지 않습니다."),
        ("주석", "파이썬에서 한 줄 주석을 작성할 때 사용하는 기호는?", "", "#", ["//", "/*", "<!--", "--"], "파이썬의 한 줄 주석은 # 기호를 사용합니다.")
    ])
    add_q("초급", t[0], t[1], t[2], t[3], t[4], t[5])

# === INTERMEDIATE (중급) ===
def gen_int_code():
    t = random.choice(["slice", "dict", "loop", "func"])
    if t == "slice":
        lst = [random.randint(1,10) for _ in range(5)]
        code = f"arr = {lst}\nprint(arr[1:4])"
        ans = str(lst[1:4])
        fakes = [str(lst[0:3]), str(lst[1:5]), str(lst[2:4]), "Error"]
        add_q("중급", "리스트 슬라이싱", "다음 코드의 출력 결과는?", code, ans, fakes, "[시작:끝] 슬라이싱에서 끝 인덱스는 포함되지 않습니다.")
    elif t == "dict":
        k1, k2 = random.sample(["a", "b", "c", "d"], 2)
        v1, v2 = random.randint(1,5), random.randint(6,10)
        code = f"d = {{'{k1}': {v1}, '{k2}': {v2}}}\nprint(d.get('{k1}', 0))"
        ans = v1
        fakes = [v2, 0, "Error", "None"]
        add_q("중급", "딕셔너리", "다음 코드의 출력 결과는?", code, ans, fakes, "get() 메서드는 키가 존재하면 해당 값을 반환합니다.")
    elif t == "loop":
        n = random.randint(3, 6)
        code = f"s = 0\nfor i in range({n}):\n    s += i\nprint(s)"
        ans = sum(range(n))
        fakes = [ans+n, ans-n+1 if ans-n+1>0 else 0, sum(range(n+1)), "Error"]
        add_q("중급", "반복문", "다음 코드의 출력 결과는?", code, ans, fakes, f"range({n})은 0부터 {n-1}까지 반복합니다.")
    elif t == "func":
        a = random.randint(2, 5)
        b = random.randint(2, 5)
        code = f"def add(x, y=1):\n    return x * y\nprint(add({a}, {b}))"
        ans = a * b
        fakes = [a * 1, a + b, b, "Error"]
        add_q("중급", "함수", "다음 코드의 출력 결과는?", code, ans, fakes, "기본값이 지정된 매개변수라도 값을 명시적으로 전달하면 그 값이 사용됩니다.")

def gen_int_theory():
    t = random.choice([
        ("반복문", "while 문과 for 문의 설명으로 틀린 것은?", "", "for 문은 무한 루프를 만들 수 없다.", ["while 문은 조건이 참인 동안 반복한다.", "break를 사용해 탈출할 수 있다.", "continue를 사용해 다음 반복으로 넘어갈 수 있다.", "for 문은 시퀀스 객체를 순회한다."], "for문도 반복 가능한 무한 제너레이터를 사용하면 무한 루프를 구현할 수 있습니다."),
        ("함수", "여러 값을 한 번에 반환(return)할 때 기본적으로 어떤 자료형으로 묶여 반환되는가?", "", "튜플(Tuple)", ["리스트(List)", "딕셔너리(Dictionary)", "세트(Set)", "문자열(String)"], "여러 값을 콤마로 구분하여 반환하면 자동으로 튜플로 패킹됩니다."),
        ("모듈", "외부 모듈을 불러올 때 사용하는 파이썬 키워드는?", "", "import", ["include", "require", "using", "load"], "파이썬에서는 import 키워드를 사용해 모듈을 가져옵니다.")
    ])
    add_q("중급", t[0], t[1], t[2], t[3], t[4], t[5])

# === ADVANCED (고급) ===
def gen_adv_code():
    t = random.choice(["list_comp", "lambda", "try", "set"])
    if t == "list_comp":
        n = random.randint(3, 5)
        code = f"lst = [x*2 for x in range({n}) if x % 2 == 0]\nprint(lst)"
        ans = str([x*2 for x in range(n) if x % 2 == 0])
        fakes = [str([x for x in range(n) if x % 2 == 0]), str([x*2 for x in range(n)]), str([x*2 for x in range(1, n+1)]), "Error"]
        add_q("고급", "리스트 컴프리헨션", "다음 코드의 출력 결과는?", code, ans, fakes, "if 조건식을 만족하는 요소만 포함되어 변환됩니다.")
    elif t == "lambda":
        m = random.randint(2, 4)
        code = f"func = lambda x: x ** {m}\nprint(func(2))"
        ans = 2 ** m
        fakes = [2 * m, m ** 2, 2, "Error"]
        add_q("고급", "람다 함수", "다음 코드의 출력 결과는?", code, ans, fakes, "lambda는 익명 함수를 생성하며 x를 인자로 받아 연산 결과를 반환합니다.")
    elif t == "try":
        code = "try:\n    10 / 0\nexcept ZeroDivisionError:\n    print('A')\nexcept:\n    print('B')\nfinally:\n    print('C')"
        ans = "A\nC (두 줄 출력)"
        fakes = ["A", "B", "B\nC", "Error"]
        add_q("고급", "예외 처리", "다음 코드가 실행되었을 때 출력되는 값은?", code, ans, fakes, "ZeroDivisionError가 발생하여 A가 출력되고, finally 블록은 무조건 실행되어 C가 출력됩니다.")
    elif t == "set":
        a1,a2,a3 = random.sample([1,2,3,4,5], 3)
        b1,b2,b3 = random.sample([3,4,5,6,7], 3)
        code = f"s1 = {{{a1}, {a2}, {a3}}}\ns2 = {{{b1}, {b2}, {b3}}}\nprint(list(s1 & s2))"
        ans = str(sorted(list({a1,a2,a3} & {b1,b2,b3})))
        fakes = [str(sorted(list({a1,a2,a3} | {b1,b2,b3}))), "[]", "Error", str(sorted(list({a1,a2,a3})))]
        add_q("고급", "세트 연산", "다음 코드의 출력 결과를 정렬한 리스트로 보면?", code, ans, fakes, "& 연산자는 두 세트의 교집합을 반환합니다.")

def gen_adv_theory():
    t = random.choice([
        ("클래스", "클래스 내부에 정의되어 객체 자신을 참조하는 첫 번째 매개변수의 관례적인 이름은?", "", "self", ["this", "cls", "object", "me"], "파이썬에서는 인스턴스 메서드의 첫 번째 인자로 self를 사용하는 것이 관례입니다."),
        ("예외처리", "사용자가 직접 예외를 발생시키고자 할 때 사용하는 키워드는?", "", "raise", ["throw", "catch", "except", "error"], "파이썬에서는 raise 키워드를 사용하여 의도적으로 예외를 발생시킵니다."),
        ("제너레이터", "제너레이터 함수에서 값을 반환하고 실행 상태를 유지하기 위해 사용하는 키워드는?", "", "yield", ["return", "emit", "give", "send"], "yield 키워드는 값을 반환한 뒤 함수의 실행 상태를 저장하여 나중에 재개할 수 있게 합니다.")
    ])
    add_q("고급", t[0], t[1], t[2], t[3], t[4], t[5])

# === EXPERT (최상) ===
def gen_exp_code():
    t = random.choice(["decorator", "closure", "inheritance", "generator"])
    if t == "decorator":
        m = random.randint(2, 5)
        v = random.randint(3, 7)
        code = f"def deco(f):\n    def wrap():\n        return f() * {m}\n    return wrap\n\n@deco\ndef num():\n    return {v}\nprint(num())"
        ans = v * m
        fakes = [v, m, v+m, "Error"]
        add_q("최상", "데코레이터", "다음 코드의 출력 결과는?", code, ans, fakes, "데코레이터 함수에 의해 원래 반환값에 특정 값을 곱한 값이 반환됩니다.")
    elif t == "closure":
        x = random.randint(5,15)
        y = random.randint(2,8)
        code = f"def outer(x):\n    def inner(y):\n        return x + y\n    return inner\nf = outer({x})\nprint(f({y}))"
        ans = x + y
        fakes = [x, y, x*y, "Error"]
        add_q("최상", "클로저", "다음 코드의 출력 결과는?", code, ans, fakes, f"외부 함수의 변수(x={x})를 내부 함수가 기억하는 클로저 특성이 활용됩니다.")
    elif t == "inheritance":
        code = "class A:\n    def say(self): return 'A'\nclass B(A):\n    def say(self): return super().say() + 'B'\nprint(B().say())"
        ans = "AB"
        fakes = ["B", "A", "BA", "Error"]
        add_q("최상", "클래스 상속", "다음 코드의 출력 결과는?", code, ans, fakes, "super()를 통해 부모 클래스의 메서드를 먼저 호출한 후 문자열을 더합니다.")
    elif t == "generator":
        n = random.randint(3,5)
        code = f"def gen():\n    for i in range({n}):\n        yield i\ng = gen()\nnext(g)\nprint(next(g))"
        ans = 1
        fakes = [0, 2, n, "Error"]
        add_q("최상", "제너레이터", "다음 코드의 출력 결과는?", code, ans, fakes, "next()를 처음 호출하면 0, 두 번째 호출하면 1이 반환됩니다.")

def gen_exp_theory():
    t = random.choice([
        ("메타클래스", "파이썬에서 클래스 자체를 생성하는 클래스, 즉 클래스의 팩토리를 의미하는 용어는?", "", "메타클래스(Metaclass)", ["슈퍼클래스", "베이스클래스", "추상클래스", "서브클래스"], "클래스가 객체를 생성하듯, 메타클래스는 클래스 자체를 생성합니다."),
        ("특수 메서드", "객체를 문자열로 표현할 때, 개발자 디버깅용 공식 문자열 표현을 반환하는 스페셜 메서드는?", "", "__repr__", ["__str__", "__format__", "__doc__", "__init__"], "__repr__은 객체를 재생성할 수 있는 공식적인 문자열 표현을 제공하는 목적이 강합니다."),
        ("GIL", "CPython에서 여러 스레드가 파이썬 바이트코드를 동시에 실행하지 못하도록 하는 뮤텍스는?", "", "GIL", ["GC", "JIT", "MRO", "JIT 컴파일러"], "GIL로 인해 CPython은 멀티코어 환경에서도 CPU 바운드 작업을 완벽히 병렬로 처리하는 데 한계가 있습니다.")
    ])
    add_q("최상", t[0], t[1], t[2], t[3], t[4], t[5])

# Generate
random.seed(123)
target_per_diff = 400

for i in range(target_per_diff):
    if random.random() < 0.8: gen_beg_code()
    else: gen_beg_theory()
    if random.random() < 0.8: gen_int_code()
    else: gen_int_theory()
    if random.random() < 0.8: gen_adv_code()
    else: gen_adv_theory()
    if random.random() < 0.8: gen_exp_code()
    else: gen_exp_theory()

# Save
with open('data/questions.json', 'w', encoding='utf-8') as f:
    json.dump(questions, f, ensure_ascii=False, indent=2)

print(f"Generated {len(questions)} high-quality mixed questions.")
