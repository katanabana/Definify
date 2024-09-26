# Definify

Definify is an engaging and interactive word-guessing game designed for groups of players. The objective is to describe randomly generated words to teammates within a limited timeframe. Each successful guess earns the team points, fostering both fun and a competitive spirit. The web application supports multiple players and real-time interaction, making it a perfect game for friends, family, or colleagues.

## Setup Instructions

### 1. Clone the Repository
Clone the repository to your local machine:

```bash
git clone https://github.com/yourusername/definify.git
cd definify
```

### 2. Install Dependencies
Install the required packages from `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Create a `.env` file in the root directory of the project and add necessary environment variables (see `.env.example`).

### 4. Set Up the Database
Run the following command to initialize the database:

```bash
python setup_db.py
```

### 5. Run the Application
Start the web application by launching `main.py`:

```bash
python main.py
```

The application should now be running on the address and port specified in `.env`.

## Dependencies

The following Python packages are required to run the application:

- **Flask**: A lightweight WSGI web application framework.
- **requests**: HTTP library for making API requests.
- **SQLAlchemy**: SQL toolkit and ORM for database interactions.
- **Flask-Login**: User session management and authentication.
- **Flask-WTF**: Forms and CSRF protection.
- **Flask-SocketIO**: Enables real-time communication using WebSockets.
- **python-dotenv**: Reads environment variables from `.env` files.

These dependencies are listed in `requirements.txt` and can be installed using `pip`.
