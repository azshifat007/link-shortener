# Link Shortener Application

This application is a simple yet powerful URL shortening service built with Flask. It includes user authentication, URL analytics, and a dashboard for managing shortened URLs.

## Features

1. **URL Shortening**: Quickly shorten any URL.
2. **User Authentication**:
   - Register and log in to access personalized features.
   - Secure user sessions.
3. **Dashboard**:
   - View all shortened URLs.
   - Track the number of clicks for each URL.
4. **Analytics**:
   - View click counts for each shortened URL.
5. **Responsive Design**:
   - Modern and clean interface using Bootstrap.

## Setup

### Prerequisites
- Python 3.7+
- Flask

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/link-shortener.git
   cd link-shortener
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Initialize the database:
   ```bash
   python app.py
   ```

4. Run the application:
   ```bash
   flask run
   ```

5. Access the app at [http://127.0.0.1:5000](http://127.0.0.1:5000).

## Usage

1. **Register**: Create an account by visiting the registration page.
2. **Login**: Log in to your account to access the dashboard.
3. **Shorten URLs**: Submit a URL to generate a shortened version.
4. **Dashboard**:
   - View your shortened URLs.
   - Check click statistics.

## Folder Structure
```
link-shortener/
├── app.py             # Main application
├── templates/         # HTML templates
├── static/            # Static files (CSS, JS, etc.)
├── database.db        # SQLite database
├── README.md          # Documentation
└── LICENSE            # License file
```

## Contributing

1. Fork the repository.
2. Create a new branch for your feature:
   ```bash
   git checkout -b feature-name
   ```
3. Commit your changes and push:
   ```bash
   git commit -m "Add feature-name"
   git push origin feature-name
   ```
4. Create a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

