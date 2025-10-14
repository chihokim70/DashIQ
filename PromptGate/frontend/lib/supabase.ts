import { createClient } from "@supabase/supabase-js";
import { createServerSupabaseClient } from "@supabase/auth-helpers-nextjs";
import { getEnvironmentVariable } from "@/lib/general-helpers";
import { NextApiRequest, NextApiResponse } from "next";
import { createMockSupabaseClient, isMockMode } from "./supabase-mock";

// Mock 모드일 때는 Mock 클라이언트 사용
export const supabaseAnonClient = isMockMode 
  ? createMockSupabaseClient()
  : createClient(
      getEnvironmentVariable("NEXT_PUBLIC_SUPABASE_URL"),
      getEnvironmentVariable("NEXT_PUBLIC_SUPABASE_ANON_KEY")
    );

export const supabaseAdminClient = isMockMode
  ? createMockSupabaseClient()
  : createClient(
      getEnvironmentVariable("NEXT_PUBLIC_SUPABASE_URL"),
      getEnvironmentVariable("SUPABASE_SERVICE_KEY")
    );

export const getSupabaseUser = async (
  req: NextApiRequest,
  res: NextApiResponse
) => {
  // Mock 모드일 때는 Mock 사용자 반환
  if (isMockMode) {
    const { MOCK_USER } = await import("./supabase-mock");
    return MOCK_USER;
  }

  // Create authenticated Supabase Client
  const supabase = createServerSupabaseClient({ req, res });

  // Check if we have a session
  const {
    data: { session },
  } = await supabase.auth.getSession();

  // If no session, return not authenticated
  if (!session) {
    throw new Error("not authenticated");
  }

  // Get user
  const {
    data: { user },
  } = await supabase.auth.getUser();

  // If user is null, return not authenticated
  if (!user) {
    throw new Error("not authenticated");
  }
  return user;
};
