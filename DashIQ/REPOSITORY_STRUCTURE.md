# DashIQ 리포지토리 구조

## 📋 개요
DashIQ 관리자 대시보드는 두 개의 리포지토리로 관리됩니다:

## 🎨 **Aisecuritydashboard** (피그마 디자인 소스)
- **목적**: 피그마에서 디자인한 순수 디자인 소스코드
- **URL**: https://github.com/chihokim70/Aisecuritydashboard
- **사용법**: 디자인 참조, 새로운 컴포넌트 가져오기
- **업데이트**: 피그마 디자인 변경시에만 업데이트

## 🚀 **DashIQ** (개발 버전)
- **목적**: 실제 개발 및 커스터마이징된 버전
- **URL**: https://github.com/chihokim70/DashIQ
- **사용법**: 실제 개발, 기능 추가, 버그 수정
- **업데이트**: 지속적인 개발 및 개선

## 🔄 **워크플로우**

### 1. 피그마 디자인 업데이트시
```bash
# Aisecuritydashboard에 새 디자인 푸시
cd /path/to/figma-export
git push origin main
```

### 2. 개발시 디자인 참조
```bash
# DashIQ에서 최신 디자인 가져오기
cd /home/krase/AiGov/DashIQ
git fetch aisecuritydashboard
git merge aisecuritydashboard/main  # 필요시
```

### 3. 개발 결과 저장
```bash
# DashIQ 리포지토리에 개발 결과 푸시
cd /home/krase/AiGov/DashIQ
git add .
git commit -m "feat: 새로운 기능 구현"
git push dashiq main
```

## 📁 **Remote 설정**
```bash
# 현재 DashIQ 디렉토리의 remote 설정
origin               git@github.com:chihokim70/AiGov.git (전체 프로젝트)
aisecuritydashboard  git@github.com:chihokim70/Aisecuritydashboard.git (피그마 디자인)
dashiq               git@github.com:chihokim70/DashIQ.git (개발 버전)
```

## 🎯 **사용 사례**

### 피그마 디자인 반영
1. 피그마에서 새로운 컴포넌트 디자인
2. Aisecuritydashboard에 코드 내보내기 및 푸시
3. DashIQ에서 aisecuritydashboard에서 변경사항 가져오기
4. 개발 요구사항에 맞게 커스터마이징
5. DashIQ 리포지토리에 결과 푸시

### 기능 개발
1. DashIQ에서 새로운 기능 개발
2. 기존 디자인 컴포넌트 활용
3. 비즈니스 로직 및 API 연동
4. 테스트 및 최적화
5. DashIQ 리포지토리에 푸시

---

**생성일**: 2025년 10월 31일
**작성자**: AI Assistant
**버전**: 1.0.0