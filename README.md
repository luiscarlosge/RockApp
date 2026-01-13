# Rock and Roll Forum - Jam en Español 🎸

A responsive Flask web application designed for musicians to view song assignments and setlists with full Spanish language support. Perfect for managing band rehearsals, jam sessions, and live performances.

## 🎵 Features

- **Song Selector Interface**: Browse and view detailed song assignments with musician roles
- **Musician View**: See all songs assigned to a specific musician with their instruments
- **Global Selector**: Comprehensive view of all songs and musicians in the setlist
- **Spanish Language Support**: Full Spanish translations for UI and error messages
- **Order Management**: Songs displayed in performance order with "next song" navigation
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices
- **Error Handling**: Comprehensive error handling with retry mechanisms and circuit breakers
- **Performance Optimized**: Response caching and efficient data processing
- **Azure Ready**: Configured for deployment on Azure App Service

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd rock-and-roll-forum
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python app.py
   ```

4. **Open your browser**
   Navigate to `http://localhost:5000`

## 📁 Project Structure

```
rock-and-roll-forum/
├── app.py                      # Main Flask application
├── csv_data_processor.py       # Data processing and CSV handling
├── spanish_translations.py     # Spanish language translations
├── Data.csv                    # Song and musician assignment data
├── requirements.txt            # Python dependencies
├── static/                     # Static assets (CSS, JavaScript)
│   ├── css/
│   │   └── style.css          # Application styles
│   └── js/
│       ├── app.js             # Main application logic
│       ├── error-handler.js   # Error handling utilities
│       └── navigation-state-manager.js
├── templates/                  # HTML templates
│   ├── base.html              # Base template
│   ├── index.html             # Main song selector page
│   └── global-selector.html   # Global view page
├── tests/                      # Test files and test documentation
│   ├── README.md              # Test documentation
│   ├── integration_test.py    # Integration tests
│   ├── test_complete_workflows.py # End-to-end tests
│   └── ...                    # Additional test files
├── docs/                       # Documentation and deployment guides
│   ├── README.md              # Documentation index
│   ├── AZURE_DEPLOYMENT_GUIDE.md # Azure deployment guide
│   ├── azure_deployment/      # Azure deployment package
│   └── ...                    # Additional documentation
└── .kiro/                      # Kiro specs and configuration
    └── specs/                  # Feature specifications
```

## 🎯 Usage

### Song Selector View
- Select a song from the dropdown to view musician assignments
- See which instruments each musician plays for that song
- Navigate to the next song in the setlist

### Musician View
- Select a musician from the dropdown to view all their song assignments
- See all instruments they play across different songs
- View songs in performance order

### Global Selector
- View all songs and musicians in a comprehensive table
- See the complete setlist with order numbers
- Quick reference for the entire performance

## 🔧 Configuration

### Environment Variables

- `SECRET_KEY`: Flask secret key for session management (required in production)
- `FLASK_ENV`: Environment mode (`development` or `production`)
- `FLASK_DEBUG`: Enable debug mode (`True` or `False`)
- `PORT`: Port number for the application (default: 5000)

### Data Format

The application reads song assignments from `Data.csv` with the following columns:
- `Order`: Performance order number
- `Artist`: Song artist name
- `Song`: Song title
- `Musician columns`: One column per musician with their instrument assignments

## 🌐 Deployment

### Azure App Service

The application is configured for Azure App Service deployment. See the [Azure Deployment Guide](docs/AZURE_DEPLOYMENT_GUIDE.md) for detailed instructions.

Quick deployment:
```bash
# Using the deployment script
./docs/deploy_linux.sh
```

### Docker

Build and run with Docker:
```bash
docker build -t rock-and-roll-forum .
docker run -p 5000:5000 rock-and-roll-forum
```

## 🧪 Testing

Run the test suite:
```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python tests/test_complete_workflows.py

# Run deployment tests
python tests/simple_deployment_test.py
```

See the [Tests Documentation](tests/README.md) for more details.

## 🛠️ Development

### Adding New Features

1. Update the data model in `csv_data_processor.py`
2. Add API endpoints in `app.py`
3. Update frontend logic in `static/js/app.js`
4. Add Spanish translations in `spanish_translations.py`
5. Update templates as needed

### Code Style

- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add docstrings to all functions and classes
- Include error handling for all external operations

## 📊 API Endpoints

- `GET /` - Main song selector interface
- `GET /global-selector` - Global view interface
- `GET /api/songs` - Get all songs (sorted by order)
- `GET /api/song/<song_id>` - Get song details with musician assignments
- `GET /api/musicians` - Get all musicians
- `GET /api/musician/<musician_id>` - Get musician details with song assignments
- `GET /api/health` - System health check

## 🌍 Internationalization

The application currently supports:
- **Spanish (Español)**: Full UI and error message translations
- **English**: API responses and internal processing

To add more languages, extend the `spanish_translations.py` module.

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with Flask and modern web technologies
- Spanish translations for accessibility
- Designed for real-world musician collaboration

## 📧 Support

For issues, questions, or suggestions, please open an issue on GitHub.

---

**Made with ❤️ for musicians everywhere**
