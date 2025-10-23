/**
 * 이미지 관리 유틸리티 함수
 * 설계서 기준 이미지 저장 구조 관리
 */

// 이미지 경로 타입 정의
export type ImageCategory = 'logos' | 'icons' | 'ui' | 'backgrounds';

// 이미지 크기 타입 정의
export type ImageSize = '16x16' | '32x32' | '192x192' | '512x512' | 'original';

/**
 * 이미지 경로 생성 함수
 * @param category 이미지 카테고리
 * @param filename 파일명
 * @param size 이미지 크기 (선택사항)
 * @returns 완전한 이미지 경로
 */
export function getImagePath(
  category: ImageCategory,
  filename: string,
  size?: ImageSize
): string {
  const basePath = '/assets/images';
  const sizeSuffix = size && size !== 'original' ? `-${size}` : '';
  const extension = filename.includes('.') ? '' : '.png';
  
  return `${basePath}/${category}/${filename}${sizeSuffix}${extension}`;
}

/**
 * 로고 이미지 경로 생성
 * @param filename 로고 파일명
 * @param size 이미지 크기
 * @returns 로고 이미지 경로
 */
export function getLogoPath(filename: string, size?: ImageSize): string {
  return getImagePath('logos', filename, size);
}

/**
 * 아이콘 이미지 경로 생성
 * @param filename 아이콘 파일명
 * @param size 이미지 크기
 * @returns 아이콘 이미지 경로
 */
export function getIconPath(filename: string, size?: ImageSize): string {
  return getImagePath('icons', filename, size);
}

/**
 * UI 이미지 경로 생성
 * @param filename UI 이미지 파일명
 * @param size 이미지 크기
 * @returns UI 이미지 경로
 */
export function getUIPath(filename: string, size?: ImageSize): string {
  return getImagePath('ui', filename, size);
}

/**
 * 배경 이미지 경로 생성
 * @param filename 배경 이미지 파일명
 * @param size 이미지 크기
 * @returns 배경 이미지 경로
 */
export function getBackgroundPath(filename: string, size?: ImageSize): string {
  return getImagePath('backgrounds', filename, size);
}

/**
 * 이미지 최적화 옵션
 */
export interface ImageOptimizationOptions {
  width?: number;
  height?: number;
  quality?: number;
  format?: 'webp' | 'png' | 'jpg';
}

/**
 * 이미지 최적화 경로 생성 (Next.js Image 컴포넌트용)
 * @param src 이미지 소스 경로
 * @param options 최적화 옵션
 * @returns 최적화된 이미지 경로
 */
export function getOptimizedImagePath(
  src: string,
  options?: ImageOptimizationOptions
): string {
  // Next.js Image 컴포넌트는 자동으로 최적화를 처리하므로
  // 여기서는 기본 경로만 반환
  return src;
}

/**
 * 이미지 미리보기 URL 생성
 * @param category 이미지 카테고리
 * @param filename 파일명
 * @returns 미리보기 URL
 */
export function getPreviewUrl(category: ImageCategory, filename: string): string {
  return getImagePath(category, filename);
}

/**
 * 이미지 메타데이터 타입
 */
export interface ImageMetadata {
  filename: string;
  category: ImageCategory;
  size: ImageSize;
  alt: string;
  title?: string;
  description?: string;
}

/**
 * 이미지 메타데이터 생성
 * @param metadata 이미지 메타데이터
 * @returns 완전한 이미지 메타데이터
 */
export function createImageMetadata(metadata: Partial<ImageMetadata>): ImageMetadata {
  return {
    filename: metadata.filename || '',
    category: metadata.category || 'ui',
    size: metadata.size || 'original',
    alt: metadata.alt || '',
    title: metadata.title,
    description: metadata.description,
  };
}

/**
 * 이미지 파일 검증 함수
 * @param filename 파일명
 * @param allowedExtensions 허용된 확장자
 * @returns 유효한 파일명인지 여부
 */
export function validateImageFile(
  filename: string,
  allowedExtensions: string[] = ['png', 'jpg', 'jpeg', 'gif', 'svg', 'webp']
): boolean {
  const extension = filename.split('.').pop()?.toLowerCase();
  return extension ? allowedExtensions.includes(extension) : false;
}

/**
 * 이미지 크기별 경로 맵
 */
export const IMAGE_SIZE_MAP: Record<ImageSize, string> = {
  '16x16': '16x16',
  '32x32': '32x32',
  '192x192': '192x192',
  '512x512': '512x512',
  'original': 'original',
};

/**
 * 기본 이미지 경로들
 */
export const DEFAULT_IMAGES = {
  logo: getLogoPath('aigov-logo'),
  favicon: getLogoPath('favicon'),
  appleTouchIcon: getLogoPath('apple-touch-icon'),
  androidChrome192: getLogoPath('android-chrome-192x192'),
  androidChrome512: getLogoPath('android-chrome-512x512'),
} as const;


