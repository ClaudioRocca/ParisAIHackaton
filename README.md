# 🌍 AI Voyage Assistant

An intelligent travel planning assistant that helps you find hotels, flights, and travel information using advanced web scraping and AI-powered recommendations.

## ✨ Features

- **🏨 Smart Hotel Search**: Find accommodations that match your budget, location, and preferences
- **✈️ Flight Discovery**: Search multiple airlines and booking sites for the best deals
- **🌍 Travel Intelligence**: Get destination guides, restaurant recommendations, and travel tips
- **🤖 AI-Powered**: Uses LangChain and OpenAI for intelligent conversation and planning
- **🔍 Web Scraping**: Real-time data from major travel booking sites
- **💬 Multiple Interfaces**: Web UI (Streamlit), CLI, and Python API

## 🚀 Quick Start

### 1. Installation

```bash
# Clone or download the project
cd lightpanda

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```env
# Required: OpenAI API Key
OPENAI_API_KEY=your_openai_api_key_here

# Optional: Professional scraping service
LIGHTPANDA_API_KEY=your_lightpanda_api_key_here
LIGHTPANDA_API_ENDPOINT=https://api.lightpanda.com/scrape
```

### 3. Run the Application

#### Web Interface (Recommended)
```bash
streamlit run app.py
```

#### Command Line Interface
```bash
python cli.py
```

#### Single Query
```bash
python cli.py --query "Find hotels in Paris under $200"
```

## 🛠️ Usage Examples

### Hotel Search
```
"Find luxury hotels in Dubai"
"Hotels in Tokyo under $150 per night"
"Best hotels near Times Square New York"
```

### Flight Search
```
"Flights from NYC to Paris"
"Cheap flights London to Barcelona"
"Direct flights from LAX to Tokyo"
```

### Travel Information
```
"Best restaurants in Rome"
"Things to do in Bali"
"Travel tips for Thailand"
"Plan a 3-day trip to London"
```

## 🏗️ Architecture

### Core Components

1. **`tools.py`**: Web scraping tools for hotels, flights, and travel info
2. **`agent.py`**: LangChain agent that orchestrates the tools
3. **`app.py`**: Streamlit web interface
4. **`cli.py`**: Command-line interface

### Web Scraping Strategy

The assistant uses a multi-tier scraping approach:

1. **Professional Service**: Uses Lightpanda or similar APIs when configured
2. **Direct Scraping**: Falls back to requests + BeautifulSoup
3. **Selenium**: For JavaScript-heavy sites (flights)

### Supported Sites

- **Hotels**: Booking.com, Expedia, Hotels.com
- **Flights**: Google Flights, Expedia, Kayak
- **Travel Info**: TripAdvisor, Lonely Planet, TimeOut

## 🔧 Configuration Options

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | OpenAI API key for the language model | Yes |
| `LIGHTPANDA_API_KEY` | Professional scraping service API key | No |
| `LIGHTPANDA_API_ENDPOINT` | Scraping service endpoint | No |
| `USER_AGENT` | User agent string for web requests | No |

### Model Options

- `gpt-3.5-turbo` (default, cost-effective)
- `gpt-4` (more capable, higher cost)
- `gpt-4-turbo-preview` (latest features)

## 📚 API Reference

### VoyageAssistant Class

```python
from agent import create_voyage_assistant

# Create assistant
assistant = create_voyage_assistant(
    model_name="gpt-3.5-turbo",
    temperature=0.7
)

# Chat with assistant
response = assistant.chat("Find hotels in Paris")
print(response)

# Reset conversation
assistant.reset_conversation()

# Get conversation history
history = assistant.get_conversation_history()
```

### Individual Tools

```python
from tools import search_hotels, search_flights, search_travel_info

# Search hotels
hotels = search_hotels("luxury hotels Dubai")

# Search flights  
flights = search_flights("flights NYC to Paris")

# Get travel info
info = search_travel_info("best restaurants Rome")
```

## 🚨 Important Notes

### Web Scraping Limitations

- **Rate Limits**: Websites may block frequent requests
- **Structure Changes**: Site layouts change, affecting parsing
- **JavaScript**: Some sites require Selenium for full functionality
- **Legal**: Respect robots.txt and terms of service

### Data Accuracy

- **Real-time**: Prices and availability change frequently
- **Verification**: Always verify information on official booking sites
- **Completeness**: Some searches may return limited results

### API Costs

- **OpenAI**: Charges per token (input + output)
- **Scraping Services**: May charge per request
- **Monitor Usage**: Set up billing alerts

## 🔒 Security Best Practices

1. **API Keys**: Never commit API keys to version control
2. **Environment Variables**: Use `.env` files for sensitive data
3. **Rate Limiting**: Implement delays between requests
4. **User Agents**: Use realistic user agent strings
5. **Proxies**: Consider using proxy services for production

## 🐛 Troubleshooting

### Common Issues

**"OPENAI_API_KEY environment variable is required"**
- Create a `.env` file with your OpenAI API key

**"Sorry, I couldn't find hotel information"**
- The target website may be blocking requests
- Try a different search term or check your internet connection

**Selenium WebDriver errors**
- Install Chrome browser
- Update Chrome to the latest version
- Check that webdriver-manager can download ChromeDriver

**Import errors**
- Install all requirements: `pip install -r requirements.txt`
- Check Python version compatibility (3.8+)

### Debug Mode

Enable verbose logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

### Development Setup

```bash
# Install development dependencies
pip install -r requirements.txt

# Run tests
python -m pytest tests/

# Format code
black .
isort .
```

## 📄 License

This project is licensed under the MIT License. See LICENSE file for details.

## 🙏 Acknowledgments

- **LangChain**: For the agent framework
- **OpenAI**: For the language models
- **Streamlit**: For the web interface
- **BeautifulSoup**: For HTML parsing
- **Selenium**: For JavaScript-heavy sites

## 📞 Support

For questions, issues, or feature requests:

1. Check the troubleshooting section
2. Search existing issues
3. Create a new issue with detailed information

---

**Happy Travels! 🌍✈️🏨**
