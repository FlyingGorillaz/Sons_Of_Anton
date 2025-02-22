# Sons of Anton - AI-Powered News Commentary

An innovative AI application that transforms news articles into engaging audio commentaries with dynamic voice selection and personalized styling.

## Features

- 🎯 Automatic extraction and summarization of news articles
- 🎭 Dynamic voice selection based on content context
- 🎨 Customizable comment styling
- 🔊 High-quality text-to-speech conversion
- 🌐 Chrome extension support
- 📱 RESTful API for easy integration

## Prerequisites

- Python 3.8+
- API keys for:
  - OpenAI
  - ElevenLabs
  - (Optional) Groq

## Installation

1. Clone the repository:
   ```bash
   git clone [your-repo-url]
   cd Sons_Of_Anton
   ```

2. Create and activate a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the root directory with your API keys:
   ```env
   OPENAI_API_KEY=your_openai_api_key
   ELEVENLABS_API_KEY=your_elevenlabs_api_key
   GROQ_API_KEY=your_groq_api_key  # Optional
   ```

## Running the Application

1. Start the server:
   ```bash
   python server.py
   ```
   The server will start on `http://localhost:8000`

2. API Endpoints:
   - POST `/api/data`
     ```json
     {
       "url": "https://news-article-url.com",
       "style": "Uwu"  // Optional, defaults to "Uwu"
     }
     ```
   - Returns: Audio stream of the AI-generated commentary

## Chrome Extension

The application includes a Chrome extension for easy access while browsing news articles:

1. Open Chrome and navigate to `chrome://extensions/`
2. Enable "Developer mode"
3. Click "Load unpacked" and select the `chrome_extension` directory
4. The extension icon will appear in your browser toolbar

## Project Structure

- `server.py`: FastAPI server implementation
- `speak.py`: Text-to-speech conversion with dynamic voice selection
- `Classify_commenter.py`: AI-powered voice selection system
- `News_comment_styler.py`: Commentary style customization
- `news_summary_extractor.py`: Article extraction and summarization
- `chrome_extension/`: Chrome extension files

## Error Handling

The application includes comprehensive error handling:
- Invalid URLs
- Failed article extraction
- API failures
- Audio generation issues

All errors are logged and appropriate error messages are returned to the client.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support, please open an issue in the repository or contact the maintainers.