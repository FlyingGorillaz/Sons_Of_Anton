
import { useLocation, useNavigate } from "react-router-dom";
import { ArrowLeft } from "lucide-react";

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

export default function Article() {
  const location = useLocation();
  const navigate = useNavigate();
  const { news } = (location.state as LocationState) || { news: null };

  if (!news) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <p>No article content found.</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background p-4 sm:p-6 md:p-8">
      <button
        onClick={() => navigate(-1)}
        className="mb-6 flex items-center gap-2 text-muted-foreground hover:text-foreground"
      >
        <ArrowLeft className="h-5 w-5" />
        <span>Back</span>
      </button>

      <article className="mx-auto max-w-2xl">
        <h1 className="mb-4 text-3xl font-bold">{news.title}</h1>
        <div className="mb-6 flex items-center gap-4">
          <p className="text-sm text-muted-foreground">
            Sources: {news.brands.join(", ")}
          </p>
          <p className="text-sm text-muted-foreground">{news.timestamp}</p>
        </div>
        <img
          src={news.image}
          alt={news.title}
          className="mb-6 h-64 w-full rounded-xl object-cover"
        />
        <p className="text-sm text-muted-foreground mb-6">
          Image source: Unsplash
        </p>
        <div className="prose prose-invert max-w-none">
          <p className="text-lg leading-relaxed">{news.summary}</p>
          {/* Additional AI-generated content would go here */}
        </div>
      </article>
    </div>
  );
}
