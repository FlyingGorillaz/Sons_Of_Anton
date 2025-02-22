import asyncio
from newspaper import Article
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

class NewsSummarizer:
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        
    async def summarize_article(self, url):
        try:
            # Download and parse article
            article = Article(url)
            article.download()
            article.parse()
            
            # Generate summary using OpenAI
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "user",
                        "content": f"Summarize this news article in 3 sentences:\n{article.text}"
                    }
                ]
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Error processing article: {e}"

async def main():
    # Example usage
    url = input("Enter news article URL: ")
    summarizer = NewsSummarizer()
    summary = await summarizer.summarize_article(url)
    print("\nArticle Summary:")
    print(summary)

if __name__ == "__main__":
    asyncio.run(main())
