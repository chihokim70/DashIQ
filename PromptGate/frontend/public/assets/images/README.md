# 이미지 관리 시스템

## 📁 디렉토리 구조

```
public/assets/images/
├── logos/           # 로고 이미지
│   ├── aigov-logo.png
│   ├── favicon.ico
│   ├── favicon-16x16.png
│   ├── favicon-32x32.png
│   ├── apple-touch-icon.png
│   ├── android-chrome-192x192.png
│   └── android-chrome-512x512.png
├── icons/           # 아이콘 이미지
│   ├── chat-icon.png
│   ├── settings-icon.png
│   ├── dashboard-icon.png
│   └── security-icon.png
├── ui/              # UI 요소 이미지
│   ├── button-bg.png
│   ├── card-bg.png
│   └── header-bg.png
└── backgrounds/     # 배경 이미지
    ├── main-bg.jpg
    ├── login-bg.jpg
    └── dashboard-bg.jpg
```

## 🛠️ 사용 방법

### 1. 이미지 유틸리티 함수 사용

```typescript
import { 
  getLogoPath, 
  getIconPath, 
  getUIPath, 
  getBackgroundPath,
  DEFAULT_IMAGES 
} from '@/lib/image-utils';

// 로고 이미지 경로 생성
const logoPath = getLogoPath('aigov-logo', '192x192');

// 아이콘 이미지 경로 생성
const iconPath = getIconPath('chat-icon', '32x32');

// 기본 이미지 사용
const defaultLogo = DEFAULT_IMAGES.logo;
```

### 2. 이미지 컴포넌트 사용

```typescript
import { 
  LogoImage, 
  IconImage, 
  UIImage, 
  BackgroundImage,
  OptimizedImage 
} from '@/components/ui/image';

// 로고 이미지 컴포넌트
<LogoImage
  filename="aigov-logo"
  size="192x192"
  alt="AiGov 로고"
  width={192}
  height={192}
  className="mx-auto"
/>

// 아이콘 이미지 컴포넌트
<IconImage
  filename="chat-icon"
  size="32x32"
  alt="채팅 아이콘"
  width={32}
  height={32}
/>

// UI 이미지 컴포넌트
<UIImage
  filename="button-bg"
  alt="버튼 배경"
  width={200}
  height={50}
/>

// 배경 이미지 컴포넌트
<BackgroundImage
  filename="main-bg"
  alt="메인 배경"
  width={1920}
  height={1080}
  className="absolute inset-0"
/>

// 최적화된 이미지 컴포넌트
<OptimizedImage
  category="logos"
  filename="aigov-logo"
  size="512x512"
  alt="AiGov 로고"
  width={512}
  height={512}
  optimization={{
    quality: 90,
    format: 'webp'
  }}
/>
```

### 3. 이미지 갤러리 사용

```typescript
import { ImageGallery } from '@/components/ui/image';

const images = [
  {
    src: '/assets/images/ui/screenshot1.png',
    alt: '스크린샷 1',
    caption: '메인 화면'
  },
  {
    src: '/assets/images/ui/screenshot2.png',
    alt: '스크린샷 2',
    caption: '설정 화면'
  }
];

<ImageGallery
  images={images}
  columns={2}
  className="mt-8"
/>
```

## 📋 이미지 규칙

### 1. 파일명 규칙
- 소문자와 하이픈(-) 사용
- 의미있는 이름 사용
- 크기별 접미사 사용 (예: `logo-192x192.png`)

### 2. 이미지 크기
- **16x16**: 파비콘
- **32x32**: 작은 아이콘
- **192x192**: 중간 크기 로고
- **512x512**: 큰 로고
- **original**: 원본 크기

### 3. 이미지 포맷
- **PNG**: 투명 배경이 필요한 이미지
- **JPG**: 사진 및 배경 이미지
- **SVG**: 벡터 아이콘
- **WebP**: 최적화된 이미지 (권장)

### 4. 이미지 최적화
- Next.js Image 컴포넌트 사용
- 적절한 quality 설정 (75-90)
- lazy loading 활용
- 반응형 이미지 사용

## 🔧 개발 도구

### 1. 이미지 검증
```typescript
import { validateImageFile } from '@/lib/image-utils';

const isValid = validateImageFile('logo.png', ['png', 'jpg', 'svg']);
```

### 2. 이미지 메타데이터
```typescript
import { createImageMetadata } from '@/lib/image-utils';

const metadata = createImageMetadata({
  filename: 'aigov-logo.png',
  category: 'logos',
  size: '192x192',
  alt: 'AiGov 로고',
  title: 'AiGov Enterprise Logo',
  description: 'AiGov 기업용 로고 이미지'
});
```

### 3. 이미지 플레이스홀더
```typescript
import { ImagePlaceholder } from '@/components/ui/image';

<ImagePlaceholder
  width={300}
  height={200}
  className="rounded-lg"
>
  <p>이미지 로딩 중...</p>
</ImagePlaceholder>
```

## 📊 성능 최적화

### 1. 이미지 압축
- PNG: TinyPNG 또는 ImageOptim 사용
- JPG: JPEGmini 또는 Kraken.io 사용
- SVG: SVGO 사용

### 2. Next.js 최적화
- `priority` 속성으로 중요한 이미지 우선 로드
- `placeholder="blur"`로 로딩 경험 개선
- `sizes` 속성으로 반응형 이미지 최적화

### 3. CDN 사용
- 이미지 CDN 서비스 활용
- WebP 포맷 자동 변환
- 지리적 분산 캐싱

## 🚀 향후 계획

### 1. 이미지 업로드 기능
- 관리자 대시보드에서 이미지 업로드
- 이미지 자동 최적화
- 이미지 메타데이터 관리

### 2. 이미지 편집 기능
- 기본적인 이미지 편집 도구
- 크롭 및 리사이즈 기능
- 필터 및 효과 적용

### 3. 이미지 분석
- 이미지 사용 통계
- 성능 모니터링
- 최적화 권장사항

---

**참고**: 이 이미지 관리 시스템은 @AiGovDevDesign.md 설계서 기준으로 구현되었습니다.


