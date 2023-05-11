import requests

# Add Weather API key below
API_KEY = ''

latitude, longitude = 51.37965983469745, -2.3280695029215726  # Uni of Bath coordinates
url = f'http://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={API_KEY}'


# location = 'SW1A 1AA'  # UK postcode example
# url = f'http://api.openweathermap.org/data/2.5/weather?q={location}&appid={API_KEY}'


response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    temperature = data['main']['temp'] - 273.15  # Convert from Kelvin to Celsius
    weather = data['weather'][0]['description']
    print(f'Temperature: {temperature}°C')
    print(f'Weather: {weather}')
else:
    print(f'Error fetching weather data: {response.status_code}')

