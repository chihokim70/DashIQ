import { Image, Eye, AlertTriangle } from "lucide-react";
import { KPICard } from "../KPICard";
import { Card, CardContent, CardHeader, CardTitle } from "../ui/card";
import { Badge } from "../ui/badge";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";

const departmentData = [
  { department: "Marketing", generated: 1250, nsfw: 12, flagged: 8 },
  { department: "Design", generated: 980, nsfw: 3, flagged: 2 },
  { department: "Engineering", generated: 420, nsfw: 1, flagged: 1 },
  { department: "Sales", generated: 350, nsfw: 5, flagged: 4 },
  { department: "HR", generated: 180, nsfw: 0, flagged: 0 },
];

const recentImages = [
  { id: 1, prompt: "Modern office workspace with...", model: "DALL-E 3", user: "john.doe", department: "Marketing", nsfw: false, blur: true },
  { id: 2, prompt: "Product showcase design for...", model: "Stable Diffusion XL", user: "jane.smith", department: "Design", nsfw: false, blur: true },
  { id: 3, prompt: "Technical diagram showing...", model: "Midjourney", user: "mike.johnson", department: "Engineering", nsfw: false, blur: true },
  { id: 4, prompt: "Marketing banner with brand...", model: "DALL-E 3", user: "sarah.williams", department: "Marketing", nsfw: false, blur: true },
  { id: 5, prompt: "Team photo concept for...", model: "Stable Diffusion", user: "robert.brown", department: "HR", nsfw: false, blur: true },
  { id: 6, prompt: "Data visualization chart...", model: "DALL-E 3", user: "emily.davis", department: "Engineering", nsfw: false, blur: true },
  { id: 7, prompt: "Social media post design...", model: "Midjourney", user: "david.wilson", department: "Marketing", nsfw: false, blur: true },
  { id: 8, prompt: "Product mockup for client...", model: "Stable Diffusion XL", user: "lisa.anderson", department: "Design", nsfw: false, blur: true },
];

const flaggedImages = [
  { time: "14:28", user: "user1@company.com", prompt: "Inappropriate content request...", reason: "NSFW content detected", severity: "Critical" },
  { time: "12:15", user: "user2@company.com", prompt: "Violent imagery request...", reason: "Violence filter triggered", severity: "High" },
  { time: "10:42", user: "user3@company.com", prompt: "Brand logo misuse attempt...", reason: "Copyright violation", severity: "Medium" },
  { time: "09:18", user: "user4@company.com", prompt: "Sensitive political content...", reason: "Policy violation", severity: "High" },
];

export function ImageGeneration() {
  return (
    <div className="space-y-6 p-6">
      {/* Page Title */}
      <div>
        <h1>Image Generation Monitoring</h1>
        <p className="text-muted-foreground mt-1">
          Track AI-generated images, detect policy violations, and monitor NSFW content
        </p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <KPICard
          title="Total Images Generated"
          value="3,180"
          icon={Image}
          trend={{ value: "24.3%", isPositive: true }}
          color="primary"
        />
        <KPICard
          title="NSFW Detections"
          value="21"
          icon={Eye}
          trend={{ value: "12.5%", isPositive: false }}
          color="destructive"
        />
        <KPICard
          title="Flagged Content"
          value="15"
          icon={AlertTriangle}
          trend={{ value: "8.7%", isPositive: false }}
          color="accent"
        />
      </div>

      {/* Department Usage Chart */}
      <Card>
        <CardHeader>
          <CardTitle>Image Generation by Department</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={departmentData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
              <XAxis dataKey="department" stroke="#6B7280" />
              <YAxis stroke="#6B7280" />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#ffffff', 
                  border: '1px solid #E5E7EB',
                  borderRadius: '8px'
                }}
              />
              <Legend />
              <Bar dataKey="generated" fill="#1E90FF" radius={[8, 8, 0, 0]} name="Generated" />
              <Bar dataKey="nsfw" fill="#EF4444" radius={[8, 8, 0, 0]} name="NSFW" />
              <Bar dataKey="flagged" fill="#F59E0B" radius={[8, 8, 0, 0]} name="Flagged" />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Model Filter */}
      <div className="flex gap-2 flex-wrap">
        <Badge className="bg-[#1E90FF] cursor-pointer">All Models</Badge>
        <Badge variant="outline" className="cursor-pointer hover:bg-accent hover:text-accent-foreground">
          DALL-E 3
        </Badge>
        <Badge variant="outline" className="cursor-pointer hover:bg-accent hover:text-accent-foreground">
          Stable Diffusion
        </Badge>
        <Badge variant="outline" className="cursor-pointer hover:bg-accent hover:text-accent-foreground">
          Midjourney
        </Badge>
        <Badge variant="outline" className="cursor-pointer hover:bg-accent hover:text-accent-foreground">
          Stable Diffusion XL
        </Badge>
      </div>

      {/* Recent Generated Images */}
      <Card>
        <CardHeader>
          <CardTitle>Recently Generated Images</CardTitle>
          <p className="text-sm text-muted-foreground mt-1">
            Images are blurred for privacy protection. Click to review.
          </p>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {recentImages.map((image) => (
              <div 
                key={image.id}
                className="group relative aspect-square bg-gradient-to-br from-muted to-muted/50 rounded-lg overflow-hidden cursor-pointer hover:ring-2 hover:ring-primary transition-all"
              >
                {/* Blurred placeholder */}
                <div className="absolute inset-0 flex items-center justify-center backdrop-blur-2xl bg-muted/80">
                  <Eye className="w-8 h-8 text-muted-foreground group-hover:text-primary transition-colors" />
                </div>
                
                {/* Image info overlay */}
                <div className="absolute bottom-0 left-0 right-0 p-3 bg-gradient-to-t from-black/80 to-transparent">
                  <p className="text-white text-xs truncate mb-1">{image.prompt}</p>
                  <div className="flex items-center justify-between">
                    <Badge className="bg-[#1E90FF] text-xs">{image.model}</Badge>
                    {image.nsfw && (
                      <Badge className="bg-[#EF4444] text-xs">NSFW</Badge>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Flagged Content */}
      <Card>
        <CardHeader>
          <CardTitle>Flagged & NSFW Content</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {flaggedImages.map((item, idx) => (
              <div 
                key={idx}
                className="flex items-start gap-4 p-4 bg-[#EF4444]/10 border border-[#EF4444]/20 rounded-lg"
              >
                <AlertTriangle className="w-5 h-5 text-[#EF4444] mt-0.5" />
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-muted-foreground">{item.time}</span>
                    <span>•</span>
                    <span>{item.user}</span>
                  </div>
                  <p className="mb-1 truncate">{item.prompt}</p>
                  <p className="text-muted-foreground">{item.reason}</p>
                </div>
                <Badge 
                  className={
                    item.severity === "Critical" ? "bg-[#EF4444]" :
                    item.severity === "High" ? "bg-[#F59E0B]" :
                    "bg-[#1E90FF]"
                  }
                >
                  {item.severity}
                </Badge>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Statistics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Most Used Model</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span>DALL-E 3</span>
                <span>1,450 images</span>
              </div>
              <div className="flex items-center justify-between text-muted-foreground">
                <span>Stable Diffusion XL</span>
                <span>980 images</span>
              </div>
              <div className="flex items-center justify-between text-muted-foreground">
                <span>Midjourney</span>
                <span>520 images</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Top Generators</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span>john.doe@company.com</span>
                <span>342</span>
              </div>
              <div className="flex items-center justify-between text-muted-foreground">
                <span>jane.smith@company.com</span>
                <span>285</span>
              </div>
              <div className="flex items-center justify-between text-muted-foreground">
                <span>mike.johnson@company.com</span>
                <span>218</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Content Safety</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span>Safe Content</span>
                <span className="text-[#10B981]">99.3%</span>
              </div>
              <div className="flex items-center justify-between">
                <span>NSFW Detected</span>
                <span className="text-[#EF4444]">0.7%</span>
              </div>
              <div className="flex items-center justify-between">
                <span>Auto-blocked</span>
                <span className="text-[#F59E0B]">15 requests</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
