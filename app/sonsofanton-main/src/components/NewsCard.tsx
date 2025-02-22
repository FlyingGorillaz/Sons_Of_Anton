
import { Play, BookOpen } from "lucide-react";
import { useState } from "react";
import { useNavigate } from "react-router-dom";

interface NewsCardProps {
  title: string;
  summary: string;
  brands: string[];
  timestamp: string;
  category: string;
  image: string;
}

export default function NewsCard({ title, summary, brands, timestamp, category, image }: NewsCardProps) {
  const [mode, setMode] = useState<"read" | "music">("read");
  const navigate = useNavigate();

  const handleModeClick = (selectedMode: "read" | "music") => {
    setMode(selectedMode);
    if (selectedMode === "music") {
      navigate("/player", { 
        state: { 
          news: { 
            title, 
            summary, 
            brands, 
            timestamp, 
            category, 
            image 
          } 
        } 
      });
    }
  };

  return (
    <div className="news-card">
      <div className="relative mb-4 h-40 overflow-hidden rounded-lg">
        <img 
          src={image} 
          alt={title}
          className="h-full w-full object-cover transition-transform duration-300 hover:scale-105"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-background/80 to-transparent" />
      </div>

      <div className="mb-3 flex flex-wrap items-center justify-between gap-2 sm:mb-4">
        <span className="rounded-full bg-primary/10 px-2 py-1 text-xs font-medium text-primary sm:px-3">
          {category}
        </span>
        <span className="text-xs text-muted-foreground">{timestamp}</span>
      </div>
      
      <h3 className="mb-2 text-base font-semibold tracking-tight sm:text-lg">{title}</h3>
      <p className="mb-3 text-sm text-muted-foreground line-clamp-2 sm:mb-4">{summary}</p>
      
      <div className="mt-3 flex flex-wrap items-center justify-between gap-3 sm:mt-4">
        <div className="flex -space-x-2">
          {brands.map((brand, index) => (
            <div
              key={brand}
              className="flex h-6 w-6 items-center justify-center rounded-full bg-secondary text-xs font-medium ring-2 ring-background"
              title={brand}
            >
              {brand[0]}
            </div>
          ))}
        </div>
        
        <div className="flex items-end gap-4">
          <button
            onClick={() => handleModeClick("read")}
            className={`inline-flex h-8 w-8 items-center justify-center rounded-full bg-secondary text-secondary-foreground transition-colors hover:bg-secondary/80 ${mode === "read" ? "bg-primary text-primary-foreground" : ""}`}
            aria-label="Read mode"
          >
            <BookOpen className="h-4 w-4" />
          </button>
          <button
            onClick={() => handleModeClick("music")}
            className={`inline-flex h-12 w-12 items-center justify-center rounded-full bg-[#13583E] text-white shadow-lg transition-all duration-300 hover:bg-[#13583E]/90 hover:scale-105 ${mode === "music" ? "ring-4 ring-[#13583E]/20 shadow-[#13583E]/20 shadow-lg" : ""}`}
            aria-label="Music mode"
          >
            <Play className="h-6 w-6 pl-0.5" />
          </button>
        </div>
      </div>
    </div>
  );
}
