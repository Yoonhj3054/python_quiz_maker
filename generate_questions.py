import json
import random
import os

topics = ["변수", "함수", "딕셔너리", "튜플", "넘파이", "판다스", "제어문", "랜덤함수", "클래스"]
difficulties = ["초급", "중급", "고급", "최상"]

questions = []
current_id = 1

# Templates
templates_by_diff = {
    "초급": [
        "다음 중 파이썬의 {topic}에 대한 설명으로 알맞은 것은?",
        "파이썬에서 {topic}을(를) 올바르게 사용하는 방법은?",
        "{topic}의 주요 특징이 아닌 것은 무엇입니까?",
        "파이썬 {topic}에서 주로 발생하는 기초적인 에러 원인은?"
    ],
    "중급": [
        "다음 코드를 실행했을 때 {topic}와 관련된 출력 결과로 알맞은 것은?\n\n{code}",
        "{topic}를 활용하여 데이터를 처리할 때 가장 효율적인 방법은?",
        "파이썬 {topic} 내부에서 특정 값을 참조할 때 발생할 수 있는 예외는?",
        "다음 중 {topic}의 활용법으로 잘못 구현된 로직은?"
    ],
    "고급": [
        "{topic}의 메모리 할당 및 가비지 컬렉션 동작 원리와 관련된 설명 중 올바른 것은?",
        "다음과 같이 복잡한 {topic} 코드가 주어졌을 때, 최종적으로 반환되는 값은?\n\n{code}",
        "멀티스레딩 환경에서 {topic}를 사용할 때 발생할 수 있는 GIL(Global Interpreter Lock)의 영향은?",
        "대규모 데이터셋을 {topic}로 처리할 때 시간 복잡도(O)를 최소화하는 최적화 기법은?"
    ],
    "최상": [
        "Python C-API 레벨에서 {topic} 객체의 메모리 동작 방식에 대한 상세 설명으로 가장 적절한 것은?",
        "{topic} 메타클래스(Metaclass)를 활용하여 프레임워크 수준의 아키텍처를 설계할 때, 생성 라이프사이클의 특징은?",
        "PEP 8 및 CPython 바이트코드 관점에서 다음 {topic} 코드의 dis() 디스어셈블리 결과 패턴으로 예측되는 것은?\n\n{code}",
        "고도로 분산된 런타임 환경에서 {topic} 객체의 상태를 동기화하기 위한 데드락(Deadlock) 회피 기법은?"
    ]
}

options_pool = {
    "초급": [
        "동적 타이핑을 지원하여 타입 선언이 필요 없다.", "인덱스는 0부터 시작한다.", 
        "들여쓰기를 통해 블록을 구분한다.", "불변(Immutable) 객체로 한 번 생성되면 변경할 수 없다.",
        "키-값 쌍으로 구성되어 해시 테이블 기반으로 동작한다."
    ],
    "중급": [
        "리스트 컴프리헨션을 사용하는 것이 append()보다 빠르다.", "얕은 복사(Shallow Copy)로 인해 원본 객체가 변경될 위험이 있다.", 
        "try-except 블록을 통해 KeyError 예외를 우아하게 처리한다.", "제너레이터(Generator)를 통해 메모리 지연 평가(Lazy Evaluation)를 적용한다.",
        "lambda 익명 함수를 활용하여 콜백 구조를 단순화한다."
    ],
    "고급": [
        "참조 카운팅(Reference Counting)과 세대별 가비지 컬렉터(Generational GC)가 복합적으로 작동한다.", 
        "GIL로 인해 멀티스레드보다 멀티프로세싱(Multiprocessing) 모듈을 사용하는 것이 병렬 처리에 유리하다.", 
        "__slots__ 속성을 정의하여 각 인스턴스의 딕셔너리 생성 오버헤드를 제거한다.", 
        "컨텍스트 매니저(Context Manager)를 통해 언매니지드 리소스의 누수를 방지한다.",
        "MRO(Method Resolution Order)는 C3 선형화 알고리즘을 따른다."
    ],
    "최상": [
        "PyObject 내부의 ob_refcnt를 직접 조작하는 C 확장 모듈을 작성하여 성능을 극대화한다.", 
        "AST(Abstract Syntax Tree) 파서를 구현하여 런타임에 동적으로 노드를 재배열하고 컴파일한다.", 
        "ctypes 또는 CFFI를 활용하여 C 표준 라이브러리의 포인터 주소를 직접 참조하여 메모리 뷰(memoryview)를 매핑한다.", 
        "GIL(Global Interpreter Lock)이 해제된 서브 인터프리터(Sub-interpreters)를 활용하여 완벽한 병렬 런타임을 구성한다.",
        "__prepare__ 메타클래스 훅을 오버라이딩하여 커스텀 네임스페이스 매핑(Custom Namespace Mapping)을 구현한다."
    ]
}

code_snippets = [
    "x = [1, 2, 3]\ny = x\ny.append(4)\nprint(x)",
    "def func(*args, **kwargs):\n    return sum(args) + kwargs.get('val', 0)",
    "import numpy as np\narr = np.array([[1, 2], [3, 4]])\nprint(arr[:, 1])",
    "import pandas as pd\ndf = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})\nprint(df.loc[0, 'B'])",
    "class Singleton:\n    _instance = None\n    def __new__(cls, *args, **kwargs):\n        if not cls._instance:\n            cls._instance = super().__new__(cls)\n        return cls._instance",
    "def decorator(f):\n    def wrapper(*a, **kw):\n        return f(*a, **kw) * 2\n    return wrapper",
    "import random\nrandom.seed(42)\nprint(random.randint(1, 10))"
]

def generate_questions():
    global current_id
    for diff in difficulties:
        for _ in range(400):
            topic = random.choice(topics)
            template = random.choice(templates_by_diff[diff])
            
            has_code = "{code}" in template
            if has_code:
                code = random.choice(code_snippets)
                question_text = template.replace("{topic}", topic).replace("{code}", code)
            else:
                question_text = template.replace("{topic}", topic)
                
            # Mix options to have enough variations
            pool = list(options_pool[diff]) + list(options_pool["초급"])
            random.shuffle(pool)
            
            opts = []
            for i in range(5):
                base_text = pool[i % len(pool)]
                opts.append(f"[{topic} 관련] {base_text} (variation-{random.randint(1000, 9999)})")
            
            correct_idx = random.randint(0, 4)
            opts[correct_idx] = f"[✅ 정답] {opts[correct_idx].replace('variation-', 'ans-')}"
            
            explanation = f"이 문제는 {diff} 난이도의 '{topic}' 관련 심화 문제입니다. 정답은 {correct_idx + 1}번입니다. 실제 서비스에서는 여기에 상세한 해설이 들어갑니다."
            
            q_obj = {
                "id": current_id,
                "difficulty": diff,
                "topic": topic,
                "question": question_text,
                "codeSnippet": code if has_code else None,
                "options": opts,
                "correctAnswer": correct_idx,
                "explanation": explanation
            }
            questions.append(q_obj)
            current_id += 1

generate_questions()

# Write to json file
os.makedirs('src/data', exist_ok=True)
with open('src/data/questions.json', 'w', encoding='utf-8') as f:
    json.dump(questions, f, ensure_ascii=False, indent=2)

print(f"Generated {len(questions)} questions successfully!")
