import asyncio
from newspaper import Article
from openai import OpenAI
from dotenv import load_dotenv
import os
import json

load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

class NewsCommenter:
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        
    async def get_relevant_perspectives(self, article_text):
        """Determine the most relevant perspectives for commenting on this specific article."""
        perspective_response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "user",
                    "content": f"""Based on this news article, determine the 4-5 most relevant perspectives or stakeholders 
                    who would have interesting and diverse viewpoints on this topic. Return the result as a JSON array of 
                    strings, where each string is a specific type of commenter (e.g., "Tech Industry Expert", "Privacy Advocate", etc.).
                    
                    Article text: {article_text}
                    
                    Consider factors like:
                    - The main topic and field (tech, politics, sports, etc.)
                    - Key stakeholders mentioned or affected
                    - Relevant expert viewpoints needed
                    - Potential opposing viewpoints
                    - Local vs global perspectives if relevant
                    
                    Return only the JSON array, no other text."""
                }
            ]
        )
        
        perspectives = json.loads(perspective_response.choices[0].message.content)
        return perspectives
        
    async def analyze_article(self, url):
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
                        "content": f"Summarize this news article briefly:\n{article.text}"
                    }
                ]
            )
            summary = summary_response.choices[0].message.content
            
            # Get relevant perspectives for this specific article
            perspectives = await self.get_relevant_perspectives(article.text)
            
            # Generate comments from the determined perspectives
            comments = {}
            for perspective in perspectives:
                comment_response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {
                            "role": "user",
                            "content": f"""As a {perspective}, provide a brief, realistic comment on this news:
                            
                            Article Summary: {summary}
                            
                            Write your comment in a style and tone typical of your perspective. Include specific insights 
                            relevant to your expertise or viewpoint. Be authentic to how this type of person would actually respond."""
                        }
                    ]
                )
                comments[perspective] = comment_response.choices[0].message.content
            
            return {
                "title": article.title,
                "summary": summary,
                "perspectives_chosen": perspectives,
                "comments": comments
            }
            
        except Exception as e:
            return f"Error processing article: {e}"

async def main():
    # Get URL from user
    url = input("Enter news article URL: ")
    print("\nAnalyzing article and determining relevant perspectives...")
    
    commenter = NewsCommenter()
    result = await commenter.analyze_article(url)
    
    if isinstance(result, dict):
        print("\nArticle Title:", result["title"])
        print("\nSummary:", result["summary"])
        print("\nRelevant Perspectives Identified:", ", ".join(result["perspectives_chosen"]))
        print("\nComments from Each Perspective:")
        print("=" * 50)
        for perspective, comment in result["comments"].items():
            print(f"\n{perspective}:")
            print("-" * len(perspective))
            print(comment)
            print("\n")
    else:
        print(result)

if __name__ == "__main__":
    asyncio.run(main())
