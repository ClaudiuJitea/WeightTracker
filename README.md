# ⚖️ WeightTracker - Personal Weight Management System

![HealthTracker Dashboard](https://github.com/ClaudiuJitea/WeightTracker/blob/main/app/static/images/screen01.png?raw=true)

![HealthTracker Features](https://github.com/ClaudiuJitea/WeightTracker/blob/main/app/static/images/screen02.png?raw=true)

A comprehensive weight tracking web application with additional features for calories and fasting monitoring. Built with Flask and featuring a modern, responsive design with dark mode support.

## ✨ Features

### 📊 Weight Management
- **Weight Tracking**: Log daily weight entries with automatic BMI calculation
- **Smart Goal Setting**: Choose from preset weight loss plans (Steady, Aggressive, Moderate) or set custom targets
- **Progress Visualization**: Interactive charts showing weight trends and goal progress
- **Daily/Weekly/Monthly Goals**: Automatic calculation of required weight loss rates

### 🍽️ Nutrition Tracking
- **Calorie Calculator**: Track daily caloric intake with food entries
- **Macro Tracking**: Monitor protein, carbohydrates, fat, and fiber intake
- **TDEE Calculator**: Calculate Total Daily Energy Expenditure based on activity level
- **Meal Distribution**: Analyze calorie distribution across breakfast, lunch, and dinner
- **Progress Monitoring**: Visual progress bars and nutritional breakdowns

### ⏱️ Intermittent Fasting
- **Fasting Timer**: Start, pause, and complete fasting sessions
- **Multiple Fasting Types**: Support for various fasting protocols (16:8, 18:6, 20:4, 24h, 36h, 48h, 72h)
- **Fasting History**: Track completed fasting sessions with duration and achievements
- **Real-time Tracking**: Live timer showing current fasting progress

### 👤 User Management
- **User Authentication**: Secure registration and login system
- **Profile Management**: Update personal information including height for BMI calculations
- **Admin Dashboard**: Administrative interface for user management
- **Dark Mode**: Toggle between light and dark themes

### 📱 Modern UI/UX
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices
- **Dark Mode Support**: Eye-friendly dark theme option
- **Interactive Charts**: Beautiful visualizations using Chart.js
- **Intuitive Navigation**: Clean, modern interface with easy navigation

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/ClaudiuJitea/WeightTracker.git
   cd WeightTracker
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv myenv
   
   # On Windows
   myenv\Scripts\activate
   
   # On macOS/Linux
   source myenv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   # Copy the example environment file
   cp .env.example .env
   
   # Edit .env and set your SECRET_KEY
   # Generate a secure key with: python -c "import secrets; print(secrets.token_hex(32))"
   ```

5. **Initialize the database**
   ```bash
   flask db upgrade
   ```

6. **Create an admin user (optional)**
   ```bash
   python create_admin.py
   ```

7. **Run the application**
   ```bash
   python run.py
   ```

8. **Access the application**
   - Open your browser and go to `http://127.0.0.1:5000`
   - Register a new account or use the admin credentials if created

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
FLASK_APP=run.py
FLASK_DEBUG=0
SECRET_KEY=your-secret-key-here
```

### Database Configuration

By default, the application uses SQLite. For production, consider using PostgreSQL:

```env
DATABASE_URL=postgresql://username:password@localhost/healthtrack
```

## 📁 Project Structure

```
WeightTracker/
├── app/
│   ├── admin/          # Admin panel functionality
│   ├── auth/           # Authentication (login/register)
│   ├── calories/       # Calorie and nutrition tracking
│   ├── fasting/        # Intermittent fasting features
│   ├── main/           # Main routes and dashboard
│   ├── weight/         # Weight tracking functionality
│   ├── static/         # CSS, JS, and images
│   ├── templates/      # HTML templates
│   └── models.py       # Database models
├── migrations/         # Database migration files
├── .env.example        # Environment variables template
├── config.py          # Application configuration
├── requirements.txt   # Python dependencies
└── run.py            # Application entry point
```

## 🎯 Usage Guide

### Getting Started
1. **Register an Account**: Create your personal account
2. **Set Up Profile**: Add your height for BMI calculations
3. **Log Initial Weight**: Record your starting weight
4. **Set Goals**: Choose a weight goal using preset options or custom targets
5. **Start Tracking**: Begin logging your daily activities

### Weight Tracking
- Log daily weight entries from the Weight Tracker page
- Set realistic goals using the built-in calculators
- Monitor progress with interactive charts
- View detailed statistics and trends

### Calorie Tracking
- Use the Calorie Calculator to log food intake
- Set daily calorie goals based on your TDEE
- Track macronutrients (protein, carbs, fat, fiber)
- Monitor meal distribution throughout the day

### Fasting Sessions
- Start fasting sessions from the Fasting Tracker
- Choose from preset fasting durations or set custom times
- Monitor real-time progress with the built-in timer
- Review fasting history and achievements

## 🛠️ Development

### Running in Development Mode

```bash
# Set debug mode
export FLASK_DEBUG=1  # On Windows: set FLASK_DEBUG=1

# Run with auto-reload
python run.py
```

### Database Migrations

```bash
# Create a new migration
flask db migrate -m "Description of changes"

# Apply migrations
flask db upgrade

# Downgrade if needed
flask db downgrade
```

### Adding New Features

1. Create new blueprints in the `app/` directory
2. Add routes, forms, and templates
3. Update the database models if needed
4. Create and apply migrations
5. Update tests and documentation

## 🔒 Security Features

- **Password Hashing**: Secure password storage using Werkzeug
- **CSRF Protection**: Forms protected against cross-site request forgery
- **Session Management**: Secure user session handling
- **Input Validation**: Comprehensive form validation
- **Admin Controls**: Separate admin interface with user management

## 🚀 Deployment

### Production Deployment

1. **Set Production Environment**
   ```bash
   export FLASK_DEBUG=0
   export SECRET_KEY="your-production-secret-key"
   ```

2. **Use Production Database**
   ```bash
   export DATABASE_URL="postgresql://user:pass@localhost/healthtrack"
   ```

3. **Use Production WSGI Server**
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:8000 run:app
   ```

### Docker Deployment (Optional)

Create a `Dockerfile` for containerized deployment:

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "run:app"]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Flask**: The web framework that powers this application
- **Chart.js**: For beautiful, responsive charts
- **Tailwind CSS**: For the modern, responsive design
- **Font Awesome**: For the comprehensive icon library

## 📞 Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/ClaudiuJitea/WeightTracker/issues) page
2. Create a new issue if your problem isn't already reported
3. Provide detailed information about your environment and the issue

## 🔄 Changelog

### Version 1.0.0
- Initial release
- Weight tracking with goal setting
- Calorie and nutrition tracking
- Intermittent fasting timer
- Admin dashboard
- Dark mode support
- Responsive design

---

**Made with ❤️ for health and fitness enthusiasts**