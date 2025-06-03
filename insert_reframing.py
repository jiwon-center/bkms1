import pandas as pd
from sentence_transformers import SentenceTransformer
import psycopg2
from psycopg2.extras import execute_batch

# 1. 데이터 불러오기
df = pd.read_csv('./archive/reframing_dataset.csv')

# 2. 임베딩 모델 로드
model = SentenceTransformer('all-MiniLM-L6-v2')

# 3. situation + thought 합치기 (예: [situation] [thought])
def make_concat(row):
    return str(row['situation']) + ' ' + str(row['thought'])

df['combined'] = df.apply(make_concat, axis=1)

# 4. 임베딩 생성 (합쳐진 텍스트로)
df['comb_embedding'] = df['combined'].apply(lambda x: model.encode(x).tolist())

# 5. Postgres 연결
conn = psycopg2.connect(
    host="localhost",
    database="cognitive_distortion",
    user="kim-bogeun",
    password="",  # 비밀번호 있으면 입력
    port=5432
)
cur = conn.cursor()

# 6. 테이블 생성 (이미 있다면 생략 가능)
cur.execute("""
CREATE TABLE IF NOT EXISTS reframing_dataset (
  id SERIAL PRIMARY KEY,
  situation TEXT,
  thought TEXT,
  reframe TEXT,
  thinking_traps_addressed TEXT,
  embedding VECTOR(384)
);
""")
conn.commit()

# 7. 데이터 일괄 적재 (필요하면 기존 데이터 삭제)
cur.execute("TRUNCATE reframing_dataset;")
records = [
    (
        row['situation'],
        row['thought'],
        row['reframe'],
        row['thinking_traps_addressed'],
        row['comb_embedding']
    )
    for _, row in df.iterrows()
]
execute_batch(
    cur,
    "INSERT INTO reframing_dataset (situation, thought, reframe, thinking_traps_addressed, embedding) VALUES (%s, %s, %s, %s, %s)",
    records
)
conn.commit()
cur.close()
conn.close()