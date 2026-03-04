"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { LayoutDashboard, Users, UserX, Settings, LogOut, Video } from "lucide-react";
import { cn } from "@/lib/utils";
import { useAuth } from "@/context/AuthContext";

const navItems = [
    { href: "/", icon: LayoutDashboard, label: "Dashboard" },
    { href: "/faces", icon: Users, label: "Trusted Faces" },
    { href: "/missing", icon: UserX, label: "Missing/Wanted" },
    { href: "/settings", icon: Settings, label: "System Settings" },
];

export function Sidebar() {
    const pathname = usePathname();
    const { logout } = useAuth();

    return (
        <div className="flex flex-col h-screen w-64 border-r border-border bg-card/50 backdrop-blur-xl fixed left-0 top-0 z-50">
            {/* Header */}
            <div className="p-6 flex items-center space-x-2 border-b border-border/50">
                <div className="w-8 h-8 bg-primary/20 rounded-md flex items-center justify-center text-primary border border-primary/50">
                    <Video className="w-5 h-5" />
                </div>
                <div>
                    <h1 className="font-bold text-lg tracking-wider text-foreground">SMART CCTV</h1>
                </div>
            </div>

            {/* Navigation */}
            <nav className="flex-1 p-4 space-y-2">
                {navItems.map((item) => {
                    const isActive = pathname === item.href;
                    return (
                        <Link
                            key={item.href}
                            href={item.href}
                            className={cn(
                                "flex items-center space-x-3 px-4 py-3 rounded-lg text-sm font-medium transition-all duration-200",
                                isActive
                                    ? "bg-primary/10 text-primary border border-primary/20 shadow-[0_0_15px_-5px_var(--color-primary)]"
                                    : "text-muted-foreground hover:bg-muted hover:text-foreground"
                            )}
                        >
                            <item.icon className={cn("w-5 h-5", isActive && "animate-pulse")} />
                            <span>{item.label}</span>
                        </Link>
                    );
                })}
            </nav>

            {/* Logout */}
            <div className="p-4 border-t border-border/50">
                <button
                    onClick={logout}
                    className="flex w-full items-center space-x-3 px-4 py-3 rounded-lg text-sm font-medium text-red-400 hover:bg-red-500/10 hover:text-red-300 transition-all duration-200"
                >
                    <LogOut className="w-5 h-5" />
                    <span>Logout</span>
                </button>
            </div>
        </div>
    );
}
