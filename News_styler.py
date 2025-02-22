import asyncio
from newspaper import Article
from openai import OpenAI
from dotenv import load_dotenv
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('StyleTranslator')

load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    logger.error("OpenAI API key not found in environment variables")
    raise ValueError("OpenAI API key not found")

class StyleTranslator:
    def __init__(self):
        logger.info("Initializing StyleTranslator")
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        
    async def get_styled_summary(self, url, style):
        logger.info(f"Starting style translation for URL: {url} with style: {style}")
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
                        "content": f"Summarize this news article in 3 sentences:\n{article.text}"
                    }
                ]
            )
            summary = summary_response.choices[0].message.content
            logger.debug(f"Generated summary: {summary}")
            
            # Then translate the summary into the desired style
            logger.info(f"Translating summary to {style} style")
            style_response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "user",
                        "content": f"Rewrite this news summary in {style} style:\n{summary}"
                    }
                ]
            )
            
            styled_summary = style_response.choices[0].message.content
            logger.debug(f"Generated styled summary: {styled_summary}")
            
            result = {
                "original_summary": summary,
                "styled_summary": styled_summary
            }
            logger.info("Successfully completed style translation")
            return result
            
        except Exception as e:
            logger.error(f"Error processing article: {str(e)}", exc_info=True)
            return f"Error processing article: {e}"

async def main():
    logger.info("Starting main function")
    try:
        # Get URL and style preference from user
        url = input("Enter news article URL: ")
        style = input("\nEnter your preferred style: ")
        logger.info(f"User input - URL: {url}, Style: {style}")
        
        translator = StyleTranslator()
        result = await translator.get_styled_summary(url, style)
        
        if isinstance(result, dict):
            logger.info("Successfully processed article")
            print("\nOriginal Summary:")
            print(result["original_summary"])
            print("\nStyled Summary:")
            print(result["styled_summary"])
        else:
            logger.error(f"Failed to process article: {result}")
            print(result)
    except Exception as e:
        logger.error("Error in main function", exc_info=True)
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())
