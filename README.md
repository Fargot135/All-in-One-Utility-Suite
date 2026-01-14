# 🎯 PET-project - Multifunctional Desktop Application

A desktop application built with Python and Tkinter that combines weather forecasting, idea management, and workout planning features with an animated wave background.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![tkinter](https://img.shields.io/badge/GUI-Tkinter-orange.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

---

## 📋 Table of Contents

- [Features](#-features)
- [Installation](#-installation)
- [Usage](#-usage)
- [Project Structure](#-project-structure)
- [Technologies Used](#-technologies-used)
- [API Configuration](#-api-configuration)
- [Future Improvements](#-future-improvements)
- [Notes](#-notes)
- [Contributing](#-contributing)
- [Author](#-author)
- [Acknowledgments](#-acknowledgments)

---

## ✨ Features

### 🌤️ Weather Forecast

- Real-time weather data using OpenWeatherMap API
- Current weather conditions with temperature, humidity, and wind speed
- 3-day weather forecast
- Visual weather icons
- Support for any city worldwide

### 💡 Idea Randomizer

- Add and store your ideas or options
- Random selection from saved ideas
- Persistent storage in text file
- Perfect for decision-making

### 🏋️ Training Programs

Three different workout programs:

- **Split Training** - 3-day split focusing on different muscle groups
- **Full Body** - Complete body workouts 3 times per week
- **Upper/Lower** - Upper and lower body split routine

Each program includes:

- Detailed exercise lists
- Sets and reps recommendations
- Animated text display

### 🎨 UI Features

- Animated gradient wave background
- Smooth hover animations on buttons
- Custom icon animations
- Modern dark theme design
- Responsive layout

---

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Step 1: Clone the repository

```bash
git clone https://github.com/Fargot135/All-in-One-Utility-Suite
cd pet-project
```

### Step 2: Install required packages

```bash
pip install -r requirements.txt
```

### Step 3: Create required directories

```bash
mkdir images
```

### Step 4: Add icon images

Place the following images in the `images/` folder:

- `weather.png` - Weather icon
- `cube.png` - Idea/randomizer icon
- `dumbbell.png` - Training icon

### Step 5: Configure API key

1. Get a free API key from [OpenWeatherMap](https://openweathermap.org/api)
2. Open the Python file and replace `YOUR_API_KEY_HERE` with your actual API key:

```python
api_key = "your_actual_api_key_here"
```

---

## 💻 Usage

### Run the application

```bash
python "All-in-One Utility Suite.py"
```

### Weather Function

1. Click the "weather" button
2. Enter city name
3. Click "Get Weather" or press Enter
4. View current weather and 3-day forecast

### Randomizer Function

1. Click the "randomiser" button
2. Type your idea/option in the text field
3. Click "Add a variant" or press Enter to save
4. Click "Random selection" to get a random idea

### Training Function

1. Click the "training" button
2. Choose one of three programs:
   - Split
   - Full Body
   - Upper/Lower
3. View detailed workout plan with exercises and sets/reps

---

## 📁 Project Structure

```
pet-project/
│
├── All-in-One Utility Suite.py    # Main application file
├── How.txt                         # Storage for randomizer ideas
├── requirements.txt                # Python dependencies
├── README.md                       # Project documentation
│
└── images/                         # Icon images folder
    ├── weather.png
    ├── cube.png
    └── dumbbell.png
```

---

## 🛠️ Technologies Used

- **Python 3.8+** - Core programming language
- **Tkinter** - Standard GUI framework
- **CustomTkinter** - Modern UI components
- **Pillow (PIL)** - Image processing
- **Requests** - HTTP requests for API calls
- **OpenWeatherMap API** - Weather data source

### Key Libraries

```python
tkinter          # GUI framework
customtkinter    # Modern UI components
PIL              # Image handling
requests         # API requests
```

---

## 🔑 API Configuration

The project uses OpenWeatherMap API for weather data:

1. Register at [OpenWeatherMap](https://openweathermap.org/api)
2. Get your free API key
3. Replace in code:

```python
api_key = "YOUR_API_KEY_HERE"  # Line ~313
```

**Note:** Free tier allows 60 calls/minute and 1,000,000 calls/month

---

## 🚧 Future Improvements

- [ ] Add database support instead of text files
- [ ] Implement user settings and preferences
- [ ] Add more training programs
- [ ] Add progress tracking for workouts
- [ ] Implement weather alerts and notifications
- [ ] Add unit tests
- [ ] Create installer for easy distribution
- [ ] Multi-language support
- [ ] Dark/Light theme toggle

---

## 📝 Notes

- The `How.txt` file is created automatically on first use
- Weather icons are fetched dynamically from OpenWeatherMap
- All images must be placed in the `images/` folder
- The application window is non-resizable by design

---

## 🤝 Contributing

This is a personal learning project, but suggestions and feedback are welcome!

---

## 👤 Author

**Ivan Kachmar**

- GitHub: [@Fargot135](https://github.com/Fargot135)
- LinkedIn: [Ivan Kachmar](https://linkedin.com/in/ivan-kachmar)

---

## 🙏 Acknowledgments

- OpenWeatherMap for providing free weather API
- CustomTkinter library for modern UI components
- Python community for excellent documentation

---

<div align="center">

**Made with ❤️ as a learning project**

</div>  