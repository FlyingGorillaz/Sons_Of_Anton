import asyncio
from newspaper import Article
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

class StyleTranslator:
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        
    async def get_styled_summary(self, url, style):
        try:
            # Download and parse article
            article = Article(url)
            article.download()
            article.parse()
            
            # First get a basic summary
            summary_response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "user",
                        "content": f"Summarize this news article in 3 sentences:\n{article.text}"
                    }
                ]
            )
            summary = summary_response.choices[0].message.content
            
            # Then translate the summary into the desired style
            style_response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "user",
                        "content": f"Rewrite this news summary in {style} style:\n{summary}"
                    }
                ]
            )
            
            return {
                "original_summary": summary,
                "styled_summary": style_response.choices[0].message.content
            }
            
        except Exception as e:
            return f"Error processing article: {e}"

async def main():
    # Get URL and style preference from user
    url = input("Enter news article URL: ")
    style = input("\nEnter your preferred style: ")
    
    translator = StyleTranslator()
    result = await translator.get_styled_summary(url, style)
    
    if isinstance(result, dict):
        print("\nOriginal Summary:")
        print(result["original_summary"])
        print("\nStyled Summary:")
        print(result["styled_summary"])
    else:
        print(result)

if __name__ == "__main__":
    asyncio.run(main())
