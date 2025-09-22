# app/policy_client.py

import psycopg2
from typing import List, Tuple
from app.config import get_settings

settings = get_settings()

def get_connection():
    """PostgreSQL 연결 객체 생성"""
    return psycopg2.connect(
        host=settings.db_host,
        port=settings.db_port,
        dbname=settings.db_name,
        user=settings.db_user,
        password=settings.db_password
    )


def get_block_keywords() -> List[str]:
    """차단 키워드 리스트 반환"""
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT keyword FROM blocked_keywords WHERE is_active = true;")
                results = cur.fetchall()
                return [row[0] for row in results]
    except Exception as e:
        print(f"[get_block_keywords] DB 오류: {e}")
        return []


def get_mask_keywords() -> List[Tuple[str, str]]:
    """마스킹 키워드와 치환값 리스트 반환"""
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT keyword, mask_value FROM masked_keywords WHERE is_active = true;")
                rows = cur.fetchall()
                print("[get_mask_keywords] 마스킹 키워드 반환값:", rows)
                return rows
    except Exception as e:
        print(f"[get_mask_keywords] DB 오류: {e}")
        return []
