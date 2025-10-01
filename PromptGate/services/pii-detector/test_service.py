#!/usr/bin/env python3
"""
PII Detection Service 테스트 스크립트
마이크로서비스로 분리된 Presidio PII Detection Service 테스트
"""

import asyncio
import httpx
import json
from datetime import datetime

async def test_pii_detection_service():
    """PII Detection Service 테스트"""
    base_url = "http://localhost:8082"
    
    print("🔍 PII Detection Service 테스트 시작")
    print(f"📍 서비스 URL: {base_url}")
    
    # 테스트 텍스트들
    test_cases = [
        {
            "name": "한국어 PII 테스트",
            "text": "안녕하세요, 저는 홍길동입니다. 제 전화번호는 010-1234-5678이고, 이메일은 hong@example.com입니다. 주민등록번호는 800101-1234567입니다.",
            "context": "고객 상담",
            "language": "ko"
        },
        {
            "name": "영어 PII 테스트",
            "text": "My name is John Doe and my email is john.doe@company.com. Phone: +1-555-123-4567. SSN: 123-45-6789",
            "context": "customer support",
            "language": "en"
        },
        {
            "name": "신용카드 정보 테스트",
            "text": "결제 정보: 카드번호 1234-5678-9012-3456, 만료일 12/25, CVV 123",
            "context": "결제 처리",
            "language": "ko"
        },
        {
            "name": "주소 정보 테스트",
            "text": "배송 주소: 서울시 강남구 테헤란로 123, 우편번호 06292",
            "context": "배송 관리",
            "language": "ko"
        }
    ]
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # 1. 헬스체크 테스트
        print("\n1️⃣ 헬스체크 테스트")
        try:
            response = await client.get(f"{base_url}/health")
            if response.status_code == 200:
                health_data = response.json()
                print(f"   ✅ 헬스체크 성공: {health_data}")
            else:
                print(f"   ❌ 헬스체크 실패: {response.status_code}")
                return
        except Exception as e:
            print(f"   ❌ 헬스체크 오류: {e}")
            return
        
        # 2. 서비스 상태 확인
        print("\n2️⃣ 서비스 상태 확인")
        try:
            response = await client.get(f"{base_url}/status")
            if response.status_code == 200:
                status_data = response.json()
                print(f"   ✅ 서비스 상태: {status_data['status']}")
                print(f"   📊 PII 탐지기 상태: {status_data['pii_detector_status']}")
            else:
                print(f"   ❌ 상태 확인 실패: {response.status_code}")
        except Exception as e:
            print(f"   ❌ 상태 확인 오류: {e}")
        
        # 3. PII 탐지 테스트
        print("\n3️⃣ PII 탐지 테스트")
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n   📝 테스트 {i}: {test_case['name']}")
            print(f"   📄 텍스트: {test_case['text'][:50]}...")
            
            try:
                payload = {
                    "text": test_case["text"],
                    "context": test_case["context"],
                    "language": test_case["language"]
                }
                
                response = await client.post(f"{base_url}/detect", json=payload)
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"   ✅ 탐지 성공:")
                    print(f"      - PII 발견: {result['has_pii']}")
                    print(f"      - 총 PII 수: {result['total_pii']}")
                    print(f"      - 고신뢰도 PII: {result['high_confidence_pii']}")
                    print(f"      - 위험 점수: {result['risk_score']:.2f}")
                    print(f"      - 처리 시간: {result['processing_time']:.3f}초")
                    
                    if result['pii_matches']:
                        print(f"      📋 탐지된 PII:")
                        for match in result['pii_matches']:
                            print(f"         - {match['pii_type']}: {match['matched_text']} (신뢰도: {match['confidence']})")
                    
                    # 4. 익명화 테스트
                    if result['pii_matches']:
                        print(f"   🔒 익명화 테스트:")
                        
                        anonymize_payload = {
                            "text": test_case["text"],
                            "pii_matches": result['pii_matches'],
                            "anonymization_method": "mask"
                        }
                        
                        anonymize_response = await client.post(f"{base_url}/anonymize", json=anonymize_payload)
                        
                        if anonymize_response.status_code == 200:
                            anonymize_result = anonymize_response.json()
                            print(f"      ✅ 익명화 성공:")
                            print(f"         - 원본: {anonymize_result['original_text'][:50]}...")
                            print(f"         - 익명화: {anonymize_result['anonymized_text'][:50]}...")
                            print(f"         - 익명화 수: {anonymize_result['anonymized_count']}")
                        else:
                            print(f"      ❌ 익명화 실패: {anonymize_response.status_code}")
                
                else:
                    print(f"   ❌ 탐지 실패: {response.status_code}")
                    print(f"   📄 응답: {response.text}")
                    
            except Exception as e:
                print(f"   ❌ 테스트 오류: {e}")
        
        # 5. 통합 테스트 (탐지 + 익명화)
        print("\n5️⃣ 통합 테스트 (탐지 + 익명화)")
        test_text = "고객 정보: 홍길동, 010-1234-5678, hong@example.com, 주민등록번호 800101-1234567"
        
        try:
            payload = {
                "text": test_text,
                "context": "통합 테스트",
                "language": "ko"
            }
            
            response = await client.post(f"{base_url}/detect-and-anonymize", json=payload)
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ 통합 테스트 성공:")
                print(f"      - 탐지된 PII: {result['detection']['total_pii']}개")
                print(f"      - 위험 점수: {result['detection']['risk_score']:.2f}")
                print(f"      - 익명화된 텍스트: {result['anonymization']['anonymized_text']}")
                print(f"      - 총 처리 시간: {result['processing_time']:.3f}초")
            else:
                print(f"   ❌ 통합 테스트 실패: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ 통합 테스트 오류: {e}")
    
    print("\n🎉 PII Detection Service 테스트 완료")

if __name__ == "__main__":
    asyncio.run(test_pii_detection_service())
