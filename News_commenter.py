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
logger = logging.getLogger('NewsCommenter')

load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    logger.error("OpenAI API key not found in environment variables")
    raise ValueError("OpenAI API key not found")

class NewsCommenter:
    def __init__(self):
        logger.info("Initializing NewsCommenter")
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
        
    async def analyze_article(self, url):
        logger.info(f"Starting analysis for URL: {url}")
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
                        "content": f"Summarize this news article briefly:\n{article.text}"
                    }
                ]
            )
            summary = summary_response.choices[0].message.content
            logger.debug(f"Generated summary: {summary[:100]}...")
            
            # Get relevant perspectives for this specific article
            logger.info("Getting perspectives for the article")
            perspectives = await self.get_relevant_perspectives(article.text)
            
            # Generate comments from the determined perspectives
            logger.info("Generating comments for each perspective")
            comments = {}
            for perspective in perspectives:
                logger.info(f"Generating comment for perspective: {perspective}")
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
                logger.debug(f"Generated comment for {perspective}: {comments[perspective][:100]}...")
            
            result = {
                "title": article.title,
                "summary": summary,
                "perspectives_chosen": perspectives,
                "comments": comments
            }
            logger.info("Successfully completed article analysis")
            logger.debug(f"Final result: {json.dumps(result, indent=2)}")
            return result
            
        except Exception as e:
            logger.error(f"Error processing article: {str(e)}", exc_info=True)
            return f"Error processing article: {e}"

async def main():
    logger.info("Starting main function")
    try:
        # Get URL from user
        url = input("Enter news article URL: ")
        logger.info(f"User input - URL: {url}")
        print("\nAnalyzing article and determining relevant perspectives...")
        
        commenter = NewsCommenter()
        result = await commenter.analyze_article(url)
        
        if isinstance(result, dict):
            logger.info("Successfully processed article")
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
            logger.error(f"Failed to process article: {result}")
            print(result)
    except Exception as e:
        logger.error("Error in main function", exc_info=True)
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())
