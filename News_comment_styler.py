import asyncio
from newspaper import Article
from openai import OpenAI
from dotenv import load_dotenv
import os
import json
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('NewsCommentStyler')

load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    logger.error("OpenAI API key not found in environment variables")
    raise ValueError("OpenAI API key not found")

class NewsCommentStyler:
    def __init__(self):
        logger.info("Initializing NewsCommentStyler")
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        
    async def get_relevant_perspectives(self, article_text):
        """Determine the most relevant perspectives for commenting on this specific article."""
        logger.info("Getting relevant perspectives for article")
        try:
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
            logger.info(f"Generated {len(perspectives)} perspectives: {perspectives}")
            return perspectives
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse perspectives JSON: {e}")
            logger.debug(f"Raw response: {perspective_response.choices[0].message.content}")
            raise
        except Exception as e:
            logger.error(f"Error getting perspectives: {e}")
            raise
        
    async def analyze_and_style_article(self, url, style):
        logger.info(f"Starting analysis for URL: {url} with style: {style}")
        try:
            # Download and parse article
            logger.info("Downloading and parsing article")
            article = Article(url)
            article.download()
            article.parse()
            logger.info(f"Successfully parsed article: {article.title}")
            
            # First get a basic summary
            logger.info("Generating basic summary")
            summary_response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "user",
                        "content": f"Summarize this news article briefly keep the length less than 30 seconds of speech:\n{article.text}"
                    }
                ]
            )
            summary = summary_response.choices[0].message.content
            logger.debug(f"Generated summary: {summary[:1000]}...")
            
            # Get relevant perspectives for this specific article
            logger.info("Getting perspectives for the article")
            perspectives = await self.get_relevant_perspectives(article.text)
            
            # Generate styled comments from the determined perspectives
            logger.info("Generating styled comments for each perspective")
            comments = {}
            for perspective in perspectives:
                logger.info(f"Generating comment for perspective: {perspective}")
                comment_response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {
                            "role": "user",
                            "content": f"""As a {perspective}, provide a comment on this news in a {style} style:
                            
                            Article Summary: {summary}
                            
                            Write your comment in {style} style while maintaining the authenticity of your perspective.
                            For example, if the style is 'RAP' and you're a tech expert, write like a world famous wrapper
                            discussing technology. If the style is 'poetic' and you're a political analyst, write a poetic
                            analysis of the political situation.
                            
                            Make it creative and entertaining while still providing meaningful insights from your perspective. the output will be used for text to speech so make minor adjustments accordingly to make it sound like natural human speech."""
                        }
                    ]
                )
                comments[perspective] = comment_response.choices[0].message.content
                logger.debug(f"Generated comment for {perspective}: {comments[perspective][:100]}...")
            
            # Also create a styled summary
            logger.info("Generating styled summary")
            styled_summary_response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "user",
                        "content": f"Rewrite this news summary in {style} style:\n{summary}"
                    }
                ]
            )
            
            result = {
                "title": article.title,
                "original_summary": summary,
                "styled_summary": styled_summary_response.choices[0].message.content,
                "perspectives_chosen": perspectives,
                "styled_comments": comments
            }
            logger.info("Successfully completed article analysis and styling")
            logger.debug(f"Final result: {json.dumps(result, indent=2)}")
            return result
            
        except Exception as e:
            logger.error(f"Error processing article: {str(e)}", exc_info=True)
            return f"Error processing article: {e}"

async def main():
    logger.info("Starting main function")
    try:
        # Get URL and style from user
        url = input("Enter news article URL: ")
        style = input("\nEnter your preferred style: ")
        logger.info(f"User input - URL: {url}, Style: {style}")
        
        styler = NewsCommentStyler()
        result = await styler.analyze_and_style_article(url, style)
        
        if isinstance(result, dict):
            logger.info("Successfully processed article")
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
            logger.error(f"Failed to process article: {result}")
            print(result)
    except Exception as e:
        logger.error("Error in main function", exc_info=True)
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())