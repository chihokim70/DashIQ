const express = require('express');
const cors = require('cors');
const { Pool } = require('pg');
require('dotenv').config();

const app = express();
const port = process.env.PORT || 3002;

// CORS 설정 - DashIQ 프론트엔드와 연동
app.use(cors({
  origin: ['http://localhost:3001', 'http://localhost:3000'],
  credentials: true
}));

app.use(express.json());

// PostgreSQL 연결 설정
const pool = new Pool({
  host: process.env.DB_HOST || 'aigov_postgres',
  port: process.env.DB_PORT || 5432,
  database: process.env.DB_NAME || 'aigov_admin',
  user: process.env.DB_USER || 'aigov_user',
  password: process.env.DB_PASSWORD || 'aigov_password',
});

// 헬스 체크 엔드포인트
app.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// 날짜 필터링 헬퍼 함수
function getDateFilter(year, month, week) {
  const currentDate = new Date();
  let startDate, endDate;

  if (year && year !== 'all') {
    const targetYear = parseInt(year);
    
    if (month && month !== 'all') {
      const targetMonth = parseInt(month) - 1; // JavaScript month is 0-indexed
      
      if (week && week !== 'all') {
        // 특정 주
        const targetWeek = parseInt(week);
        startDate = new Date(targetYear, targetMonth, (targetWeek - 1) * 7 + 1);
        endDate = new Date(targetYear, targetMonth, targetWeek * 7);
      } else {
        // 특정 년월
        startDate = new Date(targetYear, targetMonth, 1);
        endDate = new Date(targetYear, targetMonth + 1, 0);
      }
    } else {
      // 특정 년도 전체
      startDate = new Date(targetYear, 0, 1);
      endDate = new Date(targetYear, 11, 31);
    }
  } else {
    // 기본값: 이번 달
    startDate = new Date(currentDate.getFullYear(), currentDate.getMonth(), 1);
    endDate = new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 0);
  }

  return {
    startDate: startDate.toISOString(),
    endDate: endDate.toISOString()
  };
}

// 대시보드 KPI 데이터 엔드포인트 (날짜 필터링 지원)
app.get('/api/dashboard/kpi', async (req, res) => {
  try {
    const tenantId = 1; // 기본 테넌트
    const { year, month, week } = req.query;
    
    // 날짜 필터 생성
    const { startDate, endDate } = getDateFilter(year, month, week);

    // 전체 AI 요청 수 (필터링된 기간)
    const totalRequestsQuery = `
      SELECT COALESCE(SUM(total_prompts), 0) as total_requests,
             COALESCE(SUM(total_tokens), 0) as total_tokens,
             COALESCE(SUM(total_cost), 0) as total_cost
      FROM prompt_sessions 
      WHERE tenant_id = $1 
      AND created_at >= $2::timestamp
      AND created_at <= $3::timestamp
    `;
    const totalRequestsResult = await pool.query(totalRequestsQuery, [tenantId, startDate, endDate]);
    const totalRequests = totalRequestsResult.rows[0].total_requests || 0;

    // 정책 위반 수 (필터링된 기간)
    const violationsQuery = `
      SELECT COUNT(*) as violation_count
      FROM decision_logs 
      WHERE tenant_id = $1 
      AND decision = 'deny'
      AND ts >= $2::timestamp
      AND ts <= $3::timestamp
    `;
    const violationsResult = await pool.query(violationsQuery, [tenantId, startDate, endDate]);
    const violations = violationsResult.rows[0].violation_count || 0;

    // Shadow AI 탐지 수 (필터링된 기간)
    const shadowAIQuery = `
      SELECT COUNT(*) as shadow_count
      FROM shadow_events 
      WHERE tenant_id = $1 
      AND ts >= $2::timestamp
      AND ts <= $3::timestamp
    `;
    const shadowAIResult = await pool.query(shadowAIQuery, [tenantId, startDate, endDate]);
    const shadowAI = shadowAIResult.rows[0].shadow_count || 0;

    // AI 서비스 활성 사용자 수 (필터링된 기간)
    const activeUsersQuery = `
      SELECT COUNT(DISTINCT user_id) as active_users
      FROM prompt_sessions 
      WHERE tenant_id = $1 
      AND created_at >= $2::timestamp
      AND created_at <= $3::timestamp
    `;
    const activeUsersResult = await pool.query(activeUsersQuery, [tenantId, startDate, endDate]);
    const activeUsers = activeUsersResult.rows[0].active_users || 0;

    // KPI 데이터 포맷팅
    const kpiData = {
      totalAIRequests: {
        value: totalRequests > 1000 ? `${(totalRequests / 1000).toFixed(1)}K` : totalRequests.toString(),
        rawValue: totalRequests,
        trend: { value: '12.5%', isPositive: true }
      },
      policyViolations: {
        value: violations.toString(),
        rawValue: violations,
        trend: { value: '8.2%', isPositive: false }
      },
      shadowAIDetected: {
        value: shadowAI.toString(),
        rawValue: shadowAI,
        trend: { value: '15.3%', isPositive: false }
      },
      aiServiceUsers: {
        value: activeUsers.toString(),
        rawValue: activeUsers,
        trend: { value: '34.8%', isPositive: true }
      }
    };

    res.json({
      success: true,
      data: kpiData,
      filter: {
        year: year || 'current',
        month: month || 'current', 
        week: week || 'all',
        period: { startDate, endDate }
      },
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    console.error('KPI 데이터 조회 오류:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to fetch KPI data',
      message: error.message
    });
  }
});

// 부서별 사용량 데이터
app.get('/api/dashboard/department-usage', async (req, res) => {
  try {
    const tenantId = 1;

    const query = `
      SELECT 
        u.department,
        COUNT(DISTINCT u.id) as user_count,
        COALESCE(SUM(ps.total_prompts), 0) as total_requests,
        COALESCE(SUM(ps.total_tokens), 0) as total_tokens,
        COALESCE(SUM(ps.total_cost), 0) as total_cost,
        COUNT(DISTINCT CASE WHEN dl.decision = 'deny' THEN dl.id END) as violations
      FROM users u
      LEFT JOIN prompt_sessions ps ON u.id = ps.user_id 
        AND ps.created_at >= NOW() - INTERVAL '7 days'
      LEFT JOIN decision_logs dl ON u.id = dl.user_id 
        AND dl.ts >= NOW() - INTERVAL '7 days'
      WHERE u.tenant_id = $1 
      AND u.department IS NOT NULL
      GROUP BY u.department
      ORDER BY total_requests DESC
    `;

    const result = await pool.query(query, [tenantId]);
    
    res.json({
      success: true,
      data: result.rows,
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    console.error('부서별 사용량 조회 오류:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to fetch department usage data'
    });
  }
});

// 최근 고위험 이벤트
app.get('/api/dashboard/recent-events', async (req, res) => {
  try {
    const tenantId = 1;
    const limit = req.query.limit || 10;

    const query = `
      SELECT 
        dl.id,
        dl.ts,
        u.email as user_email,
        u.display_name as user_name,
        u.department,
        dl.model_name,
        dl.decision,
        dl.reasons,
        dl.summary,
        CASE 
          WHEN 'PII_DETECTED' = ANY(dl.reasons) THEN 'Critical'
          WHEN 'DATA_LEAK_PREVENTION' = ANY(dl.reasons) THEN 'Critical'
          WHEN 'PROMPT_INJECTION_DETECTED' = ANY(dl.reasons) THEN 'High'
          WHEN 'USAGE_LIMIT_EXCEEDED' = ANY(dl.reasons) THEN 'Medium'
          ELSE 'Low'
        END as risk_level
      FROM decision_logs dl
      LEFT JOIN users u ON dl.user_id = u.id
      WHERE dl.tenant_id = $1 
      AND dl.decision = 'deny'
      AND dl.ts >= NOW() - INTERVAL '7 days'
      ORDER BY dl.ts DESC
      LIMIT $2
    `;

    const result = await pool.query(query, [tenantId, limit]);
    
    const events = result.rows.map(row => ({
      id: row.id,
      time: new Date(row.ts).toLocaleTimeString('ko-KR', { 
        hour: '2-digit', 
        minute: '2-digit' 
      }),
      user: row.user_email || 'Unknown',
      userName: row.user_name || 'Unknown User',
      department: row.department || 'Unknown',
      model: row.model_name || 'Unknown',
      risk: row.risk_level,
      action: 'Blocked',
      policy: row.reasons && row.reasons[0] ? row.reasons[0].replace('_', ' ') : 'Policy Violation',
      summary: row.summary
    }));

    res.json({
      success: true,
      data: events,
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    console.error('최근 이벤트 조회 오류:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to fetch recent events'
    });
  }
});

// Shadow AI 활동 히트맵 데이터
app.get('/api/dashboard/shadow-ai-heatmap', async (req, res) => {
  try {
    const tenantId = 1;

    const query = `
      SELECT 
        EXTRACT(HOUR FROM ts) as hour,
        EXTRACT(DOW FROM ts) as dow,
        COUNT(*) as count
      FROM shadow_events 
      WHERE tenant_id = $1 
      AND ts >= NOW() - INTERVAL '7 days'
      GROUP BY EXTRACT(HOUR FROM ts), EXTRACT(DOW FROM ts)
      ORDER BY hour, dow
    `;

    const result = await pool.query(query, [tenantId]);
    
    // 히트맵 데이터 포맷팅 (시간 x 요일)
    const heatmapData = {};
    const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
    
    // 0시~23시, 일~토 초기화
    for (let hour = 0; hour < 24; hour++) {
      const hourKey = `${hour.toString().padStart(2, '0')}:00`;
      heatmapData[hourKey] = {};
      days.forEach(day => {
        heatmapData[hourKey][day] = 0;
      });
    }

    // 실제 데이터로 채우기
    result.rows.forEach(row => {
      const hourKey = `${parseInt(row.hour).toString().padStart(2, '0')}:00`;
      const dayName = days[parseInt(row.dow)];
      heatmapData[hourKey][dayName] = parseInt(row.count);
    });

    // 배열 형태로 변환
    const heatmapArray = Object.entries(heatmapData).map(([hour, dayData]) => ({
      hour,
      ...dayData
    }));

    res.json({
      success: true,
      data: heatmapArray,
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    console.error('Shadow AI 히트맵 조회 오류:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to fetch shadow AI heatmap data'
    });
  }
});

// AI Service Users 트렌드 (일별 활성 사용자 수)
app.get('/api/dashboard/users-trend', async (req, res) => {
  try {
    const tenantId = 1;
    const { year, month, week } = req.query;
    const { startDate, endDate } = getDateFilter(year, month, week);

    const query = `
      WITH daily_users AS (
        SELECT 
          DATE(created_at) as date,
          COUNT(DISTINCT user_id) as active_users
        FROM prompt_sessions 
        WHERE tenant_id = $1 
        AND created_at >= $2::timestamp
        AND created_at <= $3::timestamp
        GROUP BY DATE(created_at)
        ORDER BY DATE(created_at)
      )
      SELECT 
        to_char(date, 'Mon DD') as date_label,
        active_users
      FROM daily_users
      ORDER BY date
    `;

    const result = await pool.query(query, [tenantId, startDate, endDate]);
    
    res.json({
      success: true,
      data: result.rows,
      filter: {
        year: year || 'current',
        month: month || 'current',
        week: week || 'all',
        period: { startDate, endDate }
      },
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    console.error('사용자 트렌드 조회 오류:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to fetch users trend data'
    });
  }
});

// Model-wise User Distribution (모델별 사용자 분포)
app.get('/api/dashboard/model-distribution', async (req, res) => {
  try {
    const tenantId = 1;
    const { year, month, week } = req.query;
    const { startDate, endDate } = getDateFilter(year, month, week);

    const query = `
      SELECT 
        model_name,
        COUNT(DISTINCT user_id) as user_count,
        COUNT(*) as session_count,
        SUM(total_prompts) as total_requests,
        ROUND(SUM(total_cost), 2) as total_cost
      FROM prompt_sessions 
      WHERE tenant_id = $1 
      AND created_at >= $2::timestamp
      AND created_at <= $3::timestamp
      AND model_name IS NOT NULL
      GROUP BY model_name
      ORDER BY user_count DESC
    `;

    const result = await pool.query(query, [tenantId, startDate, endDate]);
    
    res.json({
      success: true,
      data: result.rows,
      filter: {
        year: year || 'current',
        month: month || 'current',
        week: week || 'all',
        period: { startDate, endDate }
      },
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    console.error('모델 분포 조회 오류:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to fetch model distribution data'
    });
  }
});

// Department Distribution (부서별 분포)
app.get('/api/dashboard/department-distribution', async (req, res) => {
  try {
    const tenantId = 1;
    const { year, month, week } = req.query;
    const { startDate, endDate } = getDateFilter(year, month, week);

    const query = `
      SELECT 
        u.department,
        COUNT(DISTINCT u.id) as total_users,
        COUNT(DISTINCT ps.user_id) as active_users,
        COALESCE(SUM(ps.total_prompts), 0) as total_requests,
        COALESCE(SUM(ps.total_tokens), 0) as total_tokens,
        COALESCE(ROUND(SUM(ps.total_cost), 2), 0) as total_cost,
        COUNT(DISTINCT CASE WHEN dl.decision = 'deny' THEN dl.user_id END) as violation_users,
        COUNT(CASE WHEN dl.decision = 'deny' THEN 1 END) as violation_count
      FROM users u
      LEFT JOIN prompt_sessions ps ON u.id = ps.user_id 
        AND ps.created_at >= $2::timestamp
        AND ps.created_at <= $3::timestamp
      LEFT JOIN decision_logs dl ON u.id = dl.user_id 
        AND dl.ts >= $2::timestamp
        AND dl.ts <= $3::timestamp
      WHERE u.tenant_id = $1 
      AND u.department IS NOT NULL
      GROUP BY u.department
      ORDER BY active_users DESC, total_requests DESC
    `;

    const result = await pool.query(query, [tenantId, startDate, endDate]);
    
    res.json({
      success: true,
      data: result.rows,
      filter: {
        year: year || 'current',
        month: month || 'current',
        week: week || 'all',
        period: { startDate, endDate }
      },
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    console.error('부서 분포 조회 오류:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to fetch department distribution data'
    });
  }
});

// 일별 사용량 트렌드
app.get('/api/dashboard/usage-trend', async (req, res) => {
  try {
    const tenantId = 1;

    const query = `
      WITH daily_stats AS (
        SELECT 
          DATE(created_at) as date,
          SUM(total_prompts) as requests
        FROM prompt_sessions 
        WHERE tenant_id = $1 
        AND created_at >= NOW() - INTERVAL '7 days'
        GROUP BY DATE(created_at)
      ),
      daily_violations AS (
        SELECT 
          DATE(ts) as date,
          COUNT(*) as violations
        FROM decision_logs 
        WHERE tenant_id = $1 
        AND decision = 'deny'
        AND ts >= NOW() - INTERVAL '7 days'
        GROUP BY DATE(ts)
      )
      SELECT 
        ds.date,
        COALESCE(ds.requests, 0) as requests,
        COALESCE(dv.violations, 0) as violations
      FROM daily_stats ds
      FULL OUTER JOIN daily_violations dv ON ds.date = dv.date
      ORDER BY COALESCE(ds.date, dv.date)
    `;

    const result = await pool.query(query, [tenantId]);
    
    const trendData = result.rows.map(row => ({
      date: new Date(row.date).toLocaleDateString('en-US', { 
        month: 'short', 
        day: 'numeric' 
      }),
      requests: parseInt(row.requests) || 0,
      violations: parseInt(row.violations) || 0
    }));

    res.json({
      success: true,
      data: trendData,
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    console.error('사용량 트렌드 조회 오류:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to fetch usage trend data'
    });
  }
});

// AI Service Users 상세 통계 (Total Users, AI Service Users, Adoption Rate, Growth)
app.get('/api/dashboard/user-statistics', async (req, res) => {
  try {
    const tenantId = 1;
    const { year, month, week } = req.query;
    const { startDate, endDate } = getDateFilter(year, month, week);

    // 전체 사용자 수
    const totalUsersQuery = `
      SELECT COUNT(*) as total_users
      FROM users 
      WHERE tenant_id = $1 
      AND created_at <= $2::timestamp
    `;
    const totalUsersResult = await pool.query(totalUsersQuery, [tenantId, endDate]);
    const totalUsers = parseInt(totalUsersResult.rows[0].total_users) || 0;

    // AI 서비스 활성 사용자 수 (필터링 기간 내)
    const aiServiceUsersQuery = `
      SELECT COUNT(DISTINCT user_id) as ai_service_users
      FROM prompt_sessions 
      WHERE tenant_id = $1 
      AND created_at >= $2::timestamp
      AND created_at <= $3::timestamp
    `;
    const aiServiceUsersResult = await pool.query(aiServiceUsersQuery, [tenantId, startDate, endDate]);
    const aiServiceUsers = parseInt(aiServiceUsersResult.rows[0].ai_service_users) || 0;

    // 지난 기간 AI 서비스 사용자 수 (성장률 계산용)
    const periodLength = new Date(endDate) - new Date(startDate);
    const previousStartDate = new Date(new Date(startDate) - periodLength).toISOString();
    const previousEndDate = startDate;

    const previousAiUsersQuery = `
      SELECT COUNT(DISTINCT user_id) as previous_ai_users
      FROM prompt_sessions 
      WHERE tenant_id = $1 
      AND created_at >= $2::timestamp
      AND created_at <= $3::timestamp
    `;
    const previousAiUsersResult = await pool.query(previousAiUsersQuery, [tenantId, previousStartDate, previousEndDate]);
    const previousAiUsers = parseInt(previousAiUsersResult.rows[0].previous_ai_users) || 0;

    // 채택률 계산
    const adoptionRate = totalUsers > 0 ? ((aiServiceUsers / totalUsers) * 100) : 0;

    // 성장률 계산
    const growthRate = previousAiUsers > 0 
      ? (((aiServiceUsers - previousAiUsers) / previousAiUsers) * 100) 
      : (aiServiceUsers > 0 ? 100 : 0);

    const statistics = {
      totalUsers: {
        value: totalUsers.toLocaleString(),
        rawValue: totalUsers
      },
      aiServiceUsers: {
        value: aiServiceUsers.toLocaleString(), 
        rawValue: aiServiceUsers
      },
      adoptionRate: {
        value: `${adoptionRate.toFixed(1)}%`,
        rawValue: adoptionRate,
        isPositive: adoptionRate > 30
      },
      growth: {
        value: `${growthRate >= 0 ? '↑' : '↓'} ${Math.abs(growthRate).toFixed(1)}%`,
        rawValue: growthRate,
        isPositive: growthRate > 0
      }
    };

    res.json({
      success: true,
      data: statistics,
      filter: {
        year: year || 'current',
        month: month || 'current',
        week: week || 'all',
        period: { startDate, endDate }
      },
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    console.error('사용자 통계 조회 오류:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to fetch user statistics data',
      message: error.message
    });
  }
});

// 서버 시작
app.listen(port, () => {
  console.log(`DashIQ API Server running on port ${port}`);
  console.log(`Health check: http://localhost:${port}/health`);
});

// 데이터베이스 연결 테스트
pool.query('SELECT NOW()')
  .then(() => {
    console.log('✅ Database connected successfully');
  })
  .catch(err => {
    console.error('❌ Database connection failed:', err.message);
  });