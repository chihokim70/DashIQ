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

// 대시보드 KPI 데이터 엔드포인트
app.get('/api/dashboard/kpi', async (req, res) => {
  try {
    const tenantId = 1; // 기본 테넌트

    // 전체 AI 요청 수 (이번 달)
    const totalRequestsQuery = `
      SELECT COALESCE(SUM(total_prompts), 0) as total_requests,
             COALESCE(SUM(total_tokens), 0) as total_tokens,
             COALESCE(SUM(total_cost), 0) as total_cost
      FROM prompt_sessions 
      WHERE tenant_id = $1 
      AND created_at >= DATE_TRUNC('month', NOW())
    `;
    const totalRequestsResult = await pool.query(totalRequestsQuery, [tenantId]);
    const totalRequests = totalRequestsResult.rows[0].total_requests || 0;

    // 정책 위반 수 (이번 달)
    const violationsQuery = `
      SELECT COUNT(*) as violation_count
      FROM decision_logs 
      WHERE tenant_id = $1 
      AND decision = 'deny'
      AND ts >= DATE_TRUNC('month', NOW())
    `;
    const violationsResult = await pool.query(violationsQuery, [tenantId]);
    const violations = violationsResult.rows[0].violation_count || 0;

    // Shadow AI 탐지 수 (이번 달)
    const shadowAIQuery = `
      SELECT COUNT(*) as shadow_count
      FROM shadow_events 
      WHERE tenant_id = $1 
      AND ts >= DATE_TRUNC('month', NOW())
    `;
    const shadowAIResult = await pool.query(shadowAIQuery, [tenantId]);
    const shadowAI = shadowAIResult.rows[0].shadow_count || 0;

    // AI 서비스 활성 사용자 수 (이번 달)
    const activeUsersQuery = `
      SELECT COUNT(DISTINCT user_id) as active_users
      FROM prompt_sessions 
      WHERE tenant_id = $1 
      AND created_at >= DATE_TRUNC('month', NOW())
    `;
    const activeUsersResult = await pool.query(activeUsersQuery, [tenantId]);
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