import { Server, Cpu, Clock, AlertCircle } from "lucide-react";
import { KPICard } from "../KPICard";
import { Card, CardContent, CardHeader, CardTitle } from "../ui/card";
import { Badge } from "../ui/badge";
import { Progress } from "../ui/progress";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "../ui/table";

const models = [
  { 
    name: "LLaMA-2-70B", 
    requests: 12450, 
    avgLatency: 245, 
    errorRate: 0.8, 
    gpuUsage: 85,
    status: "healthy"
  },
  { 
    name: "Mistral-7B", 
    requests: 8920, 
    avgLatency: 125, 
    errorRate: 0.3, 
    gpuUsage: 45,
    status: "healthy"
  },
  { 
    name: "CodeLLaMA-34B", 
    requests: 5680, 
    avgLatency: 380, 
    errorRate: 1.2, 
    gpuUsage: 72,
    status: "warning"
  },
  { 
    name: "Falcon-40B", 
    requests: 4230, 
    avgLatency: 420, 
    errorRate: 2.5, 
    gpuUsage: 88,
    status: "critical"
  },
  { 
    name: "MPT-30B", 
    requests: 3540, 
    avgLatency: 290, 
    errorRate: 0.9, 
    gpuUsage: 58,
    status: "healthy"
  },
];

const gpuServers = [
  { server: "GPU-Node-01", gpus: "4x A100", usage: 85, temp: 72, memory: 78, status: "healthy" },
  { server: "GPU-Node-02", gpus: "4x A100", usage: 72, temp: 68, memory: 65, status: "healthy" },
  { server: "GPU-Node-03", gpus: "4x A100", usage: 92, temp: 78, memory: 88, status: "warning" },
  { server: "GPU-Node-04", gpus: "4x A100", usage: 68, temp: 65, memory: 62, status: "healthy" },
];

export function OnPremLLM() {
  const avgGpuUsage = gpuServers.reduce((acc, s) => acc + s.usage, 0) / gpuServers.length;
  const avgLatency = models.reduce((acc, m) => acc + m.avgLatency, 0) / models.length;
  const successRate = 100 - (models.reduce((acc, m) => acc + m.errorRate, 0) / models.length);

  return (
    <div className="space-y-6 p-6">
      {/* Page Title */}
      <div>
        <h1>On-Premise LLM Monitoring</h1>
        <p className="text-muted-foreground mt-1">
          Monitor performance, resource usage, and health of your on-premise LLM infrastructure
        </p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <KPICard
          title="Average GPU Usage"
          value={`${avgGpuUsage.toFixed(1)}%`}
          icon={Cpu}
          trend={{ value: "5.2%", isPositive: true }}
          color="primary"
        />
        <KPICard
          title="Average Latency"
          value={`${avgLatency.toFixed(0)}ms`}
          icon={Clock}
          trend={{ value: "12.3%", isPositive: false }}
          color="accent"
        />
        <KPICard
          title="Success Rate"
          value={`${successRate.toFixed(1)}%`}
          icon={Server}
          trend={{ value: "2.1%", isPositive: true }}
          color="secondary"
        />
      </div>

      {/* GPU Performance Gauges */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>GPU Utilization</CardTitle>
          </CardHeader>
          <CardContent className="flex flex-col items-center justify-center py-8">
            <div className="relative w-48 h-48">
              <svg className="w-full h-full transform -rotate-90">
                <circle
                  cx="96"
                  cy="96"
                  r="80"
                  stroke="#E5E7EB"
                  strokeWidth="16"
                  fill="none"
                />
                <circle
                  cx="96"
                  cy="96"
                  r="80"
                  stroke="#1E90FF"
                  strokeWidth="16"
                  fill="none"
                  strokeDasharray={`${(avgGpuUsage / 100) * 502.4} 502.4`}
                  className="transition-all duration-500"
                />
              </svg>
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className="text-4xl">{avgGpuUsage.toFixed(0)}%</span>
                <span className="text-muted-foreground">Average</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Response Time</CardTitle>
          </CardHeader>
          <CardContent className="flex flex-col items-center justify-center py-8">
            <div className="relative w-48 h-48">
              <svg className="w-full h-full transform -rotate-90">
                <circle
                  cx="96"
                  cy="96"
                  r="80"
                  stroke="#E5E7EB"
                  strokeWidth="16"
                  fill="none"
                />
                <circle
                  cx="96"
                  cy="96"
                  r="80"
                  stroke={avgLatency > 400 ? "#EF4444" : avgLatency > 300 ? "#F59E0B" : "#10B981"}
                  strokeWidth="16"
                  fill="none"
                  strokeDasharray={`${Math.min((avgLatency / 500) * 502.4, 502.4)} 502.4`}
                  className="transition-all duration-500"
                />
              </svg>
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className="text-4xl">{avgLatency.toFixed(0)}</span>
                <span className="text-muted-foreground">ms</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Success Rate</CardTitle>
          </CardHeader>
          <CardContent className="flex flex-col items-center justify-center py-8">
            <div className="relative w-48 h-48">
              <svg className="w-full h-full transform -rotate-90">
                <circle
                  cx="96"
                  cy="96"
                  r="80"
                  stroke="#E5E7EB"
                  strokeWidth="16"
                  fill="none"
                />
                <circle
                  cx="96"
                  cy="96"
                  r="80"
                  stroke="#10B981"
                  strokeWidth="16"
                  fill="none"
                  strokeDasharray={`${(successRate / 100) * 502.4} 502.4`}
                  className="transition-all duration-500"
                />
              </svg>
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className="text-4xl">{successRate.toFixed(1)}%</span>
                <span className="text-muted-foreground">Uptime</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Model Performance Table */}
      <Card>
        <CardHeader>
          <CardTitle>Model Performance Metrics</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Model Name</TableHead>
                <TableHead className="text-right">Requests</TableHead>
                <TableHead className="text-right">Avg Latency</TableHead>
                <TableHead className="text-right">Error Rate</TableHead>
                <TableHead className="text-right">GPU Usage</TableHead>
                <TableHead>Status</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {models.map((model, idx) => (
                <TableRow key={idx} className="hover:bg-muted/50">
                  <TableCell>{model.name}</TableCell>
                  <TableCell className="text-right">{model.requests.toLocaleString()}</TableCell>
                  <TableCell className="text-right">
                    <span className={
                      model.avgLatency > 400 ? "text-[#EF4444]" :
                      model.avgLatency > 300 ? "text-[#F59E0B]" :
                      "text-[#10B981]"
                    }>
                      {model.avgLatency}ms
                      {model.avgLatency > 400 && " ⚠️"}
                    </span>
                  </TableCell>
                  <TableCell className="text-right">
                    <span className={model.errorRate > 2 ? "text-[#EF4444]" : "text-foreground"}>
                      {model.errorRate}%
                      {model.errorRate > 2 && " ⚠️"}
                    </span>
                  </TableCell>
                  <TableCell className="text-right">{model.gpuUsage}%</TableCell>
                  <TableCell>
                    <Badge 
                      className={
                        model.status === "critical" ? "bg-[#EF4444]" :
                        model.status === "warning" ? "bg-[#F59E0B]" :
                        "bg-[#10B981]"
                      }
                    >
                      {model.status}
                    </Badge>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* GPU Server Status */}
      <Card>
        <CardHeader>
          <CardTitle>GPU Server Status</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-6">
            {gpuServers.map((server, idx) => (
              <div key={idx} className="space-y-3 p-4 border border-border rounded-lg">
                <div className="flex items-center justify-between">
                  <div>
                    <h4>{server.server}</h4>
                    <p className="text-muted-foreground">{server.gpus}</p>
                  </div>
                  <Badge 
                    className={
                      server.status === "critical" ? "bg-[#EF4444]" :
                      server.status === "warning" ? "bg-[#F59E0B]" :
                      "bg-[#10B981]"
                    }
                  >
                    {server.status}
                  </Badge>
                </div>
                
                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm text-muted-foreground">Usage</span>
                      <span className="text-sm">{server.usage}%</span>
                    </div>
                    <Progress value={server.usage} className="h-2" />
                  </div>
                  
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm text-muted-foreground">Temperature</span>
                      <span className="text-sm">{server.temp}°C</span>
                    </div>
                    <Progress 
                      value={server.temp} 
                      className="h-2"
                    />
                  </div>
                  
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm text-muted-foreground">Memory</span>
                      <span className="text-sm">{server.memory}%</span>
                    </div>
                    <Progress value={server.memory} className="h-2" />
                  </div>
                </div>

                {server.usage > 90 && (
                  <div className="flex items-start gap-2 p-3 bg-[#F59E0B]/10 border border-[#F59E0B]/20 rounded">
                    <AlertCircle className="w-4 h-4 text-[#F59E0B] mt-0.5" />
                    <p className="text-sm text-[#F59E0B]">
                      High GPU utilization detected. Consider load balancing.
                    </p>
                  </div>
                )}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
