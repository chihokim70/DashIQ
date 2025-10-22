import * as React from "react"
import { cn } from "./utils"

const Sidebar = ({ children }: { children: React.ReactNode }) => {
  return <div className="flex h-full w-64 flex-col border-r bg-background">{children}</div>
}

const SidebarContent = ({ children }: { children: React.ReactNode }) => {
  return <div className="flex-1 overflow-auto">{children}</div>
}

const SidebarHeader = ({ children }: { children: React.ReactNode }) => {
  return <div className="p-4">{children}</div>
}

const SidebarFooter = ({ children }: { children: React.ReactNode }) => {
  return <div className="p-4">{children}</div>
}

const SidebarGroup = ({ children }: { children: React.ReactNode }) => {
  return <div className="p-2">{children}</div>
}

const SidebarGroupLabel = ({ children }: { children: React.ReactNode }) => {
  return <div className="px-2 py-1 text-xs font-medium text-muted-foreground">{children}</div>
}

const SidebarGroupContent = ({ children }: { children: React.ReactNode }) => {
  return <div className="space-y-1">{children}</div>
}

const SidebarMenu = ({ children }: { children: React.ReactNode }) => {
  return <div className="space-y-1">{children}</div>
}

const SidebarMenuItem = ({ children }: { children: React.ReactNode }) => {
  return <div>{children}</div>
}

const SidebarMenuButton = React.forwardRef<
  HTMLButtonElement,
  React.ButtonHTMLAttributes<HTMLButtonElement> & {
    isActive?: boolean
  }
>(({ className, isActive, ...props }, ref) => (
  <button
    ref={ref}
    className={cn(
      "flex w-full items-center rounded-md px-3 py-2 text-sm font-medium transition-colors hover:bg-accent hover:text-accent-foreground",
      isActive && "bg-accent text-accent-foreground",
      className
    )}
    {...props}
  />
))
SidebarMenuButton.displayName = "SidebarMenuButton"

export {
  Sidebar,
  SidebarContent,
  SidebarHeader,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupLabel,
  SidebarGroupContent,
  SidebarMenu,
  SidebarMenuItem,
  SidebarMenuButton,
}