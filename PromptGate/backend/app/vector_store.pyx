from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, SearchParams
from sentence_transformers import SentenceTransformer
from app.config import get_settings

# 환경 설정 불러오기
settings = get_settings()

# Qdrant 클라이언트 초기화
client = QdrantClient(host=settings.qdrant_host, port=settings.qdrant_port)

# SentenceTransformer 모델 (한국어 최적화 모델)
model = SentenceTransformer('jhgan/ko-sroberta-multitask')  # 최초 실행 시 다운로드됨

# 벡터 유사도 필터 함수
def check_similarity(prompt: str) -> bool:
    try:
        # 실제 프롬프트 임베딩
        vector = model.encode(prompt).tolist()

        # Qdrant 벡터 유사도 검색
        results = client.search(
            collection_name="blocked-prompts",
            query_vector=vector,
            limit=1,
            score_threshold=0.65,  # 유사도 임계값
            search_params=SearchParams(hnsw_ef=64, exact=False)
        )

        if results:
            print(f"[유사도 점수] {results[0].score}")

        return len(results) > 0  # 결과가 있으면 유사하다고 판단

    except Exception as e:
        print(f"[Qdrant Search Error] {e}")
        return False
