import pandas as pd
from sentence_transformers import SentenceTransformer
import psycopg2
from psycopg2.extras import execute_batch

# 1. 엑셀 파일 로딩
df = pd.read_excel('./archive/cognitive-distortion-data2.xlsx')

# 2. 임베딩 모델 선택 및 로드
MODEL_NAME = 'all-MiniLM-L6-v2'   # 384차원, 빠르고 효율적
model = SentenceTransformer(MODEL_NAME)

# 3. 예시문(example) 임베딩 생성
df['embedding'] = df['Example'].apply(lambda x: model.encode(str(x)).tolist())

# 4. Postgres 연결 (환경에 맞게 정보 입력)
conn = psycopg2.connect(
    host="localhost",
    database="cognitive_distortion",
    user="kim-bogeun",
    password="",     # 만약 비밀번호가 설정되어 있다면 입력, 아니면 빈칸 유지
    port=5432
)

cur = conn.cursor()

# 5. 테이블 생성 (최초 1회만 실행)
cur.execute("""
CREATE TABLE IF NOT EXISTS thinking_traps (
  id SERIAL PRIMARY KEY,
  trap_name TEXT NOT NULL,
  definition TEXT,
  example TEXT,
  tips TEXT,
  embedding VECTOR(384)
);
""")
conn.commit()

# 6. 데이터 일괄 적재
records = [
    (
        row['Thinking Traps'],
        row['Definition'],
        row['Example'],
        row['Tips to Overcome'],
        row['embedding']
    )
    for _, row in df.iterrows()
]
execute_batch(
    cur,
    "INSERT INTO thinking_traps (trap_name, definition, example, tips, embedding) VALUES (%s, %s, %s, %s, %s)",
    records
)
conn.commit()
cur.close()
conn.close()