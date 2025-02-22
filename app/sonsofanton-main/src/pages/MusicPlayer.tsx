
import { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { ArrowLeft, BookOpen, Mic2, Play, Pause } from "lucide-react";

interface LocationState {
  news: {
    title: string;
    summary: string;
    brands: string[];
    timestamp: string;
    category: string;
    image: string;
  };
}

export default function MusicPlayer() {
  const location = useLocation();
  const navigate = useNavigate();
  const [isPlaying, setIsPlaying] = useState(false);

  // Check if location.state exists before destructuring
  if (!location.state) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center gap-4 p-4">
        <p className="text-center text-lg">No news content found. Please select a news article first.</p>
        <button
          onClick={() => navigate("/")}
          className="flex items-center gap-2 rounded-full bg-secondary px-6 py-2 text-secondary-foreground hover:bg-secondary/80"
        >
          <ArrowLeft className="h-5 w-5" />
          <span>Go back home</span>
        </button>
      </div>
    );
  }

  const { news } = location.state as LocationState;

  const handleReadMore = () => {
    navigate("/article", { state: { news } });
  };

  const handleLyrics = () => {
    navigate("/lyrics", { state: { news } });
  };

  return (
    <div className="min-h-screen bg-background p-4 sm:p-6 md:p-8">
      <button
        onClick={() => navigate(-1)}
        className="mb-6 flex items-center gap-2 text-muted-foreground hover:text-foreground"
      >
        <ArrowLeft className="h-5 w-5" />
        <span>Back</span>
      </button>

      <div className="mx-auto max-w-3xl">
        <div className="grid gap-8 md:grid-cols-2 md:gap-12 items-center">
          <div className="aspect-square w-full overflow-hidden rounded-xl shadow-2xl max-w-md mx-auto">
            <img
              src={news.image}
              alt={news.title}
              className="h-full w-full object-cover"
            />
          </div>

          <div className="text-center md:text-left">
            <h1 className="text-2xl font-bold sm:text-3xl">{news.title}</h1>
            <p className="mt-2 text-sm text-muted-foreground">
              Sources: {news.brands.join(", ")}
            </p>
            <p className="mt-1 text-xs text-muted-foreground">
              Image from Unsplash
            </p>

            <div className="mt-8 flex justify-center md:justify-start gap-4">
              <button
                onClick={() => setIsPlaying(!isPlaying)}
                className="flex h-14 w-14 items-center justify-center rounded-full bg-[#13583E] text-white shadow-lg transition-all duration-300 hover:bg-[#13583E]/90 hover:scale-105"
              >
                {isPlaying ? (
                  <Pause className="h-6 w-6" />
                ) : (
                  <Play className="h-6 w-6 pl-1" />
                )}
              </button>
            </div>

            <div className="mt-8 flex justify-center md:justify-start gap-4">
              <button
                onClick={handleReadMore}
                className="flex items-center gap-2 rounded-full bg-secondary px-6 py-2 text-secondary-foreground hover:bg-secondary/80"
              >
                <BookOpen className="h-5 w-5" />
                <span>Read More</span>
              </button>
              <button
                onClick={handleLyrics}
                className="flex items-center gap-2 rounded-full bg-secondary px-6 py-2 text-secondary-foreground hover:bg-secondary/80"
              >
                <Mic2 className="h-5 w-5" />
                <span>View Lyrics</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
