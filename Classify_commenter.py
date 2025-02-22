import asyncio
from newspaper import Article
from openai import OpenAI
from dotenv import load_dotenv
import os
import json
import logging
import requests
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('CommentVoiceMatcher')

load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')

if not OPENAI_API_KEY:
    logger.error("OpenAI API key not found in environment variables")
    raise ValueError("OpenAI API key not found")

if not ELEVENLABS_API_KEY:
    logger.error("ElevenLabs API key not found in environment variables")
    raise ValueError("ElevenLabs API key not found")

class VoiceCategory(str, Enum):
    """Voice categories from ElevenLabs"""
    PREMADE = "premade"
    PROFESSIONAL = "professional"
    GENERATED = "generated"

@dataclass(frozen=True)
class Voice:
    """Represents a voice with its characteristics"""
    voice_id: str
    name: str
    category: str
    accent: str
    age: str
    gender: str
    use_case: str
    description: Optional[str]
    preview_url: str
    
    def __hash__(self):
        return hash(self.voice_id)
    
    def __eq__(self, other):
        if not isinstance(other, Voice):
            return NotImplemented
        return self.voice_id == other.voice_id
    
    def to_dict(self):
        """Convert Voice object to dictionary for JSON serialization"""
        return {
            'voice_id': self.voice_id,
            'name': self.name,
            'category': self.category,
            'accent': self.accent,
            'age': self.age,
            'gender': self.gender,
            'use_case': self.use_case,
            'description': self.description,
            'preview_url': self.preview_url
        }

@dataclass
class CommentPersona:
    """Represents a commenter's persona and voice requirements"""
    perspective: str
    age_range: str
    gender: str
    tone: str
    expertise_level: str
    background: str
    speaking_style: str
    accent_preference: Optional[str] = None

class CommentVoiceMatcher:
    def __init__(self):
        """Initialize the voice matcher with API clients"""
        logger.info("Initializing CommentVoiceMatcher")
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.voices = self._fetch_voices()
        logger.info(f"Successfully fetched {len(self.voices)} voices")
    
    def _fetch_voices(self) -> List[Voice]:
        """Fetch all available voices from ElevenLabs API"""
        try:
            response = requests.get(
                "https://api.elevenlabs.io/v1/voices",
                headers={"xi-api-key": ELEVENLABS_API_KEY}
            )
            response.raise_for_status()
            
            voices_data = response.json()["voices"]
            return [
                Voice(
                    voice_id=voice["voice_id"],
                    name=voice["name"],
                    category=voice.get("category", "premade"),
                    accent=voice.get("labels", {}).get("accent", "unknown"),
                    age=voice.get("labels", {}).get("age", "unknown"),
                    gender=voice.get("labels", {}).get("gender", "unknown"),
                    use_case=voice.get("labels", {}).get("use_case", "unknown"),
                    description=voice.get("description"),
                    preview_url=voice.get("preview_url", "")
                )
                for voice in voices_data
            ]
        except Exception as e:
            logger.error(f"Error fetching voices: {e}")
            raise
        
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

    def analyze_perspective(self, perspective: str) -> CommentPersona:
        """Analyze a perspective to determine the ideal voice characteristics"""
        logger.info(f"Analyzing perspective: {perspective}")
        try:
            analysis_response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "user",
                        "content": f'''Analyze this commenter perspective and determine the ideal voice characteristics.
                        Return a JSON object with these fields:
                        - age_range: "young", "middle-aged", or "old"
                        - gender: "male" or "female"
                        - tone: describe the ideal tone (e.g., "authoritative", "casual", "energetic")
                        - expertise_level: "expert", "enthusiast", or "general"
                        - background: type of background (e.g., "academic", "industry", "activist")
                        - speaking_style: how they would speak (e.g., "formal", "conversational", "passionate")
                        - accent_preference: preferred accent if relevant (e.g., "british", "american", "australian"), or null if no preference
                        
                        Perspective: {perspective}
                        
                        Consider the perspective's implied:
                        - Professional background
                        - Level of expertise
                        - Typical age range
                        - Communication style
                        - Cultural context
                        
                        Return only the JSON object, no other text.'''
                    }
                ]
            )
            
            characteristics = json.loads(analysis_response.choices[0].message.content)
            return CommentPersona(
                perspective=perspective,
                age_range=characteristics["age_range"],
                gender=characteristics["gender"],
                tone=characteristics["tone"],
                expertise_level=characteristics["expertise_level"],
                background=characteristics["background"],
                speaking_style=characteristics["speaking_style"],
                accent_preference=characteristics.get("accent_preference")
            )
        except Exception as e:
            logger.error(f"Error analyzing perspective: {e}")
            raise

    async def _analyze_summary_voice_requirements(self, title: str, summary: str, style: str) -> CommentPersona:
        """Analyze the title and summary to determine ideal voice characteristics"""
        logger.info("Analyzing summary voice requirements")
        try:
            analysis_response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "user",
                        "content": f'''Analyze this news title and summary to determine the ideal voice characteristics for narration.
                        Consider the content's tone, subject matter, and emotional impact.
                        
                        Title: {title}
                        Summary: {summary}
                        Style: {style}
                        
                        Return a JSON object with these fields:
                        - age_range: "young", "middle-aged", or "old"
                        - gender: "male" or "female"
                        - tone: describe the ideal tone (e.g., "authoritative", "empathetic", "energetic", "serious", "casual", "dramatic")
                        - expertise_level: "expert", "enthusiast", or "general"
                        - background: type of background (e.g., "journalistic", "sports", "tech", "entertainment")
                        - speaking_style: how they should speak (e.g., "formal", "conversational", "passionate", "narrative")
                        - accent_preference: preferred accent if content suggests one (e.g., "british", "american", "australian"), or null if no preference
                        
                        Consider factors like:
                        - Is this breaking news, analysis, or feature story?
                        - What's the emotional tone (serious, upbeat, dramatic)?
                        - Is this general news or specialized content?
                        - Does the content suggest a particular cultural context?
                        - How should the style ({style}) influence the voice?
                        
                        Return only the JSON object, no other text.'''
                    }
                ]
            )
            
            characteristics = json.loads(analysis_response.choices[0].message.content)
            return CommentPersona(
                perspective="News Narrator",
                age_range=characteristics["age_range"],
                gender=characteristics["gender"],
                tone=characteristics["tone"],
                expertise_level=characteristics["expertise_level"],
                background=characteristics["background"],
                speaking_style=characteristics["speaking_style"],
                accent_preference=characteristics.get("accent_preference")
            )
        except Exception as e:
            logger.error(f"Error analyzing summary voice requirements: {e}")
            # Fallback to default persona if analysis fails
            return self._create_default_summary_persona(style)

    def _create_default_summary_persona(self, style: str) -> CommentPersona:
        """Create a default persona for the summary voice if analysis fails"""
        if style.lower() in ['rap', 'poetic', 'funny', 'casual']:
            return CommentPersona(
                perspective="News Narrator",
                age_range="middle-aged",
                gender="male",
                tone="engaging",
                expertise_level="expert",
                background="journalistic",
                speaking_style="conversational",
                accent_preference="american"
            )
        else:
            return CommentPersona(
                perspective="News Anchor",
                age_range="middle-aged",
                gender="male",
                tone="authoritative",
                expertise_level="expert",
                background="journalistic",
                speaking_style="formal",
                accent_preference="american"
            )

    def match_voice_to_persona(self, persona: CommentPersona) -> List[Tuple[Voice, float]]:
        """Match a voice to a commenter persona, returns list of (voice, score) tuples"""
        logger.info(f"Matching voice for persona: {persona.perspective}")
        
        matched_voices = []
        for voice in self.voices:
            score = self._calculate_voice_match_score(voice, persona)
            if score > 0.5:  # Only include voices with >50% match
                matched_voices.append((voice, score))
        
        # Sort by score descending
        matched_voices.sort(key=lambda x: x[1], reverse=True)
        return matched_voices[:5]  # Return top 5 matches

    def _calculate_voice_match_score(self, voice: Voice, persona: CommentPersona) -> float:
        """Calculate how well a voice matches a persona"""
        score = 0.0
        weights = {
            'age': 0.2,
            'gender': 0.15,
            'accent': 0.1,
            'expertise': 0.2,
            'tone': 0.2,
            'speaking_style': 0.15
        }
        
        # Age match
        if voice.age.lower() == persona.age_range:
            score += weights['age']
        elif abs(self._age_to_number(voice.age) - self._age_to_number(persona.age_range)) == 1:
            score += weights['age'] * 0.5
        
        # Gender match
        if voice.gender.lower() == persona.gender.lower():
            score += weights['gender']
        
        # Accent match
        if persona.accent_preference:
            if voice.accent.lower() == persona.accent_preference.lower():
                score += weights['accent']
        else:
            score += weights['accent']  # No preference means any accent is fine
        
        # Expertise level match
        voice_expertise = self._determine_voice_expertise(voice)
        if voice_expertise == persona.expertise_level:
            score += weights['expertise']
        elif voice_expertise in ['expert'] and persona.expertise_level in ['enthusiast']:
            score += weights['expertise'] * 0.7
        
        # Tone and speaking style match
        description = voice.description.lower() if voice.description else ""
        
        # Tone matching
        tone_keywords = {
            'authoritative': ['authoritative', 'commanding', 'professional'],
            'casual': ['casual', 'relaxed', 'friendly'],
            'energetic': ['energetic', 'dynamic', 'lively'],
            'formal': ['formal', 'serious', 'proper'],
            'caring': ['warm', 'caring', 'gentle', 'nurturing'],
            'passionate': ['passionate', 'enthusiastic', 'driven'],
            'analytical': ['analytical', 'precise', 'detailed'],
            'engaging': ['engaging', 'interactive', 'approachable']
        }
        if any(keyword in description for keyword in tone_keywords.get(persona.tone.lower(), [])):
            score += weights['tone']
        
        # Speaking style matching
        style_keywords = {
            'formal': ['formal', 'professional', 'proper'],
            'conversational': ['conversational', 'natural', 'friendly'],
            'passionate': ['passionate', 'enthusiastic', 'energetic'],
            'academic': ['academic', 'scholarly', 'educational'],
            'journalistic': ['journalistic', 'news', 'reporting'],
            'storytelling': ['narrative', 'storytelling', 'engaging']
        }
        if any(keyword in description for keyword in style_keywords.get(persona.speaking_style.lower(), [])):
            score += weights['speaking_style']
        
        return score

    def _age_to_number(self, age: str) -> int:
        """Convert age category to number for comparison"""
        age_map = {
            'young': 1,
            'middle-aged': 2,
            'middle aged': 2,
            'old': 3
        }
        return age_map.get(age.lower(), 2)

    def _determine_voice_expertise(self, voice: Voice) -> str:
        """Determine expertise level from voice characteristics"""
        if voice.category.lower() == "professional":
            return "expert"
        if voice.description and "expert" in voice.description.lower():
            return "expert"
        if voice.description and "enthusiast" in voice.description.lower():
            return "enthusiast"
        return "general"

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
            
            # Match voice for the summary based on content analysis
            logger.info("Analyzing and matching voice for summary")
            summary_persona = await self._analyze_summary_voice_requirements(article.title, summary, style)
            logger.info(f"Selected summary persona: {summary_persona}")
            summary_voices = self.match_voice_to_persona(summary_persona)
            summary_voice_matches = [(voice.to_dict(), score) for voice, score in summary_voices]
            
            # Get relevant perspectives for this specific article
            logger.info("Getting perspectives for the article")
            perspectives = await self.get_relevant_perspectives(article.text)
            
            # Generate styled comments from the determined perspectives and match voices
            logger.info("Generating styled comments and matching voices for each perspective")
            comments = {}
            voice_matches = {}
            
            for perspective in perspectives:
                logger.info(f"Processing perspective: {perspective}")
                
                # Generate styled comment
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
                            
                            Make it creative and entertaining while still providing meaningful insights from your perspective. 
                            The output will be used for text to speech so make minor adjustments accordingly to make it sound 
                            like natural human speech."""
                        }
                    ]
                )
                comments[perspective] = comment_response.choices[0].message.content
                
                # Match voice to perspective
                persona = self.analyze_perspective(perspective)
                matching_voices = self.match_voice_to_persona(persona)
                voice_matches[perspective] = [(voice.to_dict(), score) for voice, score in matching_voices]
                
                logger.debug(f"Generated comment for {perspective}: {comments[perspective][:100]}...")
                logger.debug(f"Found {len(matching_voices)} voice matches for {perspective}")
            
            # Also create a styled summary and match voice for it
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
            styled_summary = styled_summary_response.choices[0].message.content
            
            # Match voice for styled summary
            logger.info("Matching voice for styled summary")
            styled_summary_persona = await self._analyze_summary_voice_requirements(article.title, styled_summary, style)
            styled_summary_voices = self.match_voice_to_persona(styled_summary_persona)
            styled_summary_voice_matches = [(voice.to_dict(), score) for voice, score in styled_summary_voices]
            
            result = {
                "title": article.title,
                "original_summary": summary,
                "summary_voice_matches": summary_voice_matches,
                "styled_summary": styled_summary,
                "styled_summary_voice_matches": styled_summary_voice_matches,
                "perspectives_chosen": perspectives,
                "styled_comments": comments,
                "voice_matches": voice_matches
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
        
        matcher = CommentVoiceMatcher()
        result = await matcher.analyze_and_style_article(url, style)
        
        if isinstance(result, dict):
            logger.info("Successfully processed article")
            print("\nArticle Title:", result["title"])
            print("\nOriginal Summary:")
            print(result["original_summary"])
            
            # Get best matching voice for summary (highest score)
            if result["summary_voice_matches"]:
                best_summary_voice = max(result["summary_voice_matches"], key=lambda x: x[1])
                print(f"\nRecommended Voice for Original Summary: {best_summary_voice[0]['voice_id']}")
            else:
                print("\nNo voice match found for Original Summary")
            
            print(f"\n{style.capitalize()} Style Summary:")
            print(result["styled_summary"])
            
            # Get best matching voice for styled summary
            if result["styled_summary_voice_matches"]:
                best_styled_summary_voice = max(result["styled_summary_voice_matches"], key=lambda x: x[1])
                print(f"\nRecommended Voice for {style.capitalize()} Style Summary: {best_styled_summary_voice[0]['voice_id']}")
            else:
                print(f"\nNo voice match found for {style.capitalize()} Style Summary")
            
            print("\nRelevant Perspectives Identified:", ", ".join(result["perspectives_chosen"]))
            print(f"\n{style.capitalize()} Style Comments from Each Perspective:")
            print("=" * 50)
            for perspective in result["perspectives_chosen"]:
                print(f"\n{perspective}:")
                print("-" * len(perspective))
                print(result["styled_comments"][perspective])
                
                # Get best matching voice for this perspective (highest score)
                if perspective in result["voice_matches"] and result["voice_matches"][perspective]:
                    best_voice = max(result["voice_matches"][perspective], key=lambda x: x[1])
                    print(f"\nRecommended Voice for {perspective}: {best_voice[0]['voice_id']}")
                else:
                    print(f"\nNo voice match found for {perspective}")
                print("\n")
        else:
            logger.error(f"Failed to process article: {result}")
            print(result)
    except Exception as e:
        logger.error("Error in main function", exc_info=True)
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())
