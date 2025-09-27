"""
AI Voyage Assistant - Web Scraping Tools
Simplified tools for scraping hotel and flight information.
- Flights: Skyscanner only
- Hotels: Booking.com and Airbnb only
"""

import os
import requests
import urllib3
import socket
import ssl
from bs4 import BeautifulSoup
from typing import Dict, List, Optional, Any
import json
import time
import random
from urllib.parse import urlencode, quote_plus
from langchain.tools import tool
import logging
from datetime import datetime, timedelta

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LightpandaScraper:
    """
    Scraper class that can work with Lightpanda API or fallback to direct scraping
    """
    
    def __init__(self):
        self.api_key = os.getenv('LIGHTPANDA_API_KEY')
        self.api_endpoint = os.getenv('LIGHTPANDA_API_ENDPOINT')
        self.user_agent = os.getenv('USER_AGENT', 
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        
    def scrape_with_service(self, url: str) -> str:
        """
        Scrape using Lightpanda professional service
        """
        if self.api_key and self.api_endpoint:
            logger.info(f"Using Lightpanda API to scrape: {url}")
            return self.scrape_with_lightpanda(url)
        else:
            logger.info("No Lightpanda API credentials, using direct scraping")
            return self.scrape_direct(url)
    
    def scrape_with_lightpanda(self, url: str) -> str:
        """
        Scrape using Lightpanda API with improved SSL handling and error recovery
        """
        try:
            payload = {
                'url': url,
                'render_js': True,
                'wait_for': 3000,  # Wait 3 seconds for JS to load
                'block_resources': ['image', 'stylesheet', 'font'],  # Speed up by blocking unnecessary resources
                'user_agent': self.user_agent
            }
            
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            logger.info(f"Attempting to connect to Lightpanda API: {self.api_endpoint}")
            
            # Create a session with better SSL configuration
            session = requests.Session()
            session.headers.update(headers)
            
            # Try with different timeout and SSL configurations
            try:
                # First attempt: Normal SSL with shorter timeouts
                response = session.post(
                    self.api_endpoint,
                    json=payload,
                    timeout=(5, 15),  # Shorter timeouts to fail faster
                    verify=True,
                    allow_redirects=True
                )
                
            except (requests.exceptions.SSLError, requests.exceptions.ConnectTimeout, requests.exceptions.ConnectionError) as e:
                logger.warning(f"SSL/connection error with Lightpanda API: {e}")
                logger.info("Falling back to direct scraping immediately")
                return self.scrape_direct(url)
            
            if response.status_code == 200:
                result = response.json()
                html_content = result.get('html', '')
                
                if html_content and len(html_content) > 1000:  # Ensure we got meaningful content
                    logger.info(f"Successfully scraped {len(html_content)} characters via Lightpanda")
                    return html_content
                else:
                    logger.warning("Lightpanda returned minimal content, falling back to direct scraping")
                    return self.scrape_direct(url)
            else:
                logger.error(f"Lightpanda API error: {response.status_code} - {response.text}")
                return self.scrape_direct(url)
                
        except Exception as e:
            logger.error(f"Lightpanda API completely failed: {e}")
            logger.info("Using direct scraping as fallback")
            return self.scrape_direct(url)
    
    def test_lightpanda_connection(self) -> bool:
        """
        Test if Lightpanda API is accessible with SSL troubleshooting
        """
        if not self.api_key or not self.api_endpoint:
            logger.info("Missing Lightpanda credentials")
            return False
            
        try:
            # Test with a simple URL and shorter timeout
            test_payload = {
                'url': 'https://httpbin.org/html',
                'render_js': False
            }
            
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            # Try with different SSL configurations
            session = requests.Session()
            session.headers.update(headers)
            
            # First try: Normal SSL
            try:
                response = session.post(
                    self.api_endpoint,
                    json=test_payload,
                    timeout=(5, 10),
                    verify=True
                )
                if response.status_code == 200:
                    logger.info("Lightpanda connection test successful")
                    return True
            except requests.exceptions.SSLError:
                logger.warning("SSL verification failed, trying without SSL verification")
                # Second try: Skip SSL verification (not recommended for production)
                try:
                    import urllib3
                    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
                    response = session.post(
                        self.api_endpoint,
                        json=test_payload,
                        timeout=(5, 10),
                        verify=False
                    )
                    if response.status_code == 200:
                        logger.warning("Lightpanda connection successful but SSL verification disabled")
                        return True
                except Exception as e:
                    logger.error(f"Connection failed even without SSL verification: {e}")
            
            return False
            
        except Exception as e:
            logger.error(f"Lightpanda connection test failed: {e}")
            return False
    
    def diagnose_network_issues(self):
        """
        Diagnose network connectivity issues with LightPanda API
        """
        import socket
        import ssl
        from urllib.parse import urlparse
        
        if not self.api_endpoint:
            logger.error("No Lightpanda API endpoint configured")
            return
        
        try:
            parsed_url = urlparse(self.api_endpoint)
            hostname = parsed_url.hostname
            port = parsed_url.port or (443 if parsed_url.scheme == 'https' else 80)
            
            logger.info(f"Diagnosing connection to {hostname}:{port}")
            
            # Test DNS resolution
            try:
                ip = socket.gethostbyname(hostname)
                logger.info(f"DNS resolution successful: {hostname} -> {ip}")
            except socket.gaierror as e:
                logger.error(f"DNS resolution failed: {e}")
                return
            
            # Test TCP connection
            try:
                sock = socket.create_connection((hostname, port), timeout=10)
                logger.info(f"TCP connection successful to {hostname}:{port}")
                sock.close()
            except socket.timeout:
                logger.error(f"TCP connection timeout to {hostname}:{port}")
                return
            except Exception as e:
                logger.error(f"TCP connection failed: {e}")
                return
            
            # Test SSL handshake if HTTPS
            if parsed_url.scheme == 'https':
                try:
                    context = ssl.create_default_context()
                    with socket.create_connection((hostname, port), timeout=10) as sock:
                        with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                            logger.info(f"SSL handshake successful to {hostname}")
                            logger.info(f"SSL version: {ssock.version()}")
                            logger.info(f"SSL cipher: {ssock.cipher()}")
                except ssl.SSLError as e:
                    logger.error(f"SSL handshake failed: {e}")
                except socket.timeout:
                    logger.error(f"SSL handshake timeout to {hostname}")
                except Exception as e:
                    logger.error(f"SSL connection error: {e}")
                    
        except Exception as e:
            logger.error(f"Network diagnostics failed: {e}")

    def scrape_direct(self, url: str) -> str:
        """
        Direct scraping fallback using requests and BeautifulSoup
        """
        try:
            # Use multiple user agents to avoid detection
            user_agents = [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15'
            ]
            
            headers = {
                'User-Agent': random.choice(user_agents),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Cache-Control': 'max-age=0'
            }
            
            # Add random delay to avoid being blocked
            time.sleep(random.uniform(2, 5))
            
            # Use session for better connection handling
            session = requests.Session()
            session.headers.update(headers)
            
            response = session.get(url, timeout=20, allow_redirects=True)
            response.raise_for_status()
            
            logger.info(f"Successfully scraped {len(response.text)} characters from {url}")
            return response.text
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Direct scraping error for {url}: {e}")
            return ""
        except Exception as e:
            logger.error(f"Unexpected error scraping {url}: {e}")
            return ""

    def scrape_with_selenium(self, url: str) -> str:
        """
        Selenium-based scraping for JavaScript-heavy sites (fallback method)
        Note: This is a placeholder - Selenium requires additional setup
        """
        logger.warning("Selenium scraping requested but not fully implemented")
        logger.info("Falling back to direct scraping instead")
        return self.scrape_direct(url)

# Initialize scraper
scraper = LightpandaScraper()

def parse_hotel_results(html: str, source: str = "booking") -> List[Dict[str, Any]]:
    """
    Parse hotel search results from Booking.com or Airbnb HTML
    """
    soup = BeautifulSoup(html, 'html.parser')
    hotels = []
    
    if source == "booking":
        # Booking.com specific selectors
        hotel_selectors = [
            {'container': '[data-testid="property-card"]', 'name': '[data-testid="title"]', 'price': '[data-testid="price-and-discounted-price"]', 'rating': '[data-testid="review-score"]'},
            {'container': '.sr_property_block', 'name': '.sr-hotel__name', 'price': '.bui-price-display__value', 'rating': '.bui-review-score__badge'},
            {'container': '.property_card', 'name': 'h3', 'price': '.price', 'rating': '.rating'}
        ]
    else:  # airbnb
        # Airbnb specific selectors
        hotel_selectors = [
            {'container': '[data-testid="card-container"]', 'name': '[data-testid="listing-card-title"]', 'price': '[data-testid="price-availability"]', 'rating': '[data-testid="listing-card-subtitle"]'},
            {'container': '.listing-card', 'name': '.listing-card-title', 'price': '.price', 'rating': '.rating'},
            {'container': '.property', 'name': 'h3, h4', 'price': '.price', 'rating': '.rating'}
        ]
    
    for selector_set in hotel_selectors:
        containers = soup.select(selector_set['container'])
        logger.info(f"Found {len(containers)} potential hotel containers with selector: {selector_set['container']}")
        
        if containers:
            for container in containers[:15]:
                try:
                    name_elem = container.select_one(selector_set['name'])
                    price_elem = container.select_one(selector_set['price'])
                    rating_elem = container.select_one(selector_set['rating'])
                    
                    name = name_elem.get_text(strip=True) if name_elem else ''
                    price = price_elem.get_text(strip=True) if price_elem else 'Check website'
                    rating = rating_elem.get_text(strip=True) if rating_elem else 'See reviews'
                    
                    if name and len(name) > 3:
                        hotels.append({
                            'name': name[:100],
                            'price': price[:50],
                            'rating': rating[:20],
                            'source': source,
                            'type': 'hotel'
                        })
                        
                except Exception as e:
                    logger.debug(f"Error parsing hotel container: {e}")
                    continue
            
            if hotels:
                logger.info(f"Successfully parsed {len(hotels)} hotels from {source}")
                break
    
    return hotels

def validate_future_date(date_str: str) -> str:
    """
    Ensure the date is in the future, adjust if necessary
    """
    from datetime import datetime, timedelta
    
    try:
        # Parse the date
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        current_date = datetime(2025, 9, 27)  # Current date context
        
        # If date is in the past, move to next year
        if date_obj <= current_date:
            # Add one year
            if date_obj.month == 2 and date_obj.day == 29:  # Handle leap year
                date_obj = date_obj.replace(year=date_obj.year + 1, day=28)
            else:
                date_obj = date_obj.replace(year=date_obj.year + 1)
            
            logger.info(f"Date {date_str} was in the past, moved to {date_obj.strftime('%Y-%m-%d')}")
        
        return date_obj.strftime('%Y-%m-%d')
        
    except Exception as e:
        logger.error(f"Error validating date {date_str}: {e}")
        # Return a safe future date
        return "2025-10-15"


def parse_travel_query_with_ai(query: str) -> Dict[str, str]:
    """
    Use OpenAI API to parse travel query and extract standardized location/date info
    """
    from langchain_openai import ChatOpenAI
    import os
    
    try:
        llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0,
            openai_api_key=os.getenv('OPENAI_API_KEY')
        )
        
        prompt = f"""
Parse this travel query and extract the following information in JSON format:

Query: "{query}"

Extract:
1. origin_city: The departure city name (standardized, e.g., "Paris", "New York", "Los Angeles")
2. origin_airport: The main airport code for that city (e.g., "CDG", "JFK", "LAX") 
3. destination_city: The arrival city name (standardized)
4. destination_airport: The main airport code for that city
5. departure_date: Date in YYYY-MM-DD format
6. return_date: Return date in YYYY-MM-DD format (ONLY if return is mentioned, otherwise null for one-way)
7. trip_type: "one-way" or "round-trip" based on whether return is mentioned

Date Parsing Rules:
- ALWAYS parse any date mentioned in the query (e.g., "1 October", "October 1st", "March 15")
- If year not specified, use 2025 or later to ensure future date
- If the parsed date would be in the past, automatically move it to the next year
- Current date context: September 2025
- If month not specified, use current month + 1
- If no date at all is mentioned, use 2025-10-15 as default (future date)
- Examples: "1 October" → "2025-10-01", "March 15th" → "2026-03-15" (next year since March 2025 is past), "next month" → "2025-10-XX"
- NEVER return dates in the past - always ensure departure_date is in the future

Airport Rules:
- Use the most common/main airport for each city
- For cities with multiple airports, choose the largest international one
- Standardize city names (e.g., "NYC" → "New York", "LA" → "Los Angeles")

Return ONLY valid JSON in this format:
{{
  "origin_city": "City Name",
  "origin_airport": "ABC", 
  "destination_city": "City Name",
  "destination_airport": "XYZ",
  "departure_date": "YYYY-MM-DD",
  "return_date": "YYYY-MM-DD or null",
  "trip_type": "one-way or round-trip"
}}

Examples:
- "flight from Paris to Tokyo on March 15" → trip_type: "one-way", return_date: null
- "round trip from NYC to London March 15 returning March 22" → trip_type: "round-trip", return_date: "2026-03-22"
- "flights Paris to Tokyo March 15-20" → trip_type: "round-trip", return_date: "2026-03-20"
"""
        
        response = llm.invoke(prompt)
        
        # Parse the JSON response
        import json
        try:
            result = json.loads(response.content)
            logger.info(f"AI parsed query: {result}")
            return result
        except json.JSONDecodeError:
            logger.error(f"Failed to parse AI response as JSON: {response.content}")
            return None
            
    except Exception as e:
        logger.error(f"Error using AI to parse query: {e}")
        return None


def parse_skyscanner_flights(html: str) -> List[Dict[str, Any]]:
    """
    Parse Skyscanner flight search results from HTML
    """
    soup = BeautifulSoup(html, 'html.parser')
    flights = []
    
    logger.info("Parsing Skyscanner flight results...")
    
    # Skyscanner-specific selectors (updated for current site structure)
    skyscanner_selectors = [
        # Main flight result containers
        {'container': '[data-testid="flight-result"], .FlightResultItem, [data-testid="desktop-flight-card"]'},
        {'container': '.BpkTicket, [role="button"][data-testid]'},
        {'container': '[data-testid*="flight"], [data-testid*="result"]'},
        {'container': '.fqs-flight-result, .flight-result'},
    ]
    
    for selector_config in skyscanner_selectors:
        containers = soup.select(selector_config['container'])
        logger.info(f"Found {len(containers)} flight containers with selector: {selector_config['container']}")
        
        if containers:
            for container in containers[:10]:  # Limit to top 10 results
                try:
                    flight_data = extract_skyscanner_flight_data(container)
                    if flight_data:
                        flights.append(flight_data)
                        
                except Exception as e:
                    logger.debug(f"Error parsing Skyscanner flight container: {e}")
                    continue
            
            if flights:
                logger.info(f"Successfully parsed {len(flights)} flights from Skyscanner")
                break
    
    # If no structured results, try text extraction
    if not flights:
        logger.info("No structured results found, trying text extraction...")
        flights = extract_flights_from_text(html)
    
    return flights


def extract_skyscanner_flight_data(container) -> Dict[str, Any]:
    """
    Extract flight data from a Skyscanner flight container
    """
    import re
    
    flight = {}
    
    # Extract price
    price_selectors = [
        '[data-testid*="price"], .Price, .price',
        '[aria-label*="price"], [title*="price"]',
        'span:contains("€"), span:contains("$"), span:contains("£")'
    ]
    
    for selector in price_selectors:
        price_elem = container.select_one(selector)
        if price_elem:
            price_text = price_elem.get_text(strip=True)
            if re.search(r'[€$£]\s*\d+', price_text):
                flight['price'] = price_text
                break
    
    # Extract airline
    airline_selectors = [
        '[data-testid*="airline"], .airline, .carrier',
        'img[alt*="logo"], img[title]',
        '[aria-label*="airline"], [aria-label*="carrier"]'
    ]
    
    for selector in airline_selectors:
        airline_elem = container.select_one(selector)
        if airline_elem:
            if airline_elem.name == 'img':
                flight['airline'] = airline_elem.get('alt', '') or airline_elem.get('title', '')
            else:
                flight['airline'] = airline_elem.get_text(strip=True)
            if flight['airline']:
                break
    
    # Extract duration
    duration_selectors = [
        '[data-testid*="duration"], .duration, .flight-time',
        '[aria-label*="duration"], [title*="duration"]'
    ]
    
    for selector in duration_selectors:
        duration_elem = container.select_one(selector)
        if duration_elem:
            duration_text = duration_elem.get_text(strip=True)
            if re.search(r'\d+h|\d+:\d+', duration_text):
                flight['duration'] = duration_text
                break
    
    # Extract departure/arrival times
    time_selectors = [
        '[data-testid*="time"], .time, .departure, .arrival',
        '[aria-label*="depart"], [aria-label*="arriv"]'
    ]
    
    times = []
    for selector in time_selectors:
        time_elems = container.select(selector)
        for elem in time_elems:
            time_text = elem.get_text(strip=True)
            if re.search(r'\d{1,2}:\d{2}', time_text):
                times.append(time_text)
    
    if len(times) >= 2:
        flight['departure_time'] = times[0]
        flight['arrival_time'] = times[1]
    
    # Extract stops/layovers
    stops_selectors = [
        '[data-testid*="stop"], .stops, .layover',
        '[aria-label*="stop"], [title*="stop"]'
    ]
    
    for selector in stops_selectors:
        stops_elem = container.select_one(selector)
        if stops_elem:
            stops_text = stops_elem.get_text(strip=True)
            if 'direct' in stops_text.lower() or 'non-stop' in stops_text.lower():
                flight['stops'] = 'Direct'
            elif 'stop' in stops_text.lower():
                flight['stops'] = stops_text
            break
    
    # Only return if we have essential data
    if flight.get('price') or flight.get('airline'):
        return flight
    
    return None


def extract_flights_from_text(html: str) -> List[Dict[str, Any]]:
    """
    Extract flight information from HTML text content as fallback
    """
    import re
    
    flights = []
    
    # Extract prices
    prices = re.findall(r'[€$£¥]\s*\d{2,4}', html)
    
    # Extract durations
    durations = re.findall(r'\d{1,2}h\s*\d{0,2}m?', html)
    
    # Extract times
    times = re.findall(r'\d{1,2}:\d{2}', html)
    
    # Extract common airline names
    airlines = re.findall(r'(Ryanair|EasyJet|Wizz Air|British Airways|Lufthansa|Air France|KLM|Turkish Airlines|Emirates|Qatar Airways|Etihad|Singapore Airlines|Cathay Pacific|ANA|JAL|United|American|Delta)', html, re.IGNORECASE)
    
    # Combine extracted data
    max_results = min(len(prices), 5)  # Limit to 5 results
    
    for i in range(max_results):
        flight = {
            'price': prices[i] if i < len(prices) else 'Price available',
            'airline': airlines[i] if i < len(airlines) else 'Airline available',
            'duration': durations[i] if i < len(durations) else 'Duration available',
        }
        
        if len(times) > i * 2 + 1:
            flight['departure_time'] = times[i * 2]
            flight['arrival_time'] = times[i * 2 + 1]
        
        flights.append(flight)
    
    return flights


def format_skyscanner_results(flights: List[Dict[str, Any]], origin: str, destination: str, departure_date: str, trip_type: str = "one-way", return_date: str = None) -> str:
    """
    Format Skyscanner flight results for display
    """
    from datetime import datetime
    
    if not flights:
        return f"❌ No flights found on Skyscanner for {origin} → {destination} on {departure_date}"
    
    formatted_date = datetime.strptime(departure_date, '%Y-%m-%d').strftime('%B %d, %Y')
    
    if trip_type == 'one-way' or not return_date:
        result = f"✈️ Skyscanner Results: {origin} → {destination} (One-way) on {formatted_date}\n\n"
    else:
        formatted_return = datetime.strptime(return_date, '%Y-%m-%d').strftime('%B %d, %Y')
        result = f"✈️ Skyscanner Results: {origin} → {destination} → {origin} (Round-trip)\n"
        result += f"📅 Outbound: {formatted_date} | Return: {formatted_return}\n\n"
    
    for i, flight in enumerate(flights[:8], 1):  # Show top 8 results
        result += f"{i}. "
        
        if flight.get('airline'):
            result += f"**{flight['airline']}**\n"
        else:
            result += f"**Flight Option {i}**\n"
        
        if flight.get('price'):
            result += f"   💰 **Price:** {flight['price']}\n"
        
        if flight.get('departure_time') and flight.get('arrival_time'):
            result += f"   🕐 **Times:** {flight['departure_time']} → {flight['arrival_time']}\n"
        
        if flight.get('duration'):
            result += f"   ⏱️ **Duration:** {flight['duration']}\n"
        
        if flight.get('stops'):
            result += f"   ✈️ **Route:** {flight['stops']}\n"
        
        result += "\n"
    
    result += "💡 Prices and availability from Skyscanner. Visit Skyscanner.com to book."
    return result

@tool
def search_hotels(query: str) -> str:
    """
    Search for hotel recommendations based on location and preferences.
    
    Args:
        query: Search query like "hotels in Paris" or "luxury hotels Tokyo"
    
    Returns:
        String containing hotel recommendations with names, prices, and ratings
    """
    try:
        # Extract location from query for better URL construction
        location = query.lower()
        if "japan" in location:
            location = "Tokyo, Japan"
        elif "paris" in location:
            location = "Paris, France"
        elif "tokyo" in location:
            location = "Tokyo, Japan"
        elif "kyoto" in location:
            location = "Kyoto, Japan"
        else:
            # Try to extract city name from query
            words = query.split()
            for word in words:
                if len(word) > 3 and word.lower() not in ['hotel', 'hotels', 'cheap', 'budget', 'luxury', 'under', 'in', 'the']:
                    location = word.capitalize()
                    break
        
        encoded_location = quote_plus(location)
        
        # Use more specific URLs that are more likely to work
        urls = [
            f"https://www.booking.com/searchresults.html?ss={encoded_location}&checkin=2024-03-15&checkout=2024-03-16",
            f"https://www.agoda.com/search?city={encoded_location}",
            # Try a simpler approach with basic hotel search
            f"https://www.trivago.com/en/srl?search=200-{encoded_location}"
        ]
        
        all_hotels = []
        
        for url in urls:
            try:
                logger.info(f"Scraping hotels from: {url}")
                # Use Selenium for better results with modern booking sites
                html = scraper.scrape_with_selenium(url)
                
                # If Selenium fails, try direct scraping
                if not html or len(html) < 10000:
                    html = scraper.scrape_with_service(url)
                
                if html:
                    hotels = parse_hotel_results(html)
                    all_hotels.extend(hotels)
                    
                    # If we got good results, break early
                    if len(all_hotels) >= 5:
                        break
                        
            except Exception as e:
                logger.error(f"Error scraping {url}: {e}")
                continue
        
        if not all_hotels:
            # Provide helpful fallback information
            return f"""Sorry, I couldn't retrieve real-time hotel information for '{query}' due to website restrictions. 

Here are some general recommendations for finding hotels in Japan under $100:

🏨 **Budget Hotel Options:**
1. **Business Hotels** - Clean, efficient rooms typically $50-80/night
2. **Capsule Hotels** - Unique experience, $25-50/night  
3. **Hostels** - Shared accommodations, $20-40/night
4. **Ryokans (Budget)** - Traditional inns, $60-100/night

💡 **Recommended Booking Sites:**
- Booking.com - Wide selection with free cancellation
- Agoda - Good deals in Asia
- Hotels.com - Loyalty rewards program
- Rakuten Travel - Popular in Japan

🗾 **Best Areas for Budget Hotels:**
- **Tokyo**: Asakusa, Ueno, Ikebukuro
- **Osaka**: Namba, Tennoji, Sumiyoshi  
- **Kyoto**: Near train stations, Gion area

Please check these sites directly for current prices and availability."""
        
        # Format results
        result = f"🏨 Hotel Recommendations for '{query}':\n\n"
        
        for i, hotel in enumerate(all_hotels[:8], 1):  # Show top 8 results
            result += f"{i}. **{hotel['name']}**\n"
            result += f"   💰 Price: {hotel['price']}\n"
            result += f"   ⭐ Rating: {hotel['rating']}\n\n"
        
        result += "\n💡 Tip: Prices and availability may vary. Please check the booking sites directly for the most current information."
        
        return result
        
    except Exception as e:
        logger.error(f"Error in search_hotels: {e}")
        return f"An error occurred while searching for hotels: {str(e)}"

@tool
def search_flights(query: str) -> str:
    """
    Search for flight recommendations based on route and preferences.
    
    Args:
        query: Search query like "flights from NYC to Paris" or "cheap flights London Tokyo"
    
    Returns:
        String containing flight recommendations with airlines, prices, and durations
    """
    try:
        # Use AI to parse the travel query
        parsed_data = parse_travel_query_with_ai(query)
        
        if parsed_data:
            origin = parsed_data.get('origin_airport', 'CDG')
            destination = parsed_data.get('destination_airport', 'AMS') 
            departure_date = parsed_data.get('departure_date', '2025-10-15')
            return_date = parsed_data.get('return_date')
            trip_type = parsed_data.get('trip_type', 'one-way')
            
            # Validate departure date is in the future
            departure_date = validate_future_date(departure_date)
            
            # Only validate return date if it exists (round-trip)
            if return_date:
                return_date = validate_future_date(return_date)
            else:
                trip_type = 'one-way'
                
        else:
            # Fallback to defaults if AI parsing fails
            logger.warning("AI parsing failed, using defaults")
            origin = "CDG"
            destination = "AMS"
            departure_date = "2025-10-15"
            return_date = None
            trip_type = "one-way"
        
        # Generate Skyscanner URL based on trip type
        if trip_type == 'one-way' or not return_date:
            # One-way flight URL
            skyscanner_url = f"https://www.skyscanner.com/transport/flights/{origin.lower()}/{destination.lower()}/{departure_date.replace('-', '')}/"
            logger.info(f"Searching for one-way flight: {origin} → {destination}")
        else:
            # Round-trip flight URL
            skyscanner_url = f"https://www.skyscanner.com/transport/flights/{origin.lower()}/{destination.lower()}/{departure_date.replace('-', '')}/{return_date.replace('-', '')}/"
            logger.info(f"Searching for round-trip flight: {origin} → {destination} → {origin}")
        
        # Scrape only from Skyscanner using Lightpanda
        try:
            logger.info(f"Scraping flights from Skyscanner: {skyscanner_url}")
            # Use Lightpanda API for professional scraping
            html = scraper.scrape_with_service(skyscanner_url)
            
            if html:
                flights = parse_skyscanner_flights(html)
                if flights:
                    return format_skyscanner_results(flights, origin, destination, departure_date, trip_type, return_date)
                        
        except Exception as e:
            logger.error(f"Error scraping Skyscanner: {e}")
        
        # If no results from Skyscanner, return informative error message
        from datetime import datetime
        formatted_date = datetime.strptime(departure_date, '%Y-%m-%d').strftime('%B %d, %Y')
        
        return f"""❌ Unable to retrieve flight data from Skyscanner for {origin} → {destination} on {formatted_date}.

This could be due to:
• No direct flights available on this route
• Limited flight data for this specific date
• Website access restrictions

💡 **Suggestions:**
• Try searching for flights with connections (e.g., via Dubai, Istanbul, or Singapore)
• Check alternative dates around {formatted_date}
• Consider nearby airports or different airlines
• Visit Skyscanner.com directly for more options

If you have other travel queries, I'm happy to help!"""
        
        return result
        
    except Exception as e:
        logger.error(f"Error in search_flights: {e}")
        return f"An error occurred while searching for flights: {str(e)}"

@tool
def search_hotels(query: str) -> str:
    """
    Search for hotel recommendations from Booking.com and Airbnb only.
    
    Args:
        query: Search query like "hotels in paris" or "luxury hotels Tokyo"
    
    Returns:
        String containing hotel recommendations with names, prices, and ratings
    """
    try:
        # Use AI to parse the hotel query
        location = parse_hotel_query_with_ai(query)
        
        # Try Booking.com first
        booking_url = f"https://www.booking.com/searchresults.html?ss={quote_plus(location)}"
        
        try:
            logger.info(f"Scraping hotels from Booking.com: {booking_url}")
            # Use Lightpanda API for professional scraping
            html = scraper.scrape_with_service(booking_url)
            
            if html:
                hotels = parse_booking_hotels(html)
                if hotels:
                    return format_hotel_results(hotels, location, "Booking.com")
                        
        except Exception as e:
            logger.error(f"Error scraping Booking.com: {e}")
        
        # Try Airbnb as fallback
        airbnb_url = f"https://www.airbnb.com/s/{quote_plus(location)}/homes"
        
        try:
            logger.info(f"Scraping accommodations from Airbnb: {airbnb_url}")
            # Use Lightpanda API for professional scraping
            html = scraper.scrape_with_service(airbnb_url)
            
            if html:
                accommodations = parse_airbnb_listings(html)
                if accommodations:
                    return format_hotel_results(accommodations, location, "Airbnb")
                        
        except Exception as e:
            logger.error(f"Error scraping Airbnb: {e}")
        
        # If no results from either site
        return f"❌ Unable to retrieve hotel data from Booking.com or Airbnb for {location}. Please try again later."
        
    except Exception as e:
        logger.error(f"Error in search_hotels: {e}")
        return f"An error occurred while searching for hotels: {str(e)}"


def parse_hotel_query_with_ai(query: str) -> str:
    """
    Use OpenAI API to parse hotel query and extract standardized location
    """
    from langchain_openai import ChatOpenAI
    import os
    
    try:
        llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0,
            openai_api_key=os.getenv('OPENAI_API_KEY')
        )
        
        prompt = f"""
Parse this hotel search query and extract the location in a format that Booking.com and Airbnb would understand:

Query: "{query}"

Rules:
- Extract the main city/location name
- Standardize city names (e.g., "NYC" → "New York", "LA" → "Los Angeles")
- Remove words like "hotels", "accommodation", "stay", "luxury", "cheap", "budget"
- Return just the clean city name that booking sites would recognize
- For neighborhoods, include both city and area (e.g., "Paris Montmartre", "New York Manhattan")

Return ONLY the clean location name, nothing else.
Examples:
- "luxury hotels in Paris" → "Paris"
- "cheap accommodation NYC" → "New York" 
- "hotels near Times Square" → "New York Times Square"
- "stay in Tokyo Shibuya" → "Tokyo Shibuya"
"""
        
        response = llm.invoke(prompt)
        location = response.content.strip().strip('"')
        logger.info(f"AI parsed hotel location: '{query}' → '{location}'")
        return location
        
    except Exception as e:
        logger.error(f"Error using AI to parse hotel query: {e}")
        # Fallback to simple extraction
        location = query.lower()
        for word in ['hotels', 'hotel', 'in', 'at', 'near', 'luxury', 'cheap', 'budget', 'accommodation', 'stay']:
            location = location.replace(word, '')
        return location.strip()


def parse_booking_hotels(html: str) -> List[Dict[str, Any]]:
    """Parse Booking.com hotel results"""
    soup = BeautifulSoup(html, 'html.parser')
    hotels = []
    
    # Booking.com specific selectors
    hotel_selectors = [
        '[data-testid="property-card"]',
        '.sr_property_block',
        '[data-testid="title"]'
    ]
    
    for selector in hotel_selectors:
        containers = soup.select(selector)
        logger.info(f"Found {len(containers)} hotel containers with selector: {selector}")
        
        if containers:
            for container in containers[:8]:
                try:
                    hotel = extract_booking_hotel_data(container)
                    if hotel:
                        hotels.append(hotel)
                except Exception as e:
                    logger.debug(f"Error parsing hotel container: {e}")
                    continue
            
            if hotels:
                break
    
    return hotels


def extract_booking_hotel_data(container) -> Dict[str, Any]:
    """Extract hotel data from Booking.com container"""
    import re
    
    hotel = {}
    
    # Extract hotel name
    name_selectors = [
        '[data-testid="title"], .sr-hotel__name, h3, h4',
        '.property-card-header__title'
    ]
    
    for selector in name_selectors:
        name_elem = container.select_one(selector)
        if name_elem:
            hotel['name'] = name_elem.get_text(strip=True)
            break
    
    # Extract price
    price_selectors = [
        '[data-testid="price"], .bui-price-display__value, .sr-hotel__price',
        '.property-card-pricing__value'
    ]
    
    for selector in price_selectors:
        price_elem = container.select_one(selector)
        if price_elem:
            price_text = price_elem.get_text(strip=True)
            if re.search(r'[€$£]\s*\d+', price_text):
                hotel['price'] = price_text
                break
    
    # Extract rating
    rating_selectors = [
        '[data-testid="review-score"], .bui-review-score__badge',
        '.sr-hotel__review-score'
    ]
    
    for selector in rating_selectors:
        rating_elem = container.select_one(selector)
        if rating_elem:
            rating_text = rating_elem.get_text(strip=True)
            if re.search(r'\d+\.?\d*', rating_text):
                hotel['rating'] = rating_text
                break
    
    return hotel if hotel.get('name') else None


def parse_airbnb_listings(html: str) -> List[Dict[str, Any]]:
    """Parse Airbnb listing results"""
    soup = BeautifulSoup(html, 'html.parser')
    listings = []
    
    # Airbnb specific selectors
    listing_selectors = [
        '[data-testid="listing-card"]',
        '[itemprop="itemListElement"]',
        '.listing-card'
    ]
    
    for selector in listing_selectors:
        containers = soup.select(selector)
        logger.info(f"Found {len(containers)} Airbnb containers with selector: {selector}")
        
        if containers:
            for container in containers[:8]:
                try:
                    listing = extract_airbnb_listing_data(container)
                    if listing:
                        listings.append(listing)
                except Exception as e:
                    logger.debug(f"Error parsing Airbnb container: {e}")
                    continue
            
            if listings:
                break
    
    return listings


def extract_airbnb_listing_data(container) -> Dict[str, Any]:
    """Extract listing data from Airbnb container"""
    import re
    
    listing = {}
    
    # Extract listing title
    title_selectors = [
        '[data-testid="listing-card-title"]',
        '.listing-card-title',
        'h3, h4'
    ]
    
    for selector in title_selectors:
        title_elem = container.select_one(selector)
        if title_elem:
            listing['name'] = title_elem.get_text(strip=True)
            break
    
    # Extract price
    price_selectors = [
        '[data-testid="price"]',
        '.listing-card-price',
        'span:contains("$"), span:contains("€")'
    ]
    
    for selector in price_selectors:
        price_elem = container.select_one(selector)
        if price_elem:
            price_text = price_elem.get_text(strip=True)
            if re.search(r'[€$£]\s*\d+', price_text):
                listing['price'] = price_text
                break
    
    # Extract rating
    rating_selectors = [
        '[data-testid="listing-card-rating"]',
        '.listing-card-rating'
    ]
    
    for selector in rating_selectors:
        rating_elem = container.select_one(selector)
        if rating_elem:
            rating_text = rating_elem.get_text(strip=True)
            if re.search(r'\d+\.?\d*', rating_text):
                listing['rating'] = rating_text
                break
    
    return listing if listing.get('name') else None


def format_hotel_results(accommodations: List[Dict[str, Any]], location: str, source: str) -> str:
    """Format hotel/accommodation results for display"""
    if not accommodations:
        return f"❌ No accommodations found on {source} for {location}"
    
    result = f"🏨 {source} Results for {location}:\n\n"
    
    for i, accommodation in enumerate(accommodations[:8], 1):
        result += f"{i}. **{accommodation.get('name', 'Accommodation')}**\n"
        
        if accommodation.get('price'):
            result += f"   💰 **Price:** {accommodation['price']}\n"
        
        if accommodation.get('rating'):
            result += f"   ⭐ **Rating:** {accommodation['rating']}\n"
        
        result += "\n"
    
    result += f"💡 Prices and availability from {source}. Visit {source.lower().replace('.', '')}.com to book."
    return result

# Export all tools
__all__ = ['search_hotels', 'search_flights']
