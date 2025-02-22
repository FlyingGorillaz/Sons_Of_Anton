import os
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
from fastapi.middleware.cors import CORSMiddleware
from news_summary_extractor import ArticleExtractor
from News_comment_styler import NewsCommentStyler
from speak import speak
from fastapi.responses import StreamingResponse
import logging
from urllib.parse import urlparse

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class URLData(BaseModel):
    url: HttpUrl  # This ensures URL validation
    style: str = "Uwu"  # Default style if none provided

@app.post("/api/data")
async def process_everything(request_data: URLData):
    try:
        news_url = str(request_data.url)  # Convert Pydantic URL to string
        
        # Check if URL is from a supported domain
        parsed_url = urlparse(news_url)
        if parsed_url.scheme not in ['http', 'https']:
            raise HTTPException(status_code=400, detail="Only HTTP and HTTPS URLs are supported")
            
        # Extract and summarize article
        article_extractor = ArticleExtractor()
        article_summary = await article_extractor(news_url)
        
        if not article_summary:
            raise HTTPException(status_code=400, detail="Failed to generate article summary")
        
        # Style the article summary
        styler = NewsCommentStyler()
        styled_result = await styler.analyze_and_style_article(news_url, request_data.style)
        
        # Check if styled_result is an error message (string) or None
        if not styled_result or isinstance(styled_result, str):
            error_msg = styled_result if isinstance(styled_result, str) else "Unknown styling error"
            logging.warning(f"Failed to style article: {error_msg}")
            final_summary = article_summary
        else:
            try:
                final_summary = f"{styled_result['styled_summary']}\n\nPerspectives:\n"
                for perspective, comment in styled_result['styled_comments'].items():
                    final_summary += f"\n{perspective}: {comment}\n"
            except KeyError as e:
                logging.error(f"Unexpected response format from styler: {e}")
                final_summary = article_summary
        
        # Generate audio
        audio_generator = await speak(final_summary)
        if not audio_generator:
            raise HTTPException(status_code=500, detail="Failed to generate audio")
            
        return StreamingResponse(
            audio_generator,
            media_type="audio/mpeg",
            headers={
                "Content-Type": "audio/mpeg",
                "Content-Disposition": "attachment; filename=speech.mp3"
            }
        )
    except Exception as e:
        logging.error(f"Error in process_everything: {str(e)}")
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
