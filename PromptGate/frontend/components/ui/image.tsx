/**
 * 이미지 컴포넌트
 * 설계서 기준 이미지 관리 시스템
 */

import React from 'react';
import Image from 'next/image';
import { 
  getImagePath, 
  getLogoPath, 
  getIconPath, 
  getUIPath, 
  getBackgroundPath,
  ImageCategory,
  ImageSize,
  ImageOptimizationOptions,
  DEFAULT_IMAGES
} from '@/lib/image-utils';

/**
 * 기본 이미지 컴포넌트 Props
 */
interface BaseImageProps {
  src: string;
  alt: string;
  width?: number;
  height?: number;
  className?: string;
  priority?: boolean;
  quality?: number;
  placeholder?: 'blur' | 'empty';
  blurDataURL?: string;
  onLoad?: () => void;
  onError?: () => void;
}

/**
 * 기본 이미지 컴포넌트
 */
export function BaseImage({
  src,
  alt,
  width,
  height,
  className,
  priority = false,
  quality = 75,
  placeholder = 'empty',
  blurDataURL,
  onLoad,
  onError,
}: BaseImageProps) {
  return (
    <Image
      src={src}
      alt={alt}
      width={width}
      height={height}
      className={className}
      priority={priority}
      quality={quality}
      placeholder={placeholder}
      blurDataURL={blurDataURL}
      onLoad={onLoad}
      onError={onError}
    />
  );
}

/**
 * 로고 이미지 컴포넌트 Props
 */
interface LogoImageProps extends Omit<BaseImageProps, 'src'> {
  filename: string;
  size?: ImageSize;
  fallback?: string;
}

/**
 * 로고 이미지 컴포넌트
 */
export function LogoImage({
  filename,
  size = 'original',
  fallback = DEFAULT_IMAGES.logo,
  alt,
  width,
  height,
  className,
  priority = true,
  ...props
}: LogoImageProps) {
  const logoSrc = getLogoPath(filename, size);
  
  return (
    <BaseImage
      src={logoSrc}
      alt={alt}
      width={width}
      height={height}
      className={className}
      priority={priority}
      onError={() => {
        // 폴백 이미지로 대체
        if (fallback && fallback !== logoSrc) {
          // 여기서는 간단히 콘솔 로그만 출력
          console.warn(`로고 이미지 로드 실패: ${logoSrc}`);
        }
      }}
      {...props}
    />
  );
}

/**
 * 아이콘 이미지 컴포넌트 Props
 */
interface IconImageProps extends Omit<BaseImageProps, 'src'> {
  filename: string;
  size?: ImageSize;
  fallback?: string;
}

/**
 * 아이콘 이미지 컴포넌트
 */
export function IconImage({
  filename,
  size = '32x32',
  fallback,
  alt,
  width = 32,
  height = 32,
  className,
  ...props
}: IconImageProps) {
  const iconSrc = getIconPath(filename, size);
  
  return (
    <BaseImage
      src={iconSrc}
      alt={alt}
      width={width}
      height={height}
      className={className}
      onError={() => {
        if (fallback) {
          console.warn(`아이콘 이미지 로드 실패: ${iconSrc}`);
        }
      }}
      {...props}
    />
  );
}

/**
 * UI 이미지 컴포넌트 Props
 */
interface UIImageProps extends Omit<BaseImageProps, 'src'> {
  filename: string;
  size?: ImageSize;
  fallback?: string;
}

/**
 * UI 이미지 컴포넌트
 */
export function UIImage({
  filename,
  size = 'original',
  fallback,
  alt,
  width,
  height,
  className,
  ...props
}: UIImageProps) {
  const uiSrc = getUIPath(filename, size);
  
  return (
    <BaseImage
      src={uiSrc}
      alt={alt}
      width={width}
      height={height}
      className={className}
      onError={() => {
        if (fallback) {
          console.warn(`UI 이미지 로드 실패: ${uiSrc}`);
        }
      }}
      {...props}
    />
  );
}

/**
 * 배경 이미지 컴포넌트 Props
 */
interface BackgroundImageProps extends Omit<BaseImageProps, 'src'> {
  filename: string;
  size?: ImageSize;
  fallback?: string;
}

/**
 * 배경 이미지 컴포넌트
 */
export function BackgroundImage({
  filename,
  size = 'original',
  fallback,
  alt,
  width,
  height,
  className,
  ...props
}: BackgroundImageProps) {
  const bgSrc = getBackgroundPath(filename, size);
  
  return (
    <BaseImage
      src={bgSrc}
      alt={alt}
      width={width}
      height={height}
      className={className}
      onError={() => {
        if (fallback) {
          console.warn(`배경 이미지 로드 실패: ${bgSrc}`);
        }
      }}
      {...props}
    />
  );
}

/**
 * 최적화된 이미지 컴포넌트 Props
 */
interface OptimizedImageProps extends BaseImageProps {
  category: ImageCategory;
  filename: string;
  size?: ImageSize;
  optimization?: ImageOptimizationOptions;
}

/**
 * 최적화된 이미지 컴포넌트
 */
export function OptimizedImage({
  category,
  filename,
  size = 'original',
  optimization,
  alt,
  width,
  height,
  className,
  ...props
}: OptimizedImageProps) {
  const imageSrc = getImagePath(category, filename, size);
  
  return (
    <BaseImage
      src={imageSrc}
      alt={alt}
      width={width}
      height={height}
      className={className}
      quality={optimization?.quality}
      {...props}
    />
  );
}

/**
 * 이미지 갤러리 컴포넌트 Props
 */
interface ImageGalleryProps {
  images: Array<{
    src: string;
    alt: string;
    caption?: string;
  }>;
  className?: string;
  columns?: number;
}

/**
 * 이미지 갤러리 컴포넌트
 */
export function ImageGallery({
  images,
  className = '',
  columns = 3,
}: ImageGalleryProps) {
  const gridCols = {
    1: 'grid-cols-1',
    2: 'grid-cols-2',
    3: 'grid-cols-3',
    4: 'grid-cols-4',
    5: 'grid-cols-5',
    6: 'grid-cols-6',
  }[columns] || 'grid-cols-3';

  return (
    <div className={`grid ${gridCols} gap-4 ${className}`}>
      {images.map((image, index) => (
        <div key={index} className="relative">
          <BaseImage
            src={image.src}
            alt={image.alt}
            width={300}
            height={200}
            className="w-full h-48 object-cover rounded-lg"
          />
          {image.caption && (
            <p className="mt-2 text-sm text-gray-600 text-center">
              {image.caption}
            </p>
          )}
        </div>
      ))}
    </div>
  );
}

/**
 * 이미지 플레이스홀더 컴포넌트
 */
export function ImagePlaceholder({
  width = 300,
  height = 200,
  className = '',
  children,
}: {
  width?: number;
  height?: number;
  className?: string;
  children?: React.ReactNode;
}) {
  return (
    <div
      className={`bg-gray-200 flex items-center justify-center ${className}`}
      style={{ width, height }}
    >
      {children || (
        <div className="text-gray-400 text-center">
          <svg
            className="w-12 h-12 mx-auto mb-2"
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path
              fillRule="evenodd"
              d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z"
              clipRule="evenodd"
            />
          </svg>
          <p className="text-sm">이미지 없음</p>
        </div>
      )}
    </div>
  );
}


