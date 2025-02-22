import asyncio
from newspaper import Article
from openai import OpenAI
from dotenv import load_dotenv
import os
import json

load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

class NewsCommentStyler:
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
        
    async def analyze_and_style_article(self, url, style):
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
            
            # Generate styled comments from the determined perspectives
            comments = {}
            for perspective in perspectives:
                comment_response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {
                            "role": "user",
                            "content": f"""As a {perspective}, provide a comment on this news in a {style} style:
                            
                            Article Summary: {summary}
                            
                            Write your comment in {style} style while maintaining the authenticity of your perspective.
                            For example, if the style is 'medieval' and you're a tech expert, write like a medieval scholar
                            discussing technology. If the style is 'poetic' and you're a political analyst, write a poetic
                            analysis of the political situation.
                            
                            Make it creative and entertaining while still providing meaningful insights from your perspective."""
                        }
                    ]
                )
                comments[perspective] = comment_response.choices[0].message.content
            
            # Also create a styled summary
            styled_summary_response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "user",
                        "content": f"Rewrite this news summary in {style} style:\n{summary}"
                    }
                ]
            )
            
            return {
                "title": article.title,
                "original_summary": summary,
                "styled_summary": styled_summary_response.choices[0].message.content,
                "perspectives_chosen": perspectives,
                "styled_comments": comments
            }
            
        except Exception as e:
            return f"Error processing article: {e}"

async def main():
    # Get URL and style from user
    url = input("Enter news article URL: ")
    style = input("\nEnter your preferred style: ")
    
    styler = NewsCommentStyler()
    result = await styler.analyze_and_style_article(url, style)
    
    if isinstance(result, dict):
        print("\nArticle Title:", result["title"])
        print("\nOriginal Summary:")
        print(result["original_summary"])
        print(f"\n{style.capitalize()} Style Summary:")
        print(result["styled_summary"])
        print("\nRelevant Perspectives Identified:", ", ".join(result["perspectives_chosen"]))
        print(f"\n{style.capitalize()} Style Comments from Each Perspective:")
        print("=" * 50)
        for perspective, comment in result["styled_comments"].items():
            print(f"\n{perspective}:")
            print("-" * len(perspective))
            print(comment)
            print("\n")
    else:
        print(result)

if __name__ == "__main__":
    asyncio.run(main())