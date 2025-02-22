
import { useState } from "react";
import { ArrowLeft, Brain, User2, MessageSquare } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

type Message = {
  agent: "optimist" | "skeptic";
  content: string;
  timestamp: Date;
};

// Mock debate data
const initialMessages: Message[] = [
  {
    agent: "optimist",
    content: "The rapid advancement of AI technology presents unprecedented opportunities for solving global challenges. We're seeing breakthroughs in healthcare, climate science, and education that were unimaginable just a few years ago.",
    timestamp: new Date("2024-03-15T10:00:00"),
  },
  {
    agent: "skeptic",
    content: "While technological progress is valuable, we must carefully consider the societal implications. AI systems often perpetuate existing biases and could exacerbate inequality if not properly regulated.",
    timestamp: new Date("2024-03-15T10:01:00"),
  },
  {
    agent: "optimist",
    content: "But proper regulation doesn't mean hindering progress. We can develop AI responsibly while maintaining innovation. Look at how AI is already helping to detect diseases earlier and make education more accessible.",
    timestamp: new Date("2024-03-15T10:02:00"),
  },
  {
    agent: "skeptic",
    content: "Accessibility is important, but we can't ignore the potential job displacement and privacy concerns. We need robust frameworks to ensure AI benefits everyone, not just a select few.",
    timestamp: new Date("2024-03-15T10:03:00"),
  },
];

export default function Debate() {
  const navigate = useNavigate();
  const [messages] = useState<Message[]>(initialMessages);

  const MessageBubble = ({ message }: { message: Message }) => {
    const isOptimist = message.agent === "optimist";
    
    return (
      <div className={`flex ${isOptimist ? "justify-start" : "justify-end"} mb-4`}>
        <div className={`flex gap-3 max-w-[80%] ${isOptimist ? "flex-row" : "flex-row-reverse"}`}>
          <div className={`flex h-8 w-8 shrink-0 select-none items-center justify-center rounded-full ${
            isOptimist ? "bg-emerald-500" : "bg-blue-500"
          }`}>
            <Brain className="h-4 w-4 text-white" />
          </div>
          <div className={`flex flex-col ${isOptimist ? "items-start" : "items-end"}`}>
            <Badge variant="secondary" className="mb-2">
              {isOptimist ? "Optimist Agent" : "Skeptic Agent"}
            </Badge>
            <Card>
              <CardContent className="p-3">
                <p className="text-sm">{message.content}</p>
              </CardContent>
            </Card>
            <span className="mt-1 text-xs text-muted-foreground">
              {message.timestamp.toLocaleTimeString()}
            </span>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-background p-4 sm:p-6 md:p-8">
      <div className="mx-auto max-w-4xl">
        <button
          onClick={() => navigate(-1)}
          className="mb-6 flex items-center gap-2 text-muted-foreground hover:text-foreground"
        >
          <ArrowLeft className="h-5 w-5" />
          <span>Back</span>
        </button>

        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <MessageSquare className="h-5 w-5" />
              AI Debate: The Impact of Artificial Intelligence
            </CardTitle>
            <CardDescription>
              Watch as two AI agents debate the implications of artificial intelligence on society
            </CardDescription>
          </CardHeader>
        </Card>

        <div className="grid grid-cols-1 gap-4 lg:grid-cols-[1fr_300px]">
          <Card className="h-[calc(100vh-16rem)]">
            <ScrollArea className="h-full p-4">
              {messages.map((message, index) => (
                <MessageBubble key={index} message={message} />
              ))}
            </ScrollArea>
          </Card>

          <div className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Debate Participants</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center gap-2">
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-emerald-500">
                    <User2 className="h-4 w-4 text-white" />
                  </div>
                  <div>
                    <p className="text-sm font-medium">Optimist Agent</p>
                    <p className="text-xs text-muted-foreground">Focuses on opportunities</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-blue-500">
                    <User2 className="h-4 w-4 text-white" />
                  </div>
                  <div>
                    <p className="text-sm font-medium">Skeptic Agent</p>
                    <p className="text-xs text-muted-foreground">Raises concerns</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
