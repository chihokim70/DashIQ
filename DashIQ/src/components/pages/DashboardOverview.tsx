import { useState, useEffect } from "react";
import { createPortal } from "react-dom";
import { Activity, AlertTriangle, Eye, Server, GripVertical, X, Clock, User, Shield, Users } from "lucide-react";
import { KPICard } from "../KPICard";
import { Card, CardContent, CardHeader, CardTitle } from "../ui/card";
import { Badge } from "../ui/badge";
import { Button } from "../ui/button";
import { FilterBar } from "../FilterBar";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "../ui/dialog";
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";
import { DndContext, closestCenter, KeyboardSensor, PointerSensor, useSensor, useSensors, DragEndEvent } from "@dnd-kit/core";
import { arrayMove, SortableContext, sortableKeyboardCoordinates, rectSortingStrategy, useSortable } from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import { Rnd } from "react-rnd";

const dailyUsageData = [
  { date: "Oct 24", requests: 1200, violations: 45 },
  { date: "Oct 25", requests: 1850, violations: 32 },
  { date: "Oct 26", requests: 2100, violations: 28 },
  { date: "Oct 27", requests: 1950, violations: 51 },
  { date: "Oct 28", requests: 2400, violations: 38 },
  { date: "Oct 29", requests: 2800, violations: 42 },
  { date: "Oct 30", requests: 3200, violations: 35 },
  { date: "Oct 31", requests: 2950, violations: 29 },
];

// Department data with model breakdown (stacked bar chart)
const departmentDataWithModels = [
  { 
    department: "Engineering", 
    OpenAI: 3500, 
    Anthropic: 2500, 
    Google: 1500, 
    OnPrem: 800, 
    Others: 200,
    total: 8500 
  },
  { 
    department: "Sales", 
    OpenAI: 1400, 
    Anthropic: 800, 
    Google: 500, 
    OnPrem: 300, 
    Others: 200,
    total: 3200 
  },
  { 
    department: "Marketing", 
    OpenAI: 1800, 
    Anthropic: 1200, 
    Google: 700, 
    OnPrem: 300, 
    Others: 100,
    total: 4100 
  },
  { 
    department: "HR", 
    OpenAI: 800, 
    Anthropic: 500, 
    Google: 300, 
    OnPrem: 150, 
    Others: 50,
    total: 1800 
  },
  { 
    department: "Finance", 
    OpenAI: 1100, 
    Anthropic: 700, 
    Google: 400, 
    OnPrem: 150, 
    Others: 50,
    total: 2400 
  },
];

// Department daily trend data (for popup)
const departmentDailyTrend: Record<string, any[]> = {
  "Engineering": [
    { date: "Oct 24", requests: 1200, violations: 18 },
    { date: "Oct 25", requests: 1400, violations: 15 },
    { date: "Oct 26", requests: 1600, violations: 12 },
    { date: "Oct 27", requests: 1500, violations: 20 },
    { date: "Oct 28", requests: 1700, violations: 16 },
    { date: "Oct 29", requests: 1800, violations: 19 },
    { date: "Oct 30", requests: 2000, violations: 14 },
    { date: "Oct 31", requests: 1900, violations: 13 },
  ],
  "Sales": [
    { date: "Oct 24", requests: 450, violations: 8 },
    { date: "Oct 25", requests: 500, violations: 6 },
    { date: "Oct 26", requests: 480, violations: 7 },
    { date: "Oct 27", requests: 520, violations: 9 },
    { date: "Oct 28", requests: 550, violations: 7 },
    { date: "Oct 29", requests: 600, violations: 8 },
    { date: "Oct 30", requests: 620, violations: 6 },
    { date: "Oct 31", requests: 580, violations: 5 },
  ],
  "Marketing": [
    { date: "Oct 24", requests: 580, violations: 10 },
    { date: "Oct 25", requests: 620, violations: 8 },
    { date: "Oct 26", requests: 650, violations: 9 },
    { date: "Oct 27", requests: 600, violations: 12 },
    { date: "Oct 28", requests: 680, violations: 9 },
    { date: "Oct 29", requests: 720, violations: 10 },
    { date: "Oct 30", requests: 750, violations: 8 },
    { date: "Oct 31", requests: 700, violations: 7 },
  ],
  "HR": [
    { date: "Oct 24", requests: 250, violations: 5 },
    { date: "Oct 25", requests: 280, violations: 4 },
    { date: "Oct 26", requests: 260, violations: 3 },
    { date: "Oct 27", requests: 270, violations: 6 },
    { date: "Oct 28", requests: 290, violations: 4 },
    { date: "Oct 29", requests: 300, violations: 3 },
    { date: "Oct 30", requests: 310, violations: 4 },
    { date: "Oct 31", requests: 295, violations: 3 },
  ],
  "Finance": [
    { date: "Oct 24", requests: 320, violations: 4 },
    { date: "Oct 25", requests: 350, violations: 3 },
    { date: "Oct 26", requests: 380, violations: 5 },
    { date: "Oct 27", requests: 360, violations: 4 },
    { date: "Oct 28", requests: 400, violations: 6 },
    { date: "Oct 29", requests: 420, violations: 5 },
    { date: "Oct 30", requests: 450, violations: 3 },
    { date: "Oct 31", requests: 430, violations: 4 },
  ],
};

const modelVendorData = [
  { name: "OpenAI", value: 45, color: "#1E90FF" },
  { name: "Anthropic", value: 25, color: "#10B981" },
  { name: "Google", value: 15, color: "#F59E0B" },
  { name: "On-Prem", value: 10, color: "#8B5CF6" },
  { name: "Others", value: 5, color: "#6B7280" },
];

const recentEvents = [
  { 
    id: "evt-001",
    time: "14:32", 
    user: "john.doe@company.com", 
    model: "GPT-4", 
    policy: "PII Detection", 
    risk: "High",
    department: "Engineering",
    prompt: "Please analyze this customer data including SSN: 123-45-6789",
    action: "Blocked",
    ipAddress: "192.168.1.45"
  },
  { 
    id: "evt-002",
    time: "14:28", 
    user: "jane.smith@company.com", 
    model: "Claude-2", 
    policy: "Data Leak Prevention", 
    risk: "Critical",
    department: "Sales",
    prompt: "Here is our confidential pricing strategy...",
    action: "Blocked",
    ipAddress: "192.168.1.78"
  },
  { 
    id: "evt-003",
    time: "14:15", 
    user: "mike.johnson@company.com", 
    model: "On-Prem LLaMA", 
    policy: "Usage Limit", 
    risk: "Medium",
    department: "Marketing",
    prompt: "Generate 100 marketing slogans for our new product...",
    action: "Rate Limited",
    ipAddress: "192.168.1.92"
  },
  { 
    id: "evt-004",
    time: "14:05", 
    user: "sarah.williams@company.com", 
    model: "GPT-4", 
    policy: "Shadow AI Detection", 
    risk: "High",
    department: "HR",
    prompt: "Unauthorized use of personal OpenAI account detected",
    action: "Logged",
    ipAddress: "192.168.1.103"
  },
  { 
    id: "evt-005",
    time: "13:58", 
    user: "robert.brown@company.com", 
    model: "Gemini Pro", 
    policy: "Content Filter", 
    risk: "Low",
    department: "Finance",
    prompt: "Generate a financial report summary...",
    action: "Warned",
    ipAddress: "192.168.1.115"
  },
];

const heatmapData = [
  { hour: "00:00", Mon: 2, Tue: 1, Wed: 3, Thu: 2, Fri: 1, Sat: 0, Sun: 0 },
  { hour: "04:00", Mon: 1, Tue: 0, Wed: 1, Thu: 1, Fri: 0, Sat: 0, Sun: 0 },
  { hour: "08:00", Mon: 15, Tue: 18, Wed: 22, Thu: 19, Fri: 16, Sat: 3, Sun: 2 },
  { hour: "12:00", Mon: 28, Tue: 32, Wed: 35, Thu: 30, Fri: 25, Sat: 5, Sun: 4 },
  { hour: "16:00", Mon: 22, Tue: 25, Wed: 28, Thu: 24, Fri: 20, Sat: 2, Sun: 1 },
  { hour: "20:00", Mon: 8, Tue: 10, Wed: 12, Thu: 9, Fri: 15, Sat: 1, Sun: 1 },
];

// Shadow AI detail data for heatmap clicks
const shadowAIDetails = [
  { id: "s001", time: "08:15", day: "Mon", user: "user1@company.com", tool: "ChatGPT Personal", department: "Engineering", action: "Detected" },
  { id: "s002", time: "08:32", day: "Mon", user: "user2@company.com", tool: "Claude.ai", department: "Marketing", action: "Blocked" },
  { id: "s003", time: "12:20", day: "Wed", user: "user3@company.com", tool: "Gemini", department: "Sales", action: "Logged" },
  { id: "s004", time: "12:45", day: "Wed", user: "user4@company.com", tool: "ChatGPT Personal", department: "Engineering", action: "Detected" },
  { id: "s005", time: "16:10", day: "Thu", user: "user5@company.com", tool: "Perplexity", department: "HR", action: "Warned" },
];

interface WidgetItem {
  id: string;
  type: string;
  title: string;
}

interface SortableWidgetProps {
  id: string;
  children: React.ReactNode;
  onClick?: (event: React.MouseEvent) => void;
}

interface PopupState {
  type: string;
  data?: any;
  mousePosition?: { x: number; y: number };
}

function SortableWidget({ id, children, onClick }: SortableWidgetProps) {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
  };

  return (
    <div ref={setNodeRef} style={style} className="relative group">
      <div className="absolute top-2 right-2 z-10 opacity-0 group-hover:opacity-100 transition-opacity">
        <div
          {...attributes}
          {...listeners}
          className="cursor-grab active:cursor-grabbing bg-muted hover:bg-muted/80 p-1.5 rounded"
        >
          <GripVertical className="w-4 h-4 text-muted-foreground" />
        </div>
      </div>
      <div 
        onClick={(e) => {
          e.stopPropagation();
          onClick?.(e);
        }} 
        className={onClick ? "cursor-pointer h-full transition-all duration-200 hover:shadow-lg hover:-translate-y-1" : "h-full"}
      >
        {children}
      </div>
    </div>
  );
}

// Custom Tooltip for Department Usage
const DepartmentTooltip = ({ active, payload }: any) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload;
    return (
      <div className="bg-white border border-gray-300 rounded-lg p-4 shadow-lg">
        <p className="font-semibold mb-2">{data.department}</p>
        <div className="space-y-1">
          <p className="text-sm"><span className="inline-block w-3 h-3 rounded mr-2" style={{backgroundColor: "#1E90FF"}}></span>OpenAI: {data.OpenAI}</p>
          <p className="text-sm"><span className="inline-block w-3 h-3 rounded mr-2" style={{backgroundColor: "#10B981"}}></span>Anthropic: {data.Anthropic}</p>
          <p className="text-sm"><span className="inline-block w-3 h-3 rounded mr-2" style={{backgroundColor: "#F59E0B"}}></span>Google: {data.Google}</p>
          <p className="text-sm"><span className="inline-block w-3 h-3 rounded mr-2" style={{backgroundColor: "#8B5CF6"}}></span>On-Prem: {data.OnPrem}</p>
          <p className="text-sm"><span className="inline-block w-3 h-3 rounded mr-2" style={{backgroundColor: "#6B7280"}}></span>Others: {data.Others}</p>
          <p className="text-sm font-semibold mt-2 pt-2 border-t">Total: {data.total}</p>
        </div>
      </div>
    );
  }
  return null;
};

export function DashboardOverview() {
  // Filter state
  const [currentFilters, setCurrentFilters] = useState({
    year: '2025',
    month: '11',
    week: 'all'
  });
  const [kpiData, setKpiData] = useState(null);
  const [usersTrendData, setUsersTrendData] = useState([]);
  const [modelDistributionData, setModelDistributionData] = useState([]);
  const [departmentDistributionData, setDepartmentDistributionData] = useState([]);
  const [userStatistics, setUserStatistics] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const [selectedWidgets, setSelectedWidgets] = useState<string[]>([]);
  const [popupStates, setPopupStates] = useState<Record<string, PopupState>>({});
  const [topZIndex, setTopZIndex] = useState(1000);
  const [widgetZIndices, setWidgetZIndices] = useState<Record<string, number>>({});
  const [popupsVisible, setPopupsVisible] = useState(true);
  const [isMobile, setIsMobile] = useState(false);
  const [mobileDialogOpen, setMobileDialogOpen] = useState(false);
  const [mobileDialogContent, setMobileDialogContent] = useState<string | null>(null);
  const [widgets, setWidgets] = useState<WidgetItem[]>([
    { id: "kpi-4", type: "kpi", title: "AI Service Users" },
    { id: "kpi-1", type: "kpi", title: "Total AI Requests" },
    { id: "kpi-2", type: "kpi", title: "Policy Violations" },
    { id: "kpi-3", type: "kpi", title: "Shadow AI Detected" },
    { id: "usage-trend", type: "chart-top", title: "AI Usage Trend" },
    { id: "department", type: "chart-top", title: "Department Usage" },
    { id: "model-vendor", type: "chart-top", title: "Model Vendor Distribution" },
    { id: "recent-events", type: "chart-bottom", title: "Recent High-Risk Events" },
    { id: "heatmap", type: "chart-bottom", title: "Shadow AI Activity Heatmap" },
  ]);

  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );

  // Mobile detection
  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768); // md breakpoint
    };
    
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;

    if (over && active.id !== over.id) {
      setWidgets((items) => {
        const oldIndex = items.findIndex((item) => item.id === active.id);
        const newIndex = items.findIndex((item) => item.id === over.id);
        return arrayMove(items, oldIndex, newIndex);
      });
    }
  };

  const handleDepartmentClick = (department: string) => {
    const popupId = `department-trend-${department}`;
    if (!selectedWidgets.includes(popupId)) {
      setSelectedWidgets([...selectedWidgets, popupId]);
      setPopupStates({
        ...popupStates,
        [popupId]: { type: 'department-trend', data: { department } }
      });
      const newZIndex = topZIndex + 1;
      setWidgetZIndices({ ...widgetZIndices, [popupId]: newZIndex });
      setTopZIndex(newZIndex);
    }
    setPopupsVisible(true);
  };

  const handleEventClick = (event: any) => {
    const popupId = `event-detail-${event.id}`;
    if (!selectedWidgets.includes(popupId)) {
      setSelectedWidgets([...selectedWidgets, popupId]);
      setPopupStates({
        ...popupStates,
        [popupId]: { type: 'event-detail', data: { event } }
      });
      const newZIndex = topZIndex + 1;
      setWidgetZIndices({ ...widgetZIndices, [popupId]: newZIndex });
      setTopZIndex(newZIndex);
    }
    setPopupsVisible(true);
  };

  const handleHeatmapClick = (hour: string, day: string, count: number) => {
    const popupId = `shadow-ai-detail-${day}-${hour}`;
    if (!selectedWidgets.includes(popupId)) {
      setSelectedWidgets([...selectedWidgets, popupId]);
      setPopupStates({
        ...popupStates,
        [popupId]: { type: 'shadow-ai-detail', data: { hour, day, count } }
      });
      const newZIndex = topZIndex + 1;
      setWidgetZIndices({ ...widgetZIndices, [popupId]: newZIndex });
      setTopZIndex(newZIndex);
    }
    setPopupsVisible(true);
  };

  const renderWidgetContent = (widget: WidgetItem) => {
    switch (widget.id) {
      case "kpi-1":
        return (
          <KPICard
            title="Total AI Requests"
            value={kpiData?.totalAIRequests?.value || (isLoading ? "Loading..." : "28.4K")}
            icon={Activity}
            trend={kpiData?.totalAIRequests?.trend || { value: "12.5%", isPositive: true }}
            color="primary"
          />
        );
      case "kpi-2":
        return (
          <KPICard
            title="Policy Violations"
            value={kpiData?.policyViolations?.value || (isLoading ? "Loading..." : "342")}
            icon={AlertTriangle}
            trend={kpiData?.policyViolations?.trend || { value: "8.2%", isPositive: false }}
            color="destructive"
          />
        );
      case "kpi-3":
        return (
          <KPICard
            title="Shadow AI Detected"
            value={kpiData?.shadowAIDetected?.value || (isLoading ? "Loading..." : "28")}
            icon={Eye}
            trend={kpiData?.shadowAIDetected?.trend || { value: "15.3%", isPositive: false }}
            color="accent"
          />
        );
      case "kpi-4":
        return (
          <KPICard
            title="AI Service Users"
            value={kpiData?.aiServiceUsers?.value || (isLoading ? "Loading..." : "1,247")}
            icon={Users}
            trend={kpiData?.aiServiceUsers?.trend || { value: "34.8%", isPositive: true }}
            color="primary"
          />
        );
      case "usage-trend":
        return (
          <Card className="h-full">
            <CardHeader className="p-4 sm:p-6">
              <CardTitle className="text-base sm:text-lg">AI Usage Trend</CardTitle>
            </CardHeader>
            <CardContent className="p-4 sm:p-6">
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={dailyUsageData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                  <XAxis dataKey="date" stroke="#6B7280" tick={{ fontSize: 12 }} />
                  <YAxis stroke="#6B7280" tick={{ fontSize: 12 }} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#ffffff',
                      border: '1px solid #E5E7EB',
                      borderRadius: '8px'
                    }}
                  />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="requests"
                    stroke="#1E90FF"
                    strokeWidth={2}
                    name="Requests"
                  />
                  <Line
                    type="monotone"
                    dataKey="violations"
                    stroke="#EF4444"
                    strokeWidth={2}
                    name="Violations"
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        );
      case "department":
        return (
          <Card className="h-full">
            <CardHeader className="p-4 sm:p-6">
              <CardTitle className="text-base sm:text-lg">Department Usage</CardTitle>
            </CardHeader>
            <CardContent className="p-4 sm:p-6">
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={departmentDistributionData.length > 0 ? departmentDistributionData.map(item => ({
                  department: item.department,
                  total: item.total_requests || 0,
                  active_users: item.active_users || 0,
                  cost: item.total_cost || 0,
                  violations: item.violation_count || 0
                })) : departmentDataWithModels}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                  <XAxis dataKey="department" stroke="#6B7280" tick={{ fontSize: 12 }} />
                  <YAxis stroke="#6B7280" tick={{ fontSize: 12 }} />
                  <Tooltip content={<DepartmentTooltip />} />
                  <Bar 
                    dataKey={departmentDistributionData.length > 0 ? "total" : "OpenAI"}
                    stackId="a" 
                    fill="#1E90FF" 
                    radius={[0, 0, 0, 0]} 
                    cursor="pointer"
                    onClick={(data) => {
                      if (data && data.department) {
                        handleDepartmentClick(data.department);
                      }
                    }}
                  />
{departmentDistributionData.length === 0 && (
                  <Bar 
                    dataKey="Anthropic" 
                    stackId="a" 
                    fill="#10B981" 
                    radius={[0, 0, 0, 0]} 
                    cursor="pointer"
                    onClick={(data) => {
                      if (data && data.department) {
                        handleDepartmentClick(data.department);
                      }
                    }}
                  />
                  )}
                  {departmentDistributionData.length === 0 && (
                  <>
                  <Bar 
                    dataKey="Google" 
                    stackId="a" 
                    fill="#F59E0B" 
                    radius={[0, 0, 0, 0]} 
                    cursor="pointer"
                    onClick={(data) => {
                      if (data && data.department) {
                        handleDepartmentClick(data.department);
                      }
                    }}
                  />
                  <Bar 
                    dataKey="OnPrem" 
                    stackId="a" 
                    fill="#8B5CF6" 
                    radius={[0, 0, 0, 0]} 
                    cursor="pointer"
                    onClick={(data) => {
                      if (data && data.department) {
                        handleDepartmentClick(data.department);
                      }
                    }}
                  />
                  <Bar 
                    dataKey="Others" 
                    stackId="a" 
                    fill="#6B7280" 
                    radius={[8, 8, 0, 0]} 
                    cursor="pointer"
                    onClick={(data) => {
                      if (data && data.department) {
                        handleDepartmentClick(data.department);
                      }
                    }}
                  />
                  </>
                  )}
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        );
      case "model-vendor":
        return (
          <Card className="h-full">
            <CardHeader className="p-4 sm:p-6">
              <CardTitle className="text-base sm:text-lg">Model Vendor Distribution</CardTitle>
            </CardHeader>
            <CardContent className="flex justify-center p-4 sm:p-6">
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={modelDistributionData.length > 0 ? modelDistributionData.map((item, index) => ({
                      name: item.model_name,
                      value: item.user_count,
                      color: ["#1E90FF", "#10B981", "#F59E0B", "#8B5CF6", "#6B7280", "#EF4444", "#06B6D4", "#84CC16"][index % 8]
                    })) : modelVendorData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={100}
                    paddingAngle={2}
                    dataKey="value"
                    label={(entry) => `${entry.name} ${entry.value}${modelDistributionData.length > 0 ? '' : '%'}`}
                    isAnimationActive={false}
                  >
                    {(modelDistributionData.length > 0 ? modelDistributionData.map((item, index) => ({
                      color: ["#1E90FF", "#10B981", "#F59E0B", "#8B5CF6", "#6B7280", "#EF4444", "#06B6D4", "#84CC16"][index % 8]
                    })) : modelVendorData).map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        );
      case "recent-events":
        return (
          <Card className="h-full">
            <CardHeader className="p-4 sm:p-6">
              <CardTitle className="text-base sm:text-lg">Recent High-Risk Events</CardTitle>
            </CardHeader>
            <CardContent className="p-4 sm:p-6">
              <div className="space-y-2 sm:space-y-3">
                {recentEvents.map((event, idx) => (
                  <div
                    key={idx}
                    className="flex items-center justify-between p-2 sm:p-3 bg-muted/50 rounded-lg hover:bg-muted transition-colors cursor-pointer"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleEventClick(event);
                    }}
                  >
                    <div className="flex items-center gap-2 sm:gap-4 flex-1 min-w-0">
                      <span className="text-muted-foreground text-xs sm:text-sm min-w-[45px] sm:min-w-[50px]">{event.time}</span>
                      <span className="flex-1 truncate text-xs sm:text-sm">{event.user}</span>
                      <span className="text-muted-foreground text-xs sm:text-sm hidden md:inline">{event.model}</span>
                      <span className="text-muted-foreground text-xs sm:text-sm hidden lg:inline">{event.policy}</span>
                    </div>
                    <Badge
                      className={
                        event.risk === "Critical" ? "bg-[#EF4444]" :
                          event.risk === "High" ? "bg-[#F59E0B]" :
                            event.risk === "Medium" ? "bg-[#1E90FF]" :
                              "bg-[#6B7280]"
                      }
                    >
                      {event.risk}
                    </Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        );
      case "heatmap":
        return (
          <Card className="h-full">
            <CardHeader className="p-4 sm:p-6">
              <CardTitle className="text-base sm:text-lg">Shadow AI Activity Heatmap (by Hour)</CardTitle>
            </CardHeader>
            <CardContent className="p-4 sm:p-6">
              <div className="overflow-x-auto -mx-2 sm:mx-0">
                <table className="w-full min-w-[600px]">
                  <thead>
                    <tr>
                      <th className="text-left p-1 sm:p-2 text-xs sm:text-sm">Hour</th>
                      {["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"].map((day) => (
                        <th key={day} className="text-center p-1 sm:p-2 text-xs sm:text-sm">{day}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {heatmapData.map((row, idx) => (
                      <tr key={idx}>
                        <td className="p-1 sm:p-2 text-muted-foreground text-xs sm:text-sm">{row.hour}</td>
                        {["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"].map((day) => {
                          const value = row[day as keyof typeof row] as number;
                          const intensity = Math.min(value / 35, 1);
                          return (
                            <td key={day} className="p-0.5 sm:p-1">
                              <div
                                className="w-10 h-7 sm:w-12 sm:h-8 rounded flex items-center justify-center transition-all hover:scale-110 text-xs sm:text-sm cursor-pointer"
                                style={{
                                  backgroundColor: `rgba(30, 144, 255, ${intensity})`,
                                  color: intensity > 0.5 ? '#ffffff' : '#111827'
                                }}
                                title={`${day} ${row.hour}: ${value} detections`}
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleHeatmapClick(row.hour, day, value);
                                }}
                              >
                                {value}
                              </div>
                            </td>
                          );
                        })}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        );
      default:
        return null;
    }
  };

  const handleOpenWidget = (widgetId: string, event?: React.MouseEvent) => {
    if (!selectedWidgets.includes(widgetId)) {
      const mousePosition = event ? { x: event.clientX, y: event.clientY } : undefined;
      setSelectedWidgets([...selectedWidgets, widgetId]);
      setPopupStates({
        ...popupStates,
        [widgetId]: { type: 'widget', mousePosition }
      });
      const newZIndex = topZIndex + 1;
      setWidgetZIndices({ ...widgetZIndices, [widgetId]: newZIndex });
      setTopZIndex(newZIndex);
    }
    setPopupsVisible(true);
  };

  const handleCloseWidget = (widgetId: string) => {
    setSelectedWidgets(selectedWidgets.filter((id) => id !== widgetId));
    const newIndices = { ...widgetZIndices };
    delete newIndices[widgetId];
    setWidgetZIndices(newIndices);
    const newStates = { ...popupStates };
    delete newStates[widgetId];
    setPopupStates(newStates);
  };

  const bringToFront = (widgetId: string) => {
    const newZIndex = topZIndex + 1;
    setWidgetZIndices({ ...widgetZIndices, [widgetId]: newZIndex });
    setTopZIndex(newZIndex);
    setPopupsVisible(true);
  };

  const handleMainPageClick = () => {
    if (selectedWidgets.length > 0 && popupsVisible) {
      // 팝업을 숨기지 않고 모든 팝업을 뒤로 보내기
      const newIndices: Record<string, number> = {};
      selectedWidgets.forEach((widgetId, index) => {
        newIndices[widgetId] = 100 + index; // 낮은 z-index로 설정
      });
      setWidgetZIndices(newIndices);
      setTopZIndex(200); // 다음 클릭을 위한 기준 z-index 설정
      // setPopupsVisible(false); // 이 라인을 제거하여 팝업이 계속 보이도록 함
    }
  };

  // API 호출 함수
  const fetchKPIData = async (filters: { year: string; month: string; week: string }) => {
    setIsLoading(true);
    try {
      console.log('🔄 Fetching KPI data with filters:', filters);
      
      const queryParams = new URLSearchParams();
      if (filters.year !== 'all') queryParams.append('year', filters.year);
      if (filters.month !== 'all') queryParams.append('month', filters.month);
      if (filters.week !== 'all') queryParams.append('week', filters.week);

      const apiUrl = `http://localhost:3002/api/dashboard/kpi?${queryParams.toString()}`;
      console.log('📡 API URL:', apiUrl);
      
      const response = await fetch(apiUrl);
      console.log('📊 Response status:', response.status, response.statusText);
      
      const data = await response.json();
      console.log('📋 Raw API response:', data);
      
      if (data.success) {
        setKpiData(data.data);
        console.log('✅ KPI data updated successfully:', data.data);
        console.log('🔍 aiServiceUsers data:', data.data.aiServiceUsers);
        console.log('📅 Filter applied:', data.filter);
      } else {
        console.error('❌ API returned error:', data.error);
      }
    } catch (error) {
      console.error('🚨 Failed to fetch KPI data:', error);
      console.error('Error details:', error.message);
    } finally {
      setIsLoading(false);
    }
  };

  // 차트 데이터 API 호출 함수들
  const fetchChartData = async (filters: { year: string; month: string; week: string }) => {
    try {
      const queryParams = new URLSearchParams();
      if (filters.year !== 'all') queryParams.append('year', filters.year);
      if (filters.month !== 'all') queryParams.append('month', filters.month);
      if (filters.week !== 'all') queryParams.append('week', filters.week);

      const baseUrl = 'http://localhost:3002/api/dashboard';
      const queryString = queryParams.toString();

      // 동시에 4개 API 호출
      const [usersTrendResponse, modelDistResponse, deptDistResponse, userStatsResponse] = await Promise.all([
        fetch(`${baseUrl}/users-trend?${queryString}`),
        fetch(`${baseUrl}/model-distribution?${queryString}`),
        fetch(`${baseUrl}/department-distribution?${queryString}`),
        fetch(`${baseUrl}/user-statistics?${queryString}`)
      ]);

      const [usersTrendData, modelDistData, deptDistData, userStatsData] = await Promise.all([
        usersTrendResponse.json(),
        modelDistResponse.json(),
        deptDistResponse.json(),
        userStatsResponse.json()
      ]);

      if (usersTrendData.success) {
        setUsersTrendData(usersTrendData.data);
      }
      if (modelDistData.success) {
        setModelDistributionData(modelDistData.data);
      }
      if (deptDistData.success) {
        setDepartmentDistributionData(deptDistData.data);
      }
      if (userStatsData.success) {
        setUserStatistics(userStatsData.data);
      }

      console.log('Chart data updated:', { 
        usersTrend: usersTrendData.data?.length, 
        modelDist: modelDistData.data?.length, 
        deptDist: deptDistData.data?.length,
        userStats: userStatsData.success 
      });
    } catch (error) {
      console.error('Failed to fetch chart data:', error);
    }
  };

  // 필터 변경 핸들러
  const handleFilterChange = (filters: { year: string; month: string; week: string }) => {
    setCurrentFilters(filters);
    fetchKPIData(filters);
    fetchChartData(filters);
  };

  // 컴포넌트 마운트 시 초기 데이터 로드
  useEffect(() => {
    fetchKPIData(currentFilters);
    fetchChartData(currentFilters);
  }, []);

  const getInitialPosition = (index: number, widgetId?: string, popupState?: PopupState) => {
    const offset = index * 40;
    
    // KPI 위젯이고 마우스 위치가 있으면 마우스 클릭 위치 사용 (가로 중앙, 세로 마우스 위치)
    const widget = widgetId ? widgets.find((w) => w.id === widgetId) : null;
    const isKPIWidget = widget?.type === "kpi";
    
    if (isKPIWidget && popupState?.mousePosition) {
      // 전체 페이지 중앙 위치 (팝업 너비 862px, 높이 672px)
      const popupWidth = 862;
      const popupHeight = 672;
      // 화면 중앙보다 3cm(약 113px) 위에 배치
      return {
        x: Math.max(50, window.innerWidth / 2 - popupWidth / 2),
        y: Math.max(50, window.innerHeight / 2 - popupHeight / 2 - 113),
      };
    }
    
    // KPI 카드가 아닌 나머지 팝업들도 가로 중앙 배치
    // Department Trend, Event Detail, Shadow AI Detail, Chart 위젯 등
    const defaultSize = getDefaultSize(widgetId || '', popupState);
    const popupWidth = defaultSize.width;
    
    return {
      x: Math.max(50, window.innerWidth / 2 - popupWidth / 2),
      y: Math.max(50, window.innerHeight / 2 - 300 + offset),
    };
  };

  const getDefaultSize = (widgetId: string, popupState?: PopupState) => {
    if (popupState?.type === 'department-trend') {
      return { width: 1000, height: 700 };
    }
    if (popupState?.type === 'event-detail') {
      return { width: 900, height: 750 };
    }
    if (popupState?.type === 'shadow-ai-detail') {
      return { width: 1000, height: 700 };
    }

    const widget = widgets.find((w) => w.id === widgetId);
    if (!widget) return { width: 800, height: 600 };

    const isKPIWidget = widget.type === "kpi";
    const isChartWidget = widget.type === "chart-top";
    const isRecentEvents = widget.id === "recent-events";
    const isHeatmap = widget.id === "heatmap";

    if (isKPIWidget) {
      return { width: 862, height: 672 };
    } else if (isChartWidget || isHeatmap) {
      return { width: 1000, height: 700 };
    } else if (isRecentEvents) {
      return { width: 900, height: 650 };
    }
    return { width: 700, height: 600 };
  };

  const renderDetailedView = (widgetId: string, index: number) => {
    const popupState = popupStates[widgetId];
    if (!popupState) return null;

    // Department Trend Popup
    if (popupState.type === 'department-trend') {
      const { department } = popupState.data;
      const trendData = departmentDailyTrend[department] || [];
      const defaultSize = getDefaultSize(widgetId, popupState);
      const initialPosition = getInitialPosition(index, widgetId, popupState);
      const zIndex = widgetZIndices[widgetId] || 1000 + index;

      return createPortal(
        <Rnd
          key={widgetId}
          default={{
            x: initialPosition.x,
            y: initialPosition.y,
            width: defaultSize.width,
            height: defaultSize.height,
          }}
          minWidth={700}
          minHeight={500}
          dragHandleClassName="drag-handle"
          onMouseDown={(e) => {
            e.stopPropagation();
            bringToFront(widgetId);
          }}
          style={{
            position: 'fixed',
            zIndex: zIndex,
            display: popupsVisible ? 'block' : 'none',
          }}
        >
          <div 
            className="h-full w-full bg-background border-2 border-border rounded-lg shadow-2xl flex flex-col"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="drag-handle flex items-center justify-between p-4 border-b bg-muted cursor-move rounded-t-lg">
              <h2 className="text-xl font-semibold">AI Usage Trend - {department}</h2>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => handleCloseWidget(widgetId)}
                className="h-8 w-8 hover:bg-destructive hover:text-destructive-foreground"
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
            <div className="flex-1 overflow-y-auto p-6 space-y-6">
              <Card>
                <CardContent className="p-6">
                  <ResponsiveContainer width="100%" height={500}>
                    <LineChart data={trendData}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                      <XAxis dataKey="date" stroke="#6B7280" />
                      <YAxis stroke="#6B7280" />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: '#ffffff',
                          border: '1px solid #E5E7EB',
                          borderRadius: '8px'
                        }}
                      />
                      <Legend />
                      <Line
                        type="monotone"
                        dataKey="requests"
                        stroke="#1E90FF"
                        strokeWidth={3}
                        name="Requests"
                      />
                      <Line
                        type="monotone"
                        dataKey="violations"
                        stroke="#EF4444"
                        strokeWidth={3}
                        name="Violations"
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="p-4 bg-muted rounded-lg">
                  <p className="text-sm text-muted-foreground">Monthly Total</p>
                  <p className="text-3xl font-bold mt-1">{trendData.reduce((sum, d) => sum + d.requests, 0).toLocaleString()}</p>
                </div>
                <div className="p-4 bg-muted rounded-lg">
                  <p className="text-sm text-muted-foreground">Total Violations</p>
                  <p className="text-3xl font-bold mt-1 text-red-500">{trendData.reduce((sum, d) => sum + d.violations, 0)}</p>
                </div>
                <div className="p-4 bg-muted rounded-lg">
                  <p className="text-sm text-muted-foreground">Avg Daily</p>
                  <p className="text-3xl font-bold mt-1">{Math.round(trendData.reduce((sum, d) => sum + d.requests, 0) / trendData.length).toLocaleString()}</p>
                </div>
              </div>

              <div className="p-6 bg-muted rounded-lg">
                <h3 className="font-semibold mb-3 text-xl">Department Insights</h3>
                <div className="space-y-3">
                  <p className="text-muted-foreground">
                    • This department's AI usage patterns show {trendData[trendData.length - 1].requests > trendData[0].requests ? 'an increasing' : 'a decreasing'} trend over the selected period
                  </p>
                  <p className="text-muted-foreground">
                    • Violation rate: {((trendData.reduce((sum, d) => sum + d.violations, 0) / trendData.reduce((sum, d) => sum + d.requests, 0)) * 100).toFixed(1)}%
                  </p>
                  <p className="text-muted-foreground">
                    • Monitor high-risk activities and ensure policy compliance
                  </p>
                </div>
              </div>
            </div>
          </div>
        </Rnd>,
        document.body
      );
    }

    // Event Detail Popup
    if (popupState.type === 'event-detail') {
      const { event } = popupState.data;
      const defaultSize = getDefaultSize(widgetId, popupState);
      const initialPosition = getInitialPosition(index, widgetId, popupState);
      const zIndex = widgetZIndices[widgetId] || 1000 + index;

      return createPortal(
        <Rnd
          key={widgetId}
          default={{
            x: initialPosition.x,
            y: initialPosition.y,
            width: defaultSize.width,
            height: defaultSize.height,
          }}
          minWidth={700}
          minHeight={500}
          dragHandleClassName="drag-handle"
          onMouseDown={(e) => {
            e.stopPropagation();
            bringToFront(widgetId);
          }}
          style={{
            position: 'fixed',
            zIndex: zIndex,
            display: popupsVisible ? 'block' : 'none',
          }}
        >
          <div 
            className="h-full w-full bg-background border-2 border-border rounded-lg shadow-2xl flex flex-col"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="drag-handle flex items-center justify-between p-4 border-b bg-muted cursor-move rounded-t-lg">
              <h2 className="text-xl font-semibold">Event Detail - {event.id}</h2>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => handleCloseWidget(widgetId)}
                className="h-8 w-8 hover:bg-destructive hover:text-destructive-foreground"
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
            <div className="flex-1 overflow-y-auto p-6 space-y-6">
              {/* Summary Cards */}
              <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                <Card>
                  <CardContent className="p-4">
                    <div className="flex items-center gap-2 mb-2">
                      <Clock className="w-4 h-4 text-muted-foreground" />
                      <span className="text-sm text-muted-foreground">Time</span>
                    </div>
                    <p className="font-semibold">{event.time}</p>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="p-4">
                    <div className="flex items-center gap-2 mb-2">
                      <User className="w-4 h-4 text-muted-foreground" />
                      <span className="text-sm text-muted-foreground">Department</span>
                    </div>
                    <p className="font-semibold">{event.department}</p>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="p-4">
                    <div className="flex items-center gap-2 mb-2">
                      <Server className="w-4 h-4 text-muted-foreground" />
                      <span className="text-sm text-muted-foreground">Model</span>
                    </div>
                    <p className="font-semibold">{event.model}</p>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="p-4">
                    <div className="flex items-center gap-2 mb-2">
                      <AlertTriangle className="w-4 h-4 text-muted-foreground" />
                      <span className="text-sm text-muted-foreground">Risk Level</span>
                    </div>
                    <Badge
                      className={
                        event.risk === "Critical" ? "bg-[#EF4444]" :
                        event.risk === "High" ? "bg-[#F59E0B]" :
                        event.risk === "Medium" ? "bg-[#1E90FF]" :
                        "bg-[#6B7280]"
                      }
                    >
                      {event.risk}
                    </Badge>
                  </CardContent>
                </Card>
              </div>

              {/* Event Details */}
              <Card>
                <CardHeader>
                  <CardTitle>Event Information</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <p className="text-sm text-muted-foreground mb-1">User</p>
                    <p className="font-medium">{event.user}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground mb-1">Policy Violated</p>
                    <p className="font-medium">{event.policy}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground mb-1">Action Taken</p>
                    <Badge className="bg-[#1E90FF]">{event.action}</Badge>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground mb-1">IP Address</p>
                    <p className="font-mono text-sm">{event.ipAddress}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground mb-1">Prompt Content</p>
                    <div className="p-4 bg-muted rounded-lg">
                      <p className="text-sm font-mono">{event.prompt}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Recommendations */}
              <Card>
                <CardHeader>
                  <CardTitle>Recommendations</CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="list-disc list-inside space-y-2 text-sm text-muted-foreground">
                    <li>Review user training materials for PII handling</li>
                    <li>Consider implementing additional input validation</li>
                    <li>Monitor this user's future activity closely</li>
                    <li>Update security policies if necessary</li>
                  </ul>
                </CardContent>
              </Card>
            </div>
          </div>
        </Rnd>,
        document.body
      );
    }

    // Shadow AI Detail Popup
    if (popupState.type === 'shadow-ai-detail') {
      const { hour, day, count } = popupState.data;
      const filteredDetails = shadowAIDetails.filter(d => d.day === day);
      const defaultSize = getDefaultSize(widgetId, popupState);
      const initialPosition = getInitialPosition(index, widgetId, popupState);
      const zIndex = widgetZIndices[widgetId] || 1000 + index;

      return createPortal(
        <Rnd
          key={widgetId}
          default={{
            x: initialPosition.x,
            y: initialPosition.y,
            width: defaultSize.width,
            height: defaultSize.height,
          }}
          minWidth={700}
          minHeight={500}
          dragHandleClassName="drag-handle"
          onMouseDown={(e) => {
            e.stopPropagation();
            bringToFront(widgetId);
          }}
          style={{
            position: 'fixed',
            zIndex: zIndex,
            display: popupsVisible ? 'block' : 'none',
          }}
        >
          <div 
            className="h-full w-full bg-background border-2 border-border rounded-lg shadow-2xl flex flex-col"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="drag-handle flex items-center justify-between p-4 border-b bg-muted cursor-move rounded-t-lg">
              <h2 className="text-xl font-semibold">Shadow AI Detections - {day} {hour}</h2>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => handleCloseWidget(widgetId)}
                className="h-8 w-8 hover:bg-destructive hover:text-destructive-foreground"
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
            <div className="flex-1 overflow-y-auto p-6">
              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle>Detected Activities ({count} total)</CardTitle>
                    <Badge className="bg-[#1E90FF]">{day}</Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {filteredDetails.length > 0 ? (
                      filteredDetails.map((detail) => (
                        <div key={detail.id} className="p-4 bg-muted rounded-lg">
                          <div className="flex items-center justify-between mb-2">
                            <span className="font-semibold">{detail.user}</span>
                            <Badge
                              className={
                                detail.action === "Blocked" ? "bg-[#EF4444]" :
                                detail.action === "Warned" ? "bg-[#F59E0B]" :
                                "bg-[#1E90FF]"
                              }
                            >
                              {detail.action}
                            </Badge>
                          </div>
                          <div className="grid grid-cols-2 gap-2 text-sm">
                            <p><span className="text-muted-foreground">Time:</span> {detail.time}</p>
                            <p><span className="text-muted-foreground">Tool:</span> {detail.tool}</p>
                            <p><span className="text-muted-foreground">Department:</span> {detail.department}</p>
                          </div>
                        </div>
                      ))
                    ) : (
                      <p className="text-center text-muted-foreground py-8">
                        No detailed records available for this time slot
                      </p>
                    )}
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </Rnd>,
        document.body
      );
    }

    // Standard Widget Popup
    const widget = widgets.find((w) => w.id === widgetId);
    if (!widget) return null;

    const defaultSize = getDefaultSize(widgetId, popupState);
    const initialPosition = getInitialPosition(index, widgetId, popupState);
    const zIndex = widgetZIndices[widgetId] || 1000 + index;

    return createPortal(
      <Rnd
        key={widgetId}
        default={{
          x: initialPosition.x,
          y: initialPosition.y,
          width: defaultSize.width,
          height: defaultSize.height,
        }}
        minWidth={500}
        minHeight={400}
        dragHandleClassName="drag-handle"
        onMouseDown={(e) => {
          e.stopPropagation();
          bringToFront(widgetId);
        }}
        style={{
          position: 'fixed',
          zIndex: zIndex,
          display: popupsVisible ? 'block' : 'none',
        }}
      >
        <div 
          className="h-full w-full bg-background border-2 border-border rounded-lg shadow-2xl flex flex-col"
          onClick={(e) => e.stopPropagation()}
        >
          <div className="drag-handle flex items-center justify-between p-4 border-b bg-muted cursor-move rounded-t-lg">
            <h2 className="text-xl font-semibold">{widget.title} - Detailed View</h2>
            <Button
              variant="ghost"
              size="icon"
              onClick={() => handleCloseWidget(widgetId)}
              className="h-8 w-8 hover:bg-destructive hover:text-destructive-foreground"
            >
              <X className="h-4 w-4" />
            </Button>
          </div>

          <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {(widget.id === "usage-trend") && (
            <Card>
              <CardContent className="p-6">
                <ResponsiveContainer width="100%" height={500}>
                  <LineChart data={dailyUsageData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                    <XAxis dataKey="date" stroke="#6B7280" />
                    <YAxis stroke="#6B7280" />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#ffffff',
                        border: '1px solid #E5E7EB',
                        borderRadius: '8px'
                      }}
                    />
                    <Legend />
                    <Line
                      type="monotone"
                      dataKey="requests"
                      stroke="#1E90FF"
                      strokeWidth={3}
                      name="Requests"
                    />
                    <Line
                      type="monotone"
                      dataKey="violations"
                      stroke="#EF4444"
                      strokeWidth={3}
                      name="Violations"
                    />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          )}

          {(widget.id === "department") && (
            <Card>
              <CardContent className="p-6">
                <ResponsiveContainer width="100%" height={500}>
                  <BarChart data={departmentDistributionData.length > 0 ? departmentDistributionData.map(item => ({
                    department: item.department,
                    total: item.total_requests || 0,
                    active_users: item.active_users || 0,
                    cost: item.total_cost || 0,
                    violations: item.violation_count || 0
                  })) : departmentDataWithModels}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                    <XAxis dataKey="department" stroke="#6B7280" />
                    <YAxis stroke="#6B7280" />
                    <Tooltip content={<DepartmentTooltip />} />
                    <Legend />
                    <Bar dataKey={departmentDistributionData.length > 0 ? "total" : "OpenAI"} stackId="a" fill="#1E90FF" onClick={(data) => handleDepartmentClick(data.department)} cursor="pointer" />
                    {departmentDistributionData.length === 0 && (
                    <>
                    <Bar dataKey="Anthropic" stackId="a" fill="#10B981" onClick={(data) => handleDepartmentClick(data.department)} cursor="pointer" />
                    <Bar dataKey="Google" stackId="a" fill="#F59E0B" onClick={(data) => handleDepartmentClick(data.department)} cursor="pointer" />
                    <Bar dataKey="OnPrem" stackId="a" fill="#8B5CF6" onClick={(data) => handleDepartmentClick(data.department)} cursor="pointer" />
                    <Bar dataKey="Others" stackId="a" fill="#6B7280" radius={[8, 8, 0, 0]} onClick={(data) => handleDepartmentClick(data.department)} cursor="pointer" />
                    </>
                    )}
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          )}

          {(widget.id === "model-vendor") && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Card>
                <CardContent className="p-6 flex justify-center">
                  <ResponsiveContainer width="100%" height={400}>
                    <PieChart>
                      <Pie
                        data={modelDistributionData.length > 0 ? modelDistributionData.map((item, index) => ({
                          name: item.model_name,
                          value: item.user_count,
                          color: ["#1E90FF", "#10B981", "#F59E0B", "#8B5CF6", "#6B7280", "#EF4444", "#06B6D4", "#84CC16"][index % 8]
                        })) : modelVendorData}
                        cx="50%"
                        cy="50%"
                        innerRadius={80}
                        outerRadius={140}
                        paddingAngle={2}
                        dataKey="value"
                        label={(entry) => `${entry.name} ${entry.value}${modelDistributionData.length > 0 ? '' : '%'}`}
                        isAnimationActive={false}
                      >
                        {(modelDistributionData.length > 0 ? modelDistributionData.map((item, index) => ({
                          color: ["#1E90FF", "#10B981", "#F59E0B", "#8B5CF6", "#6B7280", "#EF4444", "#06B6D4", "#84CC16"][index % 8]
                        })) : modelVendorData).map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-6">
                  <div className="space-y-4">
                    <h4 className="font-semibold mb-4">Distribution Details</h4>
                    {(modelDistributionData.length > 0 ? modelDistributionData.map((item, index) => ({
                      name: item.model_name,
                      value: item.user_count,
                      sessions: item.session_count || 0,
                      requests: item.total_requests || 0,
                      cost: item.total_cost || 0,
                      color: ["#1E90FF", "#10B981", "#F59E0B", "#8B5CF6", "#6B7280", "#EF4444", "#06B6D4", "#84CC16"][index % 8]
                    })) : modelVendorData).map((vendor, idx) => (
                      <div key={idx} className="flex items-center justify-between p-4 bg-muted rounded-lg">
                        <div className="flex items-center gap-3">
                          <div className="w-6 h-6 rounded" style={{ backgroundColor: vendor.color }}></div>
                          <span className="font-medium">{vendor.name}</span>
                        </div>
                        <div className="text-right">
                          <p className="font-bold text-2xl">{vendor.value}{modelDistributionData.length > 0 ? '' : '%'}</p>
                          <p className="text-sm text-muted-foreground">
                            {modelDistributionData.length > 0 ? 'users' : 'of total usage'}
                            {vendor.sessions && ` | ${vendor.sessions} sessions`}
                          </p>
                          {vendor.cost && (
                            <p className="text-xs text-muted-foreground">${vendor.cost.toFixed(2)} cost</p>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          )}

          {(widget.id === "recent-events") && (
            <Card>
              <CardContent className="p-6">
                <div className="space-y-3">
                  {recentEvents.map((event, idx) => (
                    <div
                      key={idx}
                      className="flex items-center justify-between p-4 bg-muted/50 rounded-lg hover:bg-muted transition-colors cursor-pointer"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleEventClick(event);
                      }}
                    >
                      <div className="flex items-center gap-6 flex-1">
                        <span className="text-muted-foreground font-medium min-w-[60px]">{event.time}</span>
                        <div className="flex-1">
                          <p className="font-medium mb-1">{event.user}</p>
                          <p className="text-sm text-muted-foreground">{event.policy}</p>
                        </div>
                        <span className="text-muted-foreground font-medium">{event.model}</span>
                      </div>
                      <Badge
                        className={
                          event.risk === "Critical" ? "bg-[#EF4444] text-white" :
                          event.risk === "High" ? "bg-[#F59E0B] text-white" :
                          event.risk === "Medium" ? "bg-[#1E90FF] text-white" :
                          "bg-[#6B7280] text-white"
                        }
                      >
                        {event.risk}
                      </Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {(widget.id === "heatmap") && (
            <Card>
              <CardContent className="p-6">
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr>
                        <th className="text-left p-3">Hour</th>
                        {["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"].map((day) => (
                          <th key={day} className="text-center p-3">{day}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {heatmapData.map((row, idx) => (
                        <tr key={idx}>
                          <td className="p-3 text-muted-foreground font-medium">{row.hour}</td>
                          {["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"].map((day) => {
                            const value = row[day as keyof typeof row] as number;
                            const intensity = Math.min(value / 35, 1);
                            return (
                              <td key={day} className="p-2">
                                <div
                                  className="w-16 h-12 rounded-lg flex items-center justify-center font-bold transition-all hover:scale-110 cursor-pointer"
                                  style={{
                                    backgroundColor: `rgba(30, 144, 255, ${intensity})`,
                                    color: intensity > 0.5 ? '#ffffff' : '#111827'
                                  }}
                                  title={`${day} ${row.hour}: ${value} detections`}
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    handleHeatmapClick(row.hour, day, value);
                                  }}
                                >
                                  {value}
                                </div>
                              </td>
                            );
                          })}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          )}

          {widget.id === "kpi-1" && (
            <>
              <Card>
                <CardHeader>
                  <CardTitle>Total AI Requests Trend</CardTitle>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={dailyUsageData}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                      <XAxis dataKey="date" stroke="#6B7280" />
                      <YAxis stroke="#6B7280" />
                      <Tooltip />
                      <Legend />
                      <Line type="monotone" dataKey="requests" stroke="#1E90FF" strokeWidth={2} name="Requests" />
                    </LineChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Card>
                  <CardHeader>
                    <CardTitle className="text-base">Model Distribution</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
                        <span className="text-sm">OpenAI (GPT-4, GPT-3.5)</span>
                        <span className="font-bold">8,600 (42%)</span>
                      </div>
                      <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
                        <span className="text-sm">Anthropic (Claude)</span>
                        <span className="font-bold">5,700 (28%)</span>
                      </div>
                      <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
                        <span className="text-sm">Google (Gemini)</span>
                        <span className="font-bold">3,400 (17%)</span>
                      </div>
                      <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
                        <span className="text-sm">On-Prem LLM</span>
                        <span className="font-bold">1,700 (8%)</span>
                      </div>
                      <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
                        <span className="text-sm">Others</span>
                        <span className="font-bold">600 (3%)</span>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="text-base">Top Departments</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
                        <span className="text-sm">Engineering</span>
                        <span className="font-bold">8,500 requests</span>
                      </div>
                      <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
                        <span className="text-sm">Marketing</span>
                        <span className="font-bold">4,100 requests</span>
                      </div>
                      <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
                        <span className="text-sm">Sales</span>
                        <span className="font-bold">3,200 requests</span>
                      </div>
                      <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
                        <span className="text-sm">Finance</span>
                        <span className="font-bold">2,400 requests</span>
                      </div>
                      <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
                        <span className="text-sm">HR</span>
                        <span className="font-bold">1,800 requests</span>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="p-4 bg-muted rounded-lg">
                  <p className="text-sm text-muted-foreground">Daily Average</p>
                  <p className="text-3xl font-bold mt-1">2,857</p>
                </div>
                <div className="p-4 bg-muted rounded-lg">
                  <p className="text-sm text-muted-foreground">Weekly Total</p>
                  <p className="text-3xl font-bold mt-1">20.0K</p>
                </div>
                <div className="p-4 bg-muted rounded-lg">
                  <p className="text-sm text-muted-foreground">Peak Hour</p>
                  <p className="text-3xl font-bold mt-1">14:00-15:00</p>
                </div>
                <div className="p-4 bg-muted rounded-lg">
                  <p className="text-sm text-muted-foreground">Growth</p>
                  <p className="text-3xl font-bold mt-1 text-green-500">↑ 12.5%</p>
                </div>
              </div>
            </>
          )}

          {widget.id === "kpi-2" && (
            <>
              <Card>
                <CardHeader>
                  <CardTitle>Policy Violations by Severity</CardTitle>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={[
                      { severity: "Critical", count: 85, color: "#EF4444" },
                      { severity: "High", count: 52, color: "#F59E0B" },
                      { severity: "Medium", count: 28, color: "#1E90FF" },
                      { severity: "Low", count: 15, color: "#6B7280" }
                    ]}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                      <XAxis dataKey="severity" stroke="#6B7280" />
                      <YAxis stroke="#6B7280" />
                      <Tooltip />
                      <Bar dataKey="count" fill="#1E90FF" radius={[8, 8, 0, 0]}>
                        {[
                          { severity: "Critical", count: 85, color: "#EF4444" },
                          { severity: "High", count: 52, color: "#F59E0B" },
                          { severity: "Medium", count: 28, color: "#1E90FF" },
                          { severity: "Low", count: 15, color: "#6B7280" }
                        ].map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Card>
                  <CardHeader>
                    <CardTitle className="text-base">Top Policy Violations</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
                        <div>
                          <p className="text-sm font-medium">PII Detection</p>
                          <p className="text-xs text-muted-foreground">Personally Identifiable Info</p>
                        </div>
                        <Badge className="bg-[#EF4444]">85</Badge>
                      </div>
                      <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
                        <div>
                          <p className="text-sm font-medium">Data Leak Prevention</p>
                          <p className="text-xs text-muted-foreground">Sensitive Data Protection</p>
                        </div>
                        <Badge className="bg-[#EF4444]">67</Badge>
                      </div>
                      <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
                        <div>
                          <p className="text-sm font-medium">Confidential Info Filter</p>
                          <p className="text-xs text-muted-foreground">Company Confidential</p>
                        </div>
                        <Badge className="bg-[#F59E0B]">52</Badge>
                      </div>
                      <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
                        <div>
                          <p className="text-sm font-medium">Prompt Injection</p>
                          <p className="text-xs text-muted-foreground">Attack Detection</p>
                        </div>
                        <Badge className="bg-[#F59E0B]">38</Badge>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="text-base">Department Violations</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
                        <span className="text-sm">Engineering</span>
                        <span className="font-bold text-red-500">68 violations</span>
                      </div>
                      <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
                        <span className="text-sm">Marketing</span>
                        <span className="font-bold text-orange-500">45 violations</span>
                      </div>
                      <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
                        <span className="text-sm">Sales</span>
                        <span className="font-bold text-orange-500">32 violations</span>
                      </div>
                      <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
                        <span className="text-sm">Finance</span>
                        <span className="font-bold text-blue-500">22 violations</span>
                      </div>
                      <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
                        <span className="text-sm">HR</span>
                        <span className="font-bold text-blue-500">13 violations</span>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="p-4 bg-muted rounded-lg">
                  <p className="text-sm text-muted-foreground">Total Violations</p>
                  <p className="text-3xl font-bold mt-1 text-red-500">180</p>
                </div>
                <div className="p-4 bg-muted rounded-lg">
                  <p className="text-sm text-muted-foreground">Blocked</p>
                  <p className="text-3xl font-bold mt-1">152</p>
                </div>
                <div className="p-4 bg-muted rounded-lg">
                  <p className="text-sm text-muted-foreground">Warned</p>
                  <p className="text-3xl font-bold mt-1">28</p>
                </div>
                <div className="p-4 bg-muted rounded-lg">
                  <p className="text-sm text-muted-foreground">Trend</p>
                  <p className="text-3xl font-bold mt-1 text-green-500">↓ 8.2%</p>
                </div>
              </div>
            </>
          )}

          {widget.id === "kpi-3" && (
            <>
              <Card>
                <CardHeader>
                  <CardTitle>Shadow AI Detection Trend</CardTitle>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={[
                      { date: "Oct 24", detections: 3 },
                      { date: "Oct 25", detections: 4 },
                      { date: "Oct 26", detections: 2 },
                      { date: "Oct 27", detections: 5 },
                      { date: "Oct 28", detections: 6 },
                      { date: "Oct 29", detections: 4 },
                      { date: "Oct 30", detections: 4 }
                    ]}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                      <XAxis dataKey="date" stroke="#6B7280" />
                      <YAxis stroke="#6B7280" />
                      <Tooltip />
                      <Legend />
                      <Line type="monotone" dataKey="detections" stroke="#F59E0B" strokeWidth={2} name="Detections" />
                    </LineChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Card>
                  <CardHeader>
                    <CardTitle className="text-base">Detected Unauthorized Tools</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
                        <div>
                          <p className="text-sm font-medium">ChatGPT Plus (Personal)</p>
                          <p className="text-xs text-muted-foreground">Unauthorized OpenAI</p>
                        </div>
                        <Badge className="bg-[#EF4444]">12 users</Badge>
                      </div>
                      <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
                        <div>
                          <p className="text-sm font-medium">Claude.ai (Personal)</p>
                          <p className="text-xs text-muted-foreground">Unauthorized Anthropic</p>
                        </div>
                        <Badge className="bg-[#F59E0B]">8 users</Badge>
                      </div>
                      <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
                        <div>
                          <p className="text-sm font-medium">Midjourney (Personal)</p>
                          <p className="text-xs text-muted-foreground">Image Generation</p>
                        </div>
                        <Badge className="bg-[#F59E0B]">5 users</Badge>
                      </div>
                      <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
                        <div>
                          <p className="text-sm font-medium">Other Tools</p>
                          <p className="text-xs text-muted-foreground">Various</p>
                        </div>
                        <Badge className="bg-[#1E90FF]">3 users</Badge>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="text-base">Risk Assessment</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div>
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-sm">Data Leak Risk</span>
                          <Badge className="bg-[#EF4444]">High</Badge>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div className="bg-[#EF4444] h-2 rounded-full" style={{ width: "75%" }}></div>
                        </div>
                      </div>
                      <div>
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-sm">Compliance Risk</span>
                          <Badge className="bg-[#F59E0B]">Medium</Badge>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div className="bg-[#F59E0B] h-2 rounded-full" style={{ width: "60%" }}></div>
                        </div>
                      </div>
                      <div>
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-sm">Cost Impact</span>
                          <Badge className="bg-[#1E90FF]">Low</Badge>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div className="bg-[#1E90FF] h-2 rounded-full" style={{ width: "30%" }}></div>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="p-4 bg-muted rounded-lg">
                  <p className="text-sm text-muted-foreground">Total Users</p>
                  <p className="text-3xl font-bold mt-1 text-orange-500">28</p>
                </div>
                <div className="p-4 bg-muted rounded-lg">
                  <p className="text-sm text-muted-foreground">Unique Tools</p>
                  <p className="text-3xl font-bold mt-1">12</p>
                </div>
                <div className="p-4 bg-muted rounded-lg">
                  <p className="text-sm text-muted-foreground">This Week</p>
                  <p className="text-3xl font-bold mt-1">28</p>
                </div>
                <div className="p-4 bg-muted rounded-lg">
                  <p className="text-sm text-muted-foreground">Trend</p>
                  <p className="text-3xl font-bold mt-1 text-red-500">↑ 15.3%</p>
                </div>
              </div>
            </>
          )}

          {widget.id === "kpi-4" && (
            <>
              <Card>
                <CardHeader>
                  <CardTitle>AI Service Users Trend</CardTitle>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    {(() => {
                      const chartData = usersTrendData.length > 0 ? usersTrendData.map(item => ({
                        date: item.date_label,
                        users: parseInt(item.active_users)
                      })) : [
                        { date: "Oct 24", users: 1120 },
                        { date: "Oct 25", users: 1145 },
                        { date: "Oct 26", users: 1178 },
                        { date: "Oct 27", users: 1195 },
                        { date: "Oct 28", users: 1210 },
                        { date: "Oct 29", users: 1230 },
                        { date: "Oct 30", users: 1247 }
                      ];
                      
                      const maxUsers = Math.max(...chartData.map(d => d.users));
                      const yAxisMax = Math.ceil(maxUsers * 1.2);
                      
                      return (
                        <LineChart data={chartData}>
                          <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                          <XAxis dataKey="date" stroke="#6B7280" />
                          <YAxis stroke="#6B7280" domain={[0, yAxisMax]} />
                          <Tooltip />
                          <Legend />
                          <Line type="monotone" dataKey="users" stroke="#1E90FF" strokeWidth={2} name="Active Users" />
                        </LineChart>
                      );
                    })()}
                  </ResponsiveContainer>
                </CardContent>
              </Card>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Card>
                  <CardHeader>
                    <CardTitle className="text-base">Model-wise User Distribution</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {(modelDistributionData.length > 0 ? modelDistributionData : [
                        { model_name: "GPT-4", user_count: "678", total_requests: "12400" },
                        { model_name: "Claude 3", user_count: "523", total_requests: "9800" },
                        { model_name: "Gemini Pro", user_count: "412", total_requests: "7200" },
                        { model_name: "On-Prem LLM", user_count: "389", total_requests: "6100" }
                      ]).map((model, index) => {
                        const totalUsers = modelDistributionData.length > 0 
                          ? modelDistributionData.reduce((sum, m) => sum + parseInt(m.user_count), 0)
                          : 2002;
                        const usageRate = totalUsers > 0 
                          ? ((parseInt(model.user_count) / totalUsers) * 100).toFixed(1)
                          : "0.0";
                        
                        return (
                          <div key={index} className="flex items-center justify-between p-3 bg-muted rounded-lg">
                            <div>
                              <p className="text-sm font-medium">{model.model_name}</p>
                              <p className="text-xs text-muted-foreground">{usageRate}% usage rate</p>
                            </div>
                            <div className="text-right">
                              <p className="text-sm font-bold">{model.user_count} users</p>
                              {model.total_requests && (
                                <p className="text-xs text-muted-foreground">{parseInt(model.total_requests).toLocaleString()} reqs</p>
                              )}
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="text-base">Department Distribution</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {(departmentDistributionData.length > 0 ? departmentDistributionData : [
                        { department: "Engineering", active_users: "425" },
                        { department: "Marketing", active_users: "312" },
                        { department: "Sales", active_users: "268" },
                        { department: "Others", active_users: "242" }
                      ]).map((dept, index) => {
                        const colors = ["#10B981", "#1E90FF", "#8B5CF6", "#F59E0B", "#EF4444", "#06B6D4"];
                        const totalUsers = departmentDistributionData.length > 0 
                          ? departmentDistributionData.reduce((sum, d) => sum + parseInt(d.active_users || d.total_users || 0), 0)
                          : 1247;
                        const userCount = parseInt(dept.active_users || dept.total_users || 0);
                        const percentage = totalUsers > 0 
                          ? Math.round((userCount / totalUsers) * 100)
                          : 0;
                        
                        return (
                          <div key={index}>
                            <div className="flex items-center justify-between mb-2">
                              <span className="text-sm">{dept.department}</span>
                              <span className="text-sm font-bold">{userCount} users ({percentage}%)</span>
                            </div>
                            <div className="w-full bg-gray-200 rounded-full h-2">
                              <div 
                                className="h-2 rounded-full" 
                                style={{ 
                                  width: `${percentage}%`, 
                                  backgroundColor: colors[index % colors.length] 
                                }}
                              ></div>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </CardContent>
                </Card>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="p-4 bg-muted rounded-lg">
                  <p className="text-sm text-muted-foreground">Total Users</p>
                  <p className="text-3xl font-bold mt-1">
                    {userStatistics?.totalUsers?.value || "3,580"}
                  </p>
                </div>
                <div className="p-4 bg-muted rounded-lg">
                  <p className="text-sm text-muted-foreground">AI Service Users</p>
                  <p className="text-3xl font-bold mt-1">
                    {userStatistics?.aiServiceUsers?.value || "1,247"}
                  </p>
                </div>
                <div className="p-4 bg-muted rounded-lg">
                  <p className="text-sm text-muted-foreground">Adoption Rate</p>
                  <p className={`text-3xl font-bold mt-1 ${
                    userStatistics?.adoptionRate?.isPositive ? 'text-green-500' : 'text-red-500'
                  }`}>
                    {userStatistics?.adoptionRate?.value || "34.8%"}
                  </p>
                </div>
                <div className="p-4 bg-muted rounded-lg">
                  <p className="text-sm text-muted-foreground">Growth</p>
                  <p className={`text-3xl font-bold mt-1 ${
                    userStatistics?.growth?.isPositive ? 'text-green-500' : 'text-red-500'
                  }`}>
                    {userStatistics?.growth?.value || "↑ 34.8%"}
                  </p>
                </div>
              </div>
            </>
          )}

          {!widget.id.startsWith("kpi") && (
            <div className="p-6 bg-muted rounded-lg">
              <h3 className="font-semibold mb-3 text-xl">Insights & Recommendations</h3>
              <div className="space-y-3">
                <p className="text-muted-foreground">
                  • This metric shows detailed patterns in your AI usage and governance
                </p>
                <p className="text-muted-foreground">
                  • Use this data to optimize policies and improve security posture
                </p>
                <p className="text-muted-foreground">
                  • Export functionality available for further analysis
                </p>
              </div>
            </div>
          )}
          </div>
        </div>
      </Rnd>,
      document.body
    );
  };

  const kpiWidgets = widgets.filter((w) => w.type === "kpi");
  const chartTopWidgets = widgets.filter((w) => w.type === "chart-top");
  const chartBottomWidgets = widgets.filter((w) => w.type === "chart-bottom");

  return (
    <div 
      className="space-y-4 sm:space-y-6 p-3 sm:p-4 md:p-6 w-full max-w-full overflow-x-hidden"
      onClick={handleMainPageClick}
    >
      {/* Global Filters */}
      <FilterBar onFilterChange={handleFilterChange} />
      
      {/* Page Title */}
      <div>
        <h1 className="text-xl sm:text-2xl">AI Dashboard</h1>
        <p className="text-muted-foreground mt-1 text-sm sm:text-base">
          Comprehensive dashboard for monitoring AI usage, security violations, and system performance
        </p>
      </div>

      <DndContext
        sensors={sensors}
        collisionDetection={closestCenter}
        onDragEnd={handleDragEnd}
      >
        <SortableContext items={widgets.map((w) => w.id)} strategy={rectSortingStrategy}>
          {/* KPI Cards - 4 items on top */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4 md:gap-6">
            {kpiWidgets.map((widget) => (
              <SortableWidget
                key={widget.id}
                id={widget.id}
                onClick={isMobile ? undefined : (e) => handleOpenWidget(widget.id, e)}
              >
                {renderWidgetContent(widget)}
              </SortableWidget>
            ))}
          </div>

          {/* Top Charts - 3 items */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-3 sm:gap-4 md:gap-6">
            {chartTopWidgets.map((widget) => (
              <SortableWidget
                key={widget.id}
                id={widget.id}
                onClick={isMobile || widget.id === "department" ? undefined : (e) => handleOpenWidget(widget.id, e)}
              >
                {renderWidgetContent(widget)}
              </SortableWidget>
            ))}
          </div>

          {/* Bottom Charts - 2 items */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-3 sm:gap-4 md:gap-6">
            {chartBottomWidgets.map((widget) => (
              <SortableWidget
                key={widget.id}
                id={widget.id}
                onClick={undefined}
              >
                {renderWidgetContent(widget)}
              </SortableWidget>
            ))}
          </div>
        </SortableContext>
      </DndContext>

      {/* Render all popups */}
      {!isMobile && selectedWidgets.map((widgetId, index) => renderDetailedView(widgetId, index))}
    </div>
  );
}
