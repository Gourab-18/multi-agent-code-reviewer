import { Shield, Zap, Search, User, CheckCircle } from "lucide-react";
import { clsx } from "clsx";

interface AgentAvatarProps {
    agent: string;
    className?: string;
    showName?: boolean;
}

export function AgentAvatar({ agent, className, showName = false }: AgentAvatarProps) {
    const normAgent = agent.toLowerCase();

    let icon = <User className="w-5 h-5" />;
    let color = "bg-gray-500";
    let label = "Agent";

    if (normAgent.includes("security")) {
        icon = <Shield className="w-5 h-5" />;
        color = "bg-red-600";
        label = "Security Agent";
    } else if (normAgent.includes("performance")) {
        icon = <Zap className="w-5 h-5" />;
        color = "bg-purple-600";
        label = "Performance Agent";
    } else if (normAgent.includes("quality")) {
        icon = <CheckCircle className="w-5 h-5" />;
        color = "bg-green-600";
        label = "Quality Agent";
    } else if (normAgent.includes("orchestrator")) {
        icon = <Search className="w-5 h-5" />;
        color = "bg-blue-600";
        label = "Orchestrator";
    }

    return (
        <div className="flex items-center gap-2">
            <div className={clsx("p-2 rounded-full text-white shadow-sm", color, className)}>
                {icon}
            </div>
            {showName && <span className="font-medium text-sm">{label}</span>}
        </div>
    );
}
