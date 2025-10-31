import { Plus, Search } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "../ui/card";
import { Badge } from "../ui/badge";
import { Button } from "../ui/button";
import { Input } from "../ui/input";
import { Avatar, AvatarFallback } from "../ui/avatar";

const cases = {
  new: [
    {
      id: "CASE-2401",
      title: "Unauthorized Claude API Usage",
      severity: "Critical",
      assignee: "JD",
      department: "Engineering",
      created: "2 hours ago",
      description: "Multiple unauthorized API calls detected from engineering department"
    },
    {
      id: "CASE-2402",
      title: "PII Leak in Prompt",
      severity: "High",
      assignee: "SM",
      department: "Sales",
      created: "4 hours ago",
      description: "Customer social security numbers found in AI prompts"
    },
    {
      id: "CASE-2403",
      title: "Excessive Token Usage",
      severity: "Medium",
      assignee: "MJ",
      department: "Marketing",
      created: "1 day ago",
      description: "User exceeded monthly token quota by 300%"
    },
  ],
  inProgress: [
    {
      id: "CASE-2398",
      title: "Shadow AI - LM Studio Detection",
      severity: "High",
      assignee: "RB",
      department: "Engineering",
      created: "2 days ago",
      description: "Local LLM instances detected on 5 engineering workstations"
    },
    {
      id: "CASE-2399",
      title: "Policy Violation - Code Exposure",
      severity: "High",
      assignee: "ED",
      department: "Engineering",
      created: "2 days ago",
      description: "Proprietary code shared with external AI service"
    },
    {
      id: "CASE-2400",
      title: "NSFW Content Generation",
      severity: "Medium",
      assignee: "DW",
      department: "Marketing",
      created: "3 days ago",
      description: "Inappropriate image generation attempts blocked"
    },
  ],
  completed: [
    {
      id: "CASE-2395",
      title: "Data Leak Investigation",
      severity: "Critical",
      assignee: "LA",
      department: "Finance",
      created: "5 days ago",
      description: "Financial data exposure resolved and user trained"
    },
    {
      id: "CASE-2396",
      title: "Quota Policy Update",
      severity: "Low",
      assignee: "SW",
      department: "HR",
      created: "6 days ago",
      description: "Department-wide token limits adjusted"
    },
    {
      id: "CASE-2397",
      title: "Model Access Review",
      severity: "Medium",
      assignee: "JD",
      department: "Sales",
      created: "7 days ago",
      description: "Sales team GPT-4 access permissions reviewed and updated"
    },
  ],
};

function CaseCard({ case: caseItem }: { case: typeof cases.new[0] }) {
  return (
    <Card className="hover:shadow-md transition-shadow cursor-pointer">
      <CardContent className="p-4">
        <div className="space-y-3">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-1">
                <span className="text-sm text-muted-foreground">{caseItem.id}</span>
                <Badge 
                  className={
                    caseItem.severity === "Critical" ? "bg-[#EF4444]" :
                    caseItem.severity === "High" ? "bg-[#F59E0B]" :
                    caseItem.severity === "Medium" ? "bg-[#1E90FF]" :
                    "bg-[#6B7280]"
                  }
                >
                  {caseItem.severity}
                </Badge>
              </div>
              <h4 className="mb-2">{caseItem.title}</h4>
              <p className="text-sm text-muted-foreground mb-3">
                {caseItem.description}
              </p>
            </div>
          </div>
          
          <div className="flex items-center justify-between pt-3 border-t border-border">
            <div className="flex items-center gap-2">
              <Avatar className="h-6 w-6">
                <AvatarFallback className="text-xs bg-[#1E90FF] text-white">
                  {caseItem.assignee}
                </AvatarFallback>
              </Avatar>
              <span className="text-sm text-muted-foreground">{caseItem.assignee}</span>
            </div>
            <div className="flex items-center gap-2">
              <Badge variant="outline">{caseItem.department}</Badge>
              <span className="text-sm text-muted-foreground">{caseItem.created}</span>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

export function CaseManagement() {
  return (
    <div className="space-y-6 p-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1>Case Management</h1>
          <p className="text-muted-foreground mt-1">
            Track and manage security incidents and policy violations
          </p>
        </div>
        <Button className="bg-[#1E90FF] hover:bg-[#1E90FF]/90">
          <Plus className="w-4 h-4 mr-2" />
          New Case
        </Button>
      </div>

      {/* Search and Filters */}
      <div className="flex gap-3">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <Input 
            placeholder="Search cases..." 
            className="pl-10 bg-input-background"
          />
        </div>
        <Button variant="outline">All Severities</Button>
        <Button variant="outline">All Departments</Button>
        <Button variant="outline">All Assignees</Button>
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardContent className="p-4">
            <div className="text-2xl mb-1">{cases.new.length}</div>
            <div className="text-muted-foreground">New Cases</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="text-2xl mb-1">{cases.inProgress.length}</div>
            <div className="text-muted-foreground">In Progress</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="text-2xl mb-1">{cases.completed.length}</div>
            <div className="text-muted-foreground">Completed</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="text-2xl mb-1">
              {cases.new.length + cases.inProgress.length + cases.completed.length}
            </div>
            <div className="text-muted-foreground">Total Cases</div>
          </CardContent>
        </Card>
      </div>

      {/* Kanban Board */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* New */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <h3>New</h3>
            <Badge className="bg-[#EF4444]">{cases.new.length}</Badge>
          </div>
          <div className="space-y-3">
            {cases.new.map((caseItem) => (
              <CaseCard key={caseItem.id} case={caseItem} />
            ))}
          </div>
        </div>

        {/* In Progress */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <h3>In Progress</h3>
            <Badge className="bg-[#F59E0B]">{cases.inProgress.length}</Badge>
          </div>
          <div className="space-y-3">
            {cases.inProgress.map((caseItem) => (
              <CaseCard key={caseItem.id} case={caseItem} />
            ))}
          </div>
        </div>

        {/* Completed */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <h3>Completed</h3>
            <Badge className="bg-[#10B981]">{cases.completed.length}</Badge>
          </div>
          <div className="space-y-3">
            {cases.completed.map((caseItem) => (
              <CaseCard key={caseItem.id} case={caseItem} />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
