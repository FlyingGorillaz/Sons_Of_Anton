
import { useState, useEffect } from "react";
import { Settings, X } from "lucide-react";
import Sidebar from "@/components/Sidebar";
import NewsCard from "@/components/NewsCard";

// Mock data for demonstration
const mockNews = [
  {
    id: 1,
    title: "Global Climate Summit Reaches Historic Agreement",
    summary: "World leaders have agreed to unprecedented measures to combat climate change in a landmark decision at the latest climate summit.",
    brands: ["BBC", "Reuters", "AP"],
    timestamp: "2 hours ago",
    category: "Environment",
    image: "https://images.unsplash.com/photo-1488590528505-98d2b5aba04b?w=800&auto=format&fit=crop&q=60"
  },
  {
    id: 2,
    title: "Tech Innovation Breakthrough in Renewable Energy",
    summary: "Scientists announce a revolutionary breakthrough in solar panel efficiency, potentially transforming the renewable energy landscape.",
    brands: ["TechCrunch", "Wired", "The Verge"],
    timestamp: "4 hours ago",
    category: "Technology",
    image: "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?w=800&auto=format&fit=crop&q=60"
  },
  {
    id: 3,
    title: "Major Economic Policy Shift Announced",
    summary: "Central banks worldwide coordinate on new economic measures aimed at stabilizing global markets and promoting sustainable growth.",
    brands: ["Bloomberg", "Financial Times", "WSJ"],
    timestamp: "6 hours ago",
    category: "Economy",
    image: "https://images.unsplash.com/photo-1487058792275-0ad4aaf24ca7?w=800&auto=format&fit=crop&q=60"
  },
];

export default function Index() {
  const [selectedCategory, setSelectedCategory] = useState("for you");
  const [showDebug, setShowDebug] = useState(true);
  const [logs, setLogs] = useState<string[]>([]);
  const categories = [
    "for you",
    "all",
    "technology",
    "politics",
    "environment",
    "economy",
    "culture",
    "science",
    "health",
    "sports",
    "entertainment",
    "business",
    "education",
    "travel",
    "food",
    "lifestyle"
  ];

  useEffect(() => {
    const originalConsoleLog = console.log;
    const originalConsoleError = console.error;
    const originalConsoleWarn = console.warn;

    function handleLog(...args: any[]) {
      const logMessage = args.map(arg => 
        typeof arg === 'object' ? JSON.stringify(arg) : String(arg)
      ).join(' ');
      
      setLogs(prevLogs => [...prevLogs, `[LOG] ${logMessage}`]);
      originalConsoleLog.apply(console, args);
    }

    function handleError(...args: any[]) {
      const logMessage = args.map(arg => 
        typeof arg === 'object' ? JSON.stringify(arg) : String(arg)
      ).join(' ');
      
      setLogs(prevLogs => [...prevLogs, `[ERROR] ${logMessage}`]);
      originalConsoleError.apply(console, args);
    }

    function handleWarn(...args: any[]) {
      const logMessage = args.map(arg => 
        typeof arg === 'object' ? JSON.stringify(arg) : String(arg)
      ).join(' ');
      
      setLogs(prevLogs => [...prevLogs, `[WARN] ${logMessage}`]);
      originalConsoleWarn.apply(console, args);
    }

    console.log = handleLog;
    console.error = handleError;
    console.warn = handleWarn;

    return () => {
      console.log = originalConsoleLog;
      console.error = originalConsoleError;
      console.warn = originalConsoleWarn;
    };
  }, []);

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return "Good Morning";
    if (hour < 18) return "Good Afternoon";
    return "Good Evening";
  };

  const clearLogs = () => {
    setLogs([]);
  };

  return (
    <div className="min-h-screen bg-background">
      <Sidebar />
      <main className="p-4 transition-all duration-300 sm:p-6 md:p-8 lg:ml-64">
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h2 className="text-lg font-medium text-muted-foreground sm:text-xl">{getGreeting()}</h2>
            <h1 className="mt-1 text-2xl font-bold tracking-tight sm:text-3xl md:text-4xl">
              John Anton
            </h1>
          </div>
          <div className="flex items-center gap-4">
            <button
              onClick={() => setShowDebug(!showDebug)}
              className={`rounded-full px-4 py-2 text-sm transition-colors ${
                showDebug ? "bg-[#13583E] text-white" : "bg-secondary text-secondary-foreground"
              }`}
            >
              Debug
            </button>
            <button
              className="rounded-full bg-secondary p-2 transition-colors hover:bg-secondary/80"
              aria-label="Settings"
            >
              <Settings className="h-5 w-5" />
            </button>
          </div>
        </div>
        
        {/* Categories section */}
        <div className="relative mb-6 -mx-4 px-4 sm:-mx-6 sm:px-6 md:-mx-8 md:px-8 md:mb-8">
          <div className="flex gap-2 overflow-x-auto pb-4 no-scrollbar">
            {categories.map((category) => (
              <button
                key={category}
                onClick={() => setSelectedCategory(category)}
                className={`rounded-full px-3 py-1.5 text-sm font-medium transition-colors whitespace-nowrap sm:px-4 sm:py-2 ${
                  selectedCategory === category
                    ? "bg-[#13583E] text-white shadow-lg"
                    : "bg-secondary text-secondary-foreground hover:bg-secondary/80"
                }`}
              >
                {category.split(' ').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')}
              </button>
            ))}
          </div>
        </div>

        {/* News grid */}
        <div className="grid gap-4 sm:gap-6 md:grid-cols-2 lg:grid-cols-3">
          {mockNews.map((news) => (
            <NewsCard key={news.id} {...news} />
          ))}
        </div>

        {/* Debug window */}
        {showDebug && (
          <div className="fixed bottom-4 right-4 w-96 max-h-96 bg-card border rounded-lg shadow-lg overflow-hidden">
            <div className="bg-secondary p-2 flex justify-between items-center">
              <h3 className="text-sm font-medium">Debug Console</h3>
              <div className="flex gap-2">
                <button
                  onClick={clearLogs}
                  className="text-xs px-2 py-1 rounded bg-primary/10 text-primary hover:bg-primary/20"
                >
                  Clear
                </button>
                <button
                  onClick={() => setShowDebug(false)}
                  className="text-muted-foreground hover:text-foreground"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>
            </div>
            <div className="overflow-y-auto h-64 p-2 bg-background/95 font-mono text-xs">
              {logs.map((log, index) => (
                <div key={index} className="py-1 border-b border-border/20 last:border-0">
                  {log}
                </div>
              ))}
              {logs.length === 0 && (
                <div className="text-muted-foreground text-center py-4">
                  No logs yet
                </div>
              )}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
