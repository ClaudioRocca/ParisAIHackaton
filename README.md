# Gemini API Project

A Python project for interacting with Google's Gemini AI API with proper environment variable configuration.

## 🚀 Features

- **Environment-based Configuration**: Secure API key and model configuration using `.env` files
- **Multiple Gemini Models**: Support for different Gemini models (1.5-pro, 1.5-flash, 1.0-pro)
- **Interactive Chat**: Command-line chat interface with Gemini
- **Video Generation**: Create videos using Veo 3 model from text prompts
- **Image Generation**: Generate images using Imagen 4.0 model
- **Image-to-Video**: Animate uploaded images or generated images into videos
- **Full Workflow**: Generate image first, then create video from it
- **Web Interface**: Beautiful multimedia web interface with tabs for different functions
- **File Upload**: Support for uploading images to animate
- **Flexible Parameters**: Configurable temperature, max tokens, and other generation parameters
- **Example Usage**: Comprehensive examples for different use cases
- **Error Handling**: Robust error handling and user-friendly messages

## 📋 Prerequisites

- Python 3.7 or higher
- Google AI Studio API key ([Get one here](https://makersuite.google.com/app/apikey))

## 🛠️ Installation

1. **Clone or download this project**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   ```bash
   cp .env.example .env
   ```

4. **Edit the `.env` file** and add your configuration:
   ```env
   GEMINI_API_KEY=your_actual_api_key_here
   GEMINI_MODEL=gemini-1.5-pro
   GEMINI_TEMPERATURE=0.7
   GEMINI_MAX_TOKENS=1000
   ```

## 🎯 Usage

### Interactive Chat Mode

Run the main application for an interactive chat with Gemini:

```bash
python gemini_client.py
```

### Using the GeminiClient Class

```python
from gemini_client import GeminiClient

# Initialize client
client = GeminiClient()

# Generate text
response = client.generate_text("Explain machine learning in simple terms")
print(response)

# Chat conversation
messages = [{"role": "user", "content": "What is Python?"}]
response = client.chat(messages)
print(response)

# Custom parameters
response = client.generate_text(
    "Write a creative story",
    temperature=0.9,  # More creative
    max_tokens=500
)
```

### Run Examples

See various usage examples:

```bash
python examples.py
```

### Web Interface

Launch a beautiful web interface for chatting with Gemini:

```bash
python web_app.py
```

Then open http://localhost:5000 in your browser for a modern chat interface.

### Enhanced Multimedia Web Interface

Launch the full multimedia interface with video and image generation:

```bash
python multimedia_web_app.py
```

Features:
- 💬 **Chat Tab**: Text conversations with Gemini
- 🎨 **Generate Image**: Create images from text prompts
- 🎬 **Generate Video**: Create videos from text prompts using Veo 3
- 🎭 **Animate Image**: Upload an image and animate it into a video
- ⚡ **Full Workflow**: Generate image then automatically create video from it

### Video and Image Generation (Command Line)

Use the video generation client directly:

```bash
python video_client.py
```

Run video and image examples:

```bash
python video_examples.py
```

## 📁 Project Structure

```
gemini-api/
├── .env.example              # Environment variables template
├── .env                      # Your actual environment variables (not in git)
├── .gitignore               # Git ignore file
├── requirements.txt         # Python dependencies
├── README.md               # This file
├── gemini_client.py        # Main Gemini client class
├── video_client.py         # Video and image generation client
├── examples.py             # Text generation examples
├── video_examples.py       # Video and image generation examples
├── web_app.py              # Basic Flask web interface
├── multimedia_web_app.py   # Enhanced multimedia web interface
├── templates/
│   ├── index.html          # Basic web interface template
│   └── multimedia_index.html # Enhanced multimedia interface
├── uploads/                # Uploaded images (created automatically)
└── generated/              # Generated content (created automatically)
```

## ⚙️ Configuration Options

| Environment Variable | Description | Default | Options |
|---------------------|-------------|---------|---------|
| `GEMINI_API_KEY` | Your Gemini API key | **Required** | Get from Google AI Studio |
| `GEMINI_MODEL` | Model to use | `gemini-1.5-pro` | `gemini-1.5-pro`, `gemini-1.5-flash`, `gemini-1.0-pro` |
| `GEMINI_TEMPERATURE` | Response creativity (0.0-1.0) | `0.7` | `0.0` (deterministic) to `1.0` (creative) |
| `GEMINI_MAX_TOKENS` | Maximum response length | `1000` | Any positive integer |

## 🔧 Available Models

### Text Generation (Gemini)
- **gemini-1.5-pro**: Most capable model, best for complex tasks
- **gemini-1.5-flash**: Faster responses, good for most tasks
- **gemini-1.0-pro**: Original model, reliable for basic tasks

### Video Generation
- **veo-3.0-generate-001**: Latest Veo 3 model for high-quality video generation

### Image Generation
- **imagen-4.0-generate-001**: Latest Imagen model for high-quality image generation

## 📝 Example Use Cases

### Text Generation
1. **Creative Writing**: Stories, poems, scripts
2. **Code Generation**: Python functions, scripts, debugging help
3. **Analysis**: Text analysis, data interpretation, research
4. **Chat**: Interactive conversations, Q&A sessions
5. **Translation**: Language translation and localization

### Video Generation
1. **Dialogue Scenes**: Character conversations and interactions
2. **Action Sequences**: Dynamic movement and cinematography
3. **Nature Documentaries**: Wildlife and landscape footage
4. **Product Demos**: Showcase products in motion
5. **Creative Animations**: Artistic and abstract video content

### Image Generation
1. **Concept Art**: Visual concepts for projects
2. **Illustrations**: Custom artwork and graphics
3. **Product Mockups**: Visual representations of ideas
4. **Landscapes**: Scenic and environmental imagery
5. **Character Design**: People, creatures, and characters

### Image-to-Video Workflows
1. **Storyboarding**: Convert static scenes to animated sequences
2. **Photo Animation**: Bring still photos to life
3. **Concept Visualization**: Animate design concepts
4. **Marketing Content**: Create engaging promotional videos
5. **Educational Content**: Illustrate processes and concepts

## 🛡️ Security Best Practices

- ✅ API keys stored in environment variables (not hardcoded)
- ✅ `.env` file excluded from version control
- ✅ Example configuration provided separately
- ✅ Input validation and error handling

## 🐛 Troubleshooting

### Common Issues

1. **"GEMINI_API_KEY not found"**
   - Make sure you copied `.env.example` to `.env`
   - Add your actual API key to the `.env` file

2. **"Failed to initialize model"**
   - Check if your API key is valid
   - Verify the model name is correct
   - Ensure you have internet connection

3. **"Error generating text"**
   - Check your API quota/billing
   - Verify the prompt is not too long
   - Try reducing `max_tokens` if needed

### Getting Help

- Check the [Google AI Studio documentation](https://ai.google.dev/)
- Review the examples in `examples.py`
- Ensure all dependencies are installed correctly

## 📄 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

---

**Happy coding with Gemini! 🚀**
