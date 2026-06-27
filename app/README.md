# Email Summarizer

This project is a web application that summarizes emails using a Flask backend and a simple frontend built with HTML, CSS, and JavaScript. The application allows users to connect their email accounts and retrieve summaries of their emails.

## Project Structure

```
email-summarizer
├── app.py                # Main entry point of the Flask application
├── requirements.txt      # Lists the dependencies required for the project
├── templates
│   └── index.html       # HTML structure of the web application
├── static
│   ├── css
│   │   └── styles.css    # CSS styles for the web application
│   └── js
│       └── script.js     # JavaScript logic for the web application
└── README.md             # Documentation for the project
```

## Setup Instructions

1. **Clone the repository:**
   ```
   git clone <repository-url>
   cd email-summarizer
   ```

2. **Create a virtual environment:**
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install the required dependencies:**
   ```
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```
   python app.py
   ```

5. **Access the application:**
   Open your web browser and go to `http://127.0.0.1:5000`.

## Usage Guidelines

- Click on the "Connect Gmail" or "Connect Outlook" buttons to link your email account.
- After connecting, click on the "Summarize My 24hr Emails" button to retrieve a summary of your emails.
- If there are any issues, an error message will be displayed.

## Contributing

Feel free to submit issues or pull requests if you have suggestions or improvements for the project.