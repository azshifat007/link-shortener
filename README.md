Link Shortener

A simple web application that converts long URLs into short, shareable links. The app also supports redirection from short links to the original URLs.

Features
Generate short URLs for any valid long URL.
Redirect users to the original URL using the short URL.
Track stored links in a database for persistence.
User-friendly web interface for shortening links.
Technologies Used
Frontend: HTML, CSS (basic styling).
Backend: Python with Flask.
Database: SQLite for storing original URLs and their corresponding short codes.

How It Works
A user enters a long URL into the input form.
The application checks if the URL is already shortened:
If yes, the existing short URL is displayed.
If no, a unique short code is generated, saved in the database, and displayed.
When a user visits the short URL, the app retrieves the original URL from the database and redirects them.
Setup and Installation

Prerequisites

Python 3.x installed on your system.
Flask library installed. You can install Flask by running:

pip install flask

Steps

Clone this repository: git clone https://github.com/azshifat007/link-shortener.git

cd link-shortener
Initialize the database:

python app.py
This creates the database.db file with the required tables.

Run the Flask development server:

python app.py
Open your browser and navigate to:

http://127.0.0.1:5000/

Usage

Enter a long URL into the input field.
Click the "Shorten" button to generate a short URL.
Use the short URL to redirect to the original URL.

Example

Input: https://www.example.com/very-long-url
Output: http://127.0.0.1:5000/abc123
Visiting http://127.0.0.1:5000/abc123 will redirect to https://www.example.com/very-long-url.

Future Improvements
Add user accounts for managing personal short links.
Implement analytics for tracking clicks on short URLs.
Support custom short codes.
Deploy the application to a live server (e.g., Heroku, AWS).
License
This project is open-source and available under the GPL 3.0 License.
