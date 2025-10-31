import { DollarSign, MessageSquare, Zap } from "lucide-react";
import { KPICard } from "../KPICard";
import { Card, CardContent, CardHeader, CardTitle } from "../ui/card";
import { Badge } from "../ui/badge";
import { ComposedChart, Line, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "../ui/table";

const tokenCostData = [
  { date: "Oct 24", tokens: 2500000, cost: 125 },
  { date: "Oct 25", tokens: 3200000, cost: 160 },
  { date: "Oct 26", tokens: 3800000, cost: 190 },
  { date: "Oct 27", tokens: 3500000, cost: 175 },
  { date: "Oct 28", tokens: 4200000, cost: 210 },
  { date: "Oct 29", tokens: 4800000, cost: 240 },
  { date: "Oct 30", tokens: 5100000, cost: 255 },
  { date: "Oct 31", tokens: 4900000, cost: 245 },
];

const userUsageData = [
  { 
    user: "john.doe@company.com", 
    department: "Engineering", 
    model: "GPT-4", 
    requests: 1250, 
    tokens: "2.5M", 
    cost: "$125" 
  },
  { 
    user: "jane.smith@company.com", 
    department: "Sales", 
    model: "Claude-2", 
    requests: 980, 
    tokens: "1.8M", 
    cost: "$90" 
  },
  { 
    user: "mike.johnson@company.com", 
    department: "Engineering", 
    model: "GPT-4", 
    requests: 850, 
    tokens: "1.5M", 
    cost: "$75" 
  },
  { 
    user: "sarah.williams@company.com", 
    department: "Marketing", 
    model: "Gemini Pro", 
    requests: 720, 
    tokens: "1.2M", 
    cost: "$48" 
  },
  { 
    user: "robert.brown@company.com", 
    department: "Finance", 
    model: "GPT-3.5", 
    requests: 650, 
    tokens: "950K", 
    cost: "$19" 
  },
  { 
    user: "emily.davis@company.com", 
    department: "HR", 
    model: "Claude-2", 
    requests: 580, 
    tokens: "890K", 
    cost: "$45" 
  },
  { 
    user: "david.wilson@company.com", 
    department: "Engineering", 
    model: "On-Prem LLaMA", 
    requests: 520, 
    tokens: "1.1M", 
    cost: "$0" 
  },
  { 
    user: "lisa.anderson@company.com", 
    department: "Sales", 
    model: "GPT-4", 
    requests: 480, 
    tokens: "820K", 
    cost: "$41" 
  },
];

export function PromptUsage() {
  return (
    <div className="space-y-6 p-6">
      {/* Page Title */}
      <div>
        <h1>Prompt Usage Statistics</h1>
        <p className="text-muted-foreground mt-1">
          Track AI usage, token consumption, and cost analysis across your organization
        </p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <KPICard
          title="Total Prompts"
          value="34.2K"
          icon={MessageSquare}
          trend={{ value: "18.4%", isPositive: true }}
          color="primary"
        />
        <KPICard
          title="Token Usage"
          value="28.5M"
          icon={Zap}
          trend={{ value: "22.1%", isPositive: true }}
          color="secondary"
        />
        <KPICard
          title="Estimated Cost"
          value="$1,425"
          icon={DollarSign}
          trend={{ value: "15.8%", isPositive: false }}
          color="accent"
        />
      </div>

      {/* Filter Chips */}
      <div className="flex gap-2 flex-wrap">
        <Badge variant="outline" className="cursor-pointer hover:bg-accent hover:text-accent-foreground">
          All Departments
        </Badge>
        <Badge variant="outline" className="cursor-pointer hover:bg-accent hover:text-accent-foreground">
          All Models
        </Badge>
        <Badge variant="outline" className="cursor-pointer hover:bg-accent hover:text-accent-foreground">
          Last 7 Days
        </Badge>
        <Badge className="bg-[#1E90FF] cursor-pointer">
          Engineering
        </Badge>
        <Badge variant="outline" className="cursor-pointer hover:bg-accent hover:text-accent-foreground">
          Clear Filters
        </Badge>
      </div>

      {/* Token vs Cost Chart */}
      <Card>
        <CardHeader>
          <CardTitle>Token Usage vs Cost Trend</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={400}>
            <ComposedChart data={tokenCostData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
              <XAxis dataKey="date" stroke="#6B7280" />
              <YAxis yAxisId="left" stroke="#6B7280" />
              <YAxis yAxisId="right" orientation="right" stroke="#6B7280" />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#ffffff', 
                  border: '1px solid #E5E7EB',
                  borderRadius: '8px'
                }}
              />
              <Legend />
              <Bar 
                yAxisId="left"
                dataKey="tokens" 
                fill="#1E90FF" 
                radius={[8, 8, 0, 0]}
                name="Tokens"
              />
              <Line 
                yAxisId="right"
                type="monotone" 
                dataKey="cost" 
                stroke="#F59E0B" 
                strokeWidth={3}
                name="Cost ($)"
              />
            </ComposedChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* User Usage Table */}
      <Card>
        <CardHeader>
          <CardTitle>User Usage Details</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>User</TableHead>
                <TableHead>Department</TableHead>
                <TableHead>Model</TableHead>
                <TableHead className="text-right">Requests</TableHead>
                <TableHead className="text-right">Tokens</TableHead>
                <TableHead className="text-right">Cost</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {userUsageData.map((user, idx) => (
                <TableRow key={idx} className="hover:bg-muted/50">
                  <TableCell>{user.user}</TableCell>
                  <TableCell>
                    <Badge variant="outline">{user.department}</Badge>
                  </TableCell>
                  <TableCell>
                    <Badge 
                      className={
                        user.model.includes("GPT") ? "bg-[#10B981]" :
                        user.model.includes("Claude") ? "bg-[#F59E0B]" :
                        user.model.includes("Gemini") ? "bg-[#1E90FF]" :
                        "bg-[#8B5CF6]"
                      }
                    >
                      {user.model}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-right">{user.requests.toLocaleString()}</TableCell>
                  <TableCell className="text-right">{user.tokens}</TableCell>
                  <TableCell className="text-right">{user.cost}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
