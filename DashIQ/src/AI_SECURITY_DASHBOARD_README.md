# AiGov | DashIQ - AI Governance Dashboard

## 📋 Overview

**AiGov DashIQ** is a comprehensive enterprise AI governance platform that provides real-time monitoring, policy enforcement, and security management for AI usage across your organization.

## 🎯 Key Features

### 1. **Dashboard Overview**
- Real-time KPI metrics (AI requests, violations, Shadow AI, On-Prem usage)
- Interactive charts for usage trends and department analytics
- Model vendor distribution visualization
- High-risk event monitoring with severity badges
- Shadow AI activity heatmap by day/hour

### 2. **Prompt Usage Statistics**
- User-level prompt tracking and token consumption
- Cost analysis and budget monitoring
- Department-wise usage breakdown
- Multi-model support tracking (GPT-4, Claude, Gemini, On-Prem)
- Exportable usage reports

### 3. **Policy Monitor**
- Active policy tracking and violation detection
- Department and time-based violation heatmaps
- Top 10 policy violations with severity indicators
- Real-time critical violation alerts
- Customizable policy rules

### 4. **Shadow AI Detection**
- Unauthorized AI tool detection (ChatGPT Plus, Claude Personal, LM Studio, Ollama)
- Domain and process monitoring
- Department-level activity visualization
- Risk-based classification (Critical, High, Medium, Low)
- Suspicious process identification

### 5. **On-Premise LLM Monitoring**
- GPU utilization and performance metrics
- Model-specific performance tracking
- Server health monitoring (temperature, memory, usage)
- Latency and error rate tracking
- Threshold-based alerting

### 6. **Image Generation Monitoring**
- DALL-E, Stable Diffusion, Midjourney tracking
- NSFW content detection
- Privacy-protected image previews (blurred thumbnails)
- Department-wise generation statistics
- Flagged content management

### 7. **Case Management**
- Kanban-style workflow (New, In Progress, Completed)
- Incident tracking and assignment
- Severity-based prioritization
- Department and user filtering
- Case history and audit trail

### 8. **Settings & Configuration**
- Organization-wide settings
- Policy rule configuration
- Notification preferences (Email, Slack, Teams)
- AI model provider integrations
- Data retention and security settings

## 🎨 Design System

### Color Palette
- **Primary**: `#1E90FF` (Dodger Blue)
- **Secondary**: `#10B981` (Emerald Green)
- **Accent**: `#F59E0B` (Amber)
- **Destructive**: `#EF4444` (Red)
- **Background**: `#F9FAFB` (Gray)
- **Foreground**: `#111827` (Dark Gray)

### Typography
- **Font Family**: System default (Inter/Pretendard compatible)
- **Heading Sizes**: 24px (H1), 18px (H2), 16px (H3)
- **Body**: 14-16px
- **Spacing**: 16px/24px grid system
- **Border Radius**: 12px

### Dark Mode
Full dark mode support with optimized color schemes for reduced eye strain during extended monitoring sessions.

## 📊 Data Visualization

The dashboard uses **Recharts** library for all data visualizations:
- Line charts for trend analysis
- Bar charts for comparative metrics
- Pie charts for distribution analysis
- Custom heatmaps for time/department analysis
- Circular gauge charts for real-time metrics

## 🔔 Real-Time Features

- **Auto-refresh**: Dashboard updates every 10 seconds
- **Live notifications**: Real-time alerts for critical events
- **Status indicators**: Visual feedback for system health
- **Badge notifications**: Unread alert counters

## 🛡️ Security Features

- Two-factor authentication support
- IP whitelisting
- Role-based access control (implied)
- Audit logging
- Data encryption (best practices)
- Secure API key management

## 🔧 Technical Stack

- **Framework**: React with TypeScript
- **Styling**: Tailwind CSS v4.0
- **Components**: shadcn/ui component library
- **Charts**: Recharts
- **Icons**: Lucide React
- **State Management**: React hooks (useState, useEffect)

## 📱 Responsive Design

The dashboard is fully responsive with breakpoints:
- **Mobile**: < 768px
- **Tablet**: 768px - 1024px
- **Desktop**: > 1024px

## 🚀 Quick Start

The application is ready to use. Simply navigate through the sidebar menu to access different modules:

1. **Dashboard Overview** - Start here for a comprehensive view
2. **Prompt Usage** - Monitor AI usage and costs
3. **Policy Monitor** - Track compliance
4. **Shadow AI** - Detect unauthorized tools
5. **On-Prem LLM** - Monitor infrastructure
6. **Image Generation** - Track image AI usage
7. **Case Management** - Manage incidents
8. **Settings** - Configure the platform

## 🎛️ Global Filters

Available in the header:
- **Period**: Last 24 hours, 7 days, 30 days, 90 days
- **Department**: All, Engineering, Sales, Marketing, HR
- **Model**: All, GPT-4, Claude, Gemini, On-Prem
- **Policy**: All, Active, With Violations

## 📈 Metrics & KPIs

### Key Performance Indicators:
- Total AI Requests
- Policy Violations
- Shadow AI Detections
- On-Prem LLM Usage
- Token Consumption
- Cost Analysis
- Success Rates
- Response Times

### Trending Metrics:
- Usage growth percentages
- Violation trends
- Cost projections
- Performance benchmarks

## 🔍 Monitoring Capabilities

- **User Activity**: Track individual user behavior
- **Department Analytics**: Identify high-usage teams
- **Model Performance**: Compare AI model efficiency
- **Cost Optimization**: Identify cost-saving opportunities
- **Risk Assessment**: Prioritize security threats
- **Compliance Tracking**: Ensure policy adherence

## 📝 Best Practices

1. **Regular Monitoring**: Check dashboard daily for anomalies
2. **Policy Updates**: Review and update policies quarterly
3. **Team Training**: Educate users on governance policies
4. **Incident Response**: Address critical violations immediately
5. **Cost Management**: Set department budgets and limits
6. **Data Retention**: Follow compliance requirements

## 🆘 Support & Maintenance

- **Version**: 2.4.1
- **Auto-updates**: Enabled
- **Backup**: Recommended daily
- **Log Retention**: 90 days (configurable)

## 📊 Sample Use Cases

1. **Detecting PII Leaks**: Real-time alerts when users share sensitive data
2. **Budget Control**: Track and limit AI spending per department
3. **Shadow IT Prevention**: Identify unauthorized AI tool usage
4. **Performance Optimization**: Monitor on-prem LLM efficiency
5. **Compliance Reporting**: Generate audit-ready reports
6. **Incident Management**: Track and resolve security events

## 🎯 Future Enhancements

- Advanced ML-based anomaly detection
- Custom report builder
- API access for integrations
- Mobile app support
- Multi-language support
- Enhanced role-based permissions

---

**© 2025 AiGov | DashIQ** - Enterprise AI Governance Platform
