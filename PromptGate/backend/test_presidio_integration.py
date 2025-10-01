#!/usr/bin/env python3
"""
Presidio PII 탐지기 통합 테스트
"""

import asyncio
import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.pii_detector import get_pii_detector, PIIType, PIIConfidence

async def test_presidio_integration():
    """Presidio 통합 테스트"""
    print("🔍 Presidio PII 탐지기 통합 테스트 시작")
    
    try:
        # PII 탐지기 인스턴스 가져오기
        detector = await get_pii_detector()
        
        # 스캐너 상태 확인
        status = detector.get_scanner_status()
        print(f"📊 스캐너 상태: {status}")
        
        # 테스트 텍스트
        test_texts = [
            "안녕하세요, 저는 홍길동입니다. 제 전화번호는 010-1234-5678이고, 이메일은 hong@example.com입니다.",
            "주민등록번호는 800101-1234567이고, 신용카드 번호는 1234-5678-9012-3456입니다.",
            "서울시 강남구 테헤란로 123에 살고 있습니다. 생년월일은 1980-01-01입니다.",
            "My name is John Doe and my email is john.doe@company.com. Phone: +1-555-123-4567"
        ]
        
        for i, text in enumerate(test_texts, 1):
            print(f"\n📝 테스트 {i}: {text}")
            
            # PII 스캔
            result = await detector.scan_text(text, f"test_{i}")
            
            print(f"   🔍 PII 탐지 결과:")
            print(f"   - PII 발견: {result.has_pii}")
            print(f"   - 총 PII 수: {result.total_pii}")
            print(f"   - 고신뢰도 PII: {result.high_confidence_pii}")
            print(f"   - 위험 점수: {result.risk_score:.2f}")
            print(f"   - 처리 시간: {result.processing_time:.3f}초")
            
            if result.pii_matches:
                print(f"   📋 탐지된 PII:")
                for match in result.pii_matches:
                    print(f"     - 타입: {match.pii_type.value}")
                    print(f"     - 신뢰도: {match.confidence.value}")
                    print(f"     - 텍스트: {match.matched_text}")
                    print(f"     - 스캐너: {match.metadata.get('scanner', 'unknown')}")
                    print(f"     - 위치: {match.start_pos}-{match.end_pos}")
                    print()
            
            # 익명화 테스트
            if result.pii_matches:
                anonymized = detector.anonymize_text(text, result.pii_matches)
                print(f"   🔒 익명화된 텍스트: {anonymized}")
        
        print("\n✅ Presidio PII 탐지기 통합 테스트 완료")
        
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_presidio_integration())
