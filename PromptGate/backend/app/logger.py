from loguru import logger
import sys
from elasticsearch import Elasticsearch
from app.config import get_settings

settings = get_settings()

# 콘솔 로그 기본 설정
logger.remove()
logger.add(sys.stdout, level="INFO", format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | <cyan>{message}</cyan>")

# Elasticsearch 클라이언트 및 로그 함수 정의
if settings.enable_es_logging:
    try:
        es = Elasticsearch(
            settings.elasticsearch_url,
            http_auth=(settings.elasticsearch_user, settings.elasticsearch_password),
            verify_certs=bool(settings.elastic_ca_cert_path),
            ca_certs=settings.elastic_ca_cert_path or None
        )
        logger.info("[Elasticsearch] 연결 성공")

        def log_to_elasticsearch(index: str, document: dict):
            try:
                es.index(index=index, document=document)
            except Exception as e:
                logger.error(f"[Elasticsearch] 로그 전송 실패: {str(e)}")

    except Exception as conn_err:
        logger.error(f"[Elasticsearch] 초기화 실패: {str(conn_err)}")

        def log_to_elasticsearch(index: str, document: dict):
            pass  # 연결 실패 시 비활성화

else:
    logger.info("[Elasticsearch] 로그 비활성화됨")

    def log_to_elasticsearch(index: str, document: dict):
        pass

def get_logger(name: str):
    return logger.bind(service=name)
