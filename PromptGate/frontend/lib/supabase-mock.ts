// Mock Supabase 클라이언트 - 개발 환경용
import { User, Session } from '@supabase/supabase-js';

// Mock 사용자 데이터
export const MOCK_USER: User = {
  id: 'mock-user-123',
  aud: 'authenticated',
  role: 'authenticated',
  email: 'test@example.com',
  email_confirmed_at: '2025-10-14T00:00:00Z',
  phone: '',
  confirmed_at: '2025-10-14T00:00:00Z',
  last_sign_in_at: '2025-10-14T00:00:00Z',
  app_metadata: {
    provider: 'google',
    providers: ['google']
  },
  user_metadata: {
    username: 'testuser',
    full_name: 'Test User'
  },
  identities: [],
  created_at: '2025-10-14T00:00:00Z',
  updated_at: '2025-10-14T00:00:00Z'
};

// Mock 세션 데이터
export const MOCK_SESSION: Session = {
  access_token: 'mock-access-token',
  refresh_token: 'mock-refresh-token',
  expires_in: 3600,
  expires_at: Math.floor(Date.now() / 1000) + 3600,
  token_type: 'bearer',
  user: MOCK_USER
};

// Mock Supabase 클라이언트
export const createMockSupabaseClient = () => {
  return {
    auth: {
      getSession: async () => ({ data: { session: MOCK_SESSION }, error: null }),
      getUser: async () => ({ data: { user: MOCK_USER }, error: null }),
      signInWithOAuth: async () => ({ data: MOCK_SESSION, error: null }),
      signOut: async () => ({ error: null }),
      onAuthStateChange: (callback: any) => {
        // 즉시 로그인된 상태로 콜백 호출
        callback('SIGNED_IN', MOCK_SESSION);
        return { data: { subscription: { unsubscribe: () => {} } } };
      }
    },
    from: (table: string) => ({
      select: (columns?: string) => ({
        eq: (column: string, value: any) => ({
          single: async () => ({ data: null, error: null }),
          then: async (resolve: any) => resolve({ data: [], error: null })
        }),
        then: async (resolve: any) => resolve({ data: [], error: null })
      }),
      insert: (data: any) => ({
        select: async (columns?: string) => ({ data: [], error: null })
      }),
      update: (data: any) => ({
        eq: (column: string, value: any) => ({
          select: async (columns?: string) => ({ data: [], error: null })
        })
      })
    })
  } as any;
};

// Mock 모드 확인
export const isMockMode = process.env.NODE_ENV === 'development' || 
                          process.env.NEXT_PUBLIC_APP_ENV === 'development';
