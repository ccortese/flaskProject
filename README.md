# Flask Project

A simple Flask web application with user authentication and basic functionality.

## Features

- User registration and login
- Homepage with user dashboard
- Session management
- SQLite database integration

## Setup

1. Install dependencies:
```bash
pip install flask flask-sqlalchemy
```

2. Run the application:
```bash
python app.py
```

3. Visit `http://localhost:5000` in your browser

## Project Structure

- `app.py` - Main Flask application
- `models.py` - Database models
- `templates/` - HTML templates
- `static/` - CSS and JavaScript files

## Database

The application uses SQLite for data storage. The database file `users.db` will be created automatically when you first run the application.

## Routes

- `/` - Homepage
- `/login` - User login
- `/register` - User registration
- `/logout` - User logout

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is open source and available under the MIT License.
