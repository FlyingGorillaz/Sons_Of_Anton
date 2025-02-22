from elevenlabs.client import ElevenLabs, Voice, VoiceSettings
from dotenv import load_dotenv
from logger import logging
import os
import asyncio
from utils import timing
import io

load_dotenv()
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")


@timing
async def speak(text: str):
    try:
        if not ELEVENLABS_API_KEY:
            raise ValueError("ELEVENLABS_API_KEY not found in environment variables")
            
        # Ensure text is a string and not empty
        if not isinstance(text, str):
            text = str(text)
        text = text.strip()
        if not text:
            raise ValueError("Empty text provided to speak function")
            
        logging.info(f"Generating audio for text (first 5000 chars): {text[:5000]}...")
        
        client = ElevenLabs(
            api_key=ELEVENLABS_API_KEY
        )

        # Generate audio with correct output format
        try:
            audio_stream = client.generate(
                text=text,
                voice=Voice(
                    voice_id="onwK4e9ZLuTAKqWW03F9",
                    settings=VoiceSettings(
                        stability=0.5,
                        similarity_boost=0.75,
                        style=0.0,
                        use_speaker_boost=False,
                    ),
                ),
                model="eleven_turbo_v2_5",
                output_format="mp3_44100_128"  # High-quality MP3 format
            )
        except Exception as e:
            logging.error(f"ElevenLabs API error: {e}")
            raise ValueError(f"Failed to generate audio: {str(e)}")
        
        # Create an async generator for streaming
        async def audio_generator():
            try:
                # If audio_stream is already bytes, yield it directly
                if isinstance(audio_stream, bytes):
                    yield audio_stream
                    return
                    
                # If it's a generator or iterator, yield chunks
                chunk_count = 0
                for chunk in audio_stream:  # Regular for loop instead of async for
                    if chunk:
                        chunk_count += 1
                        yield chunk
                
                if chunk_count == 0:
                    raise ValueError("No audio chunks generated")
                    
                logging.info(f"Successfully streamed {chunk_count} audio chunks")
                
            except Exception as e:
                logging.error(f"Error in audio generator: {e}")
                raise ValueError(f"Audio streaming error: {str(e)}")

        return audio_generator()

    except Exception as e:
        logging.error(f"Error in speak function: {e}")
        raise  # Re-raise the exception to handle it at a higher level


if __name__ == "__main__":
    asyncio.run(speak("e money \"derived substantially the whole of its value from the activities of Mr Grint\", which was \"otherwise realised\" as income.\n\nHe previously lost another, separate court case in 2019 that involved a £1m tax refund.\n\nGrint appeared in all eight Harry Potter films from 2001 until 2011.\n\nSince then, he has appeared in the films Into the White and Knock at the Cabin, and also appeared on TV and in theatre.\n\nHe has starred in Apple TV series Servant for the last four years."))