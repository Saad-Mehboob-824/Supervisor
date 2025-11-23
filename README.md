# Sleep Optimizer Supervisor Agent

A Supervisor Agent for managing users, coordinating with the Worker Agent for sleep analysis, and displaying personalized recommendations based on user memory.

## Features

- **User Authentication**: Registration and login system with secure password hashing
- **Worker Agent Integration**: Communicates with the Worker Agent for sleep analysis
- **Recommendations Display**: Shows personalized sleep recommendations based on user memory
- **Dashboard**: Centralized view of user's sleep data and insights
- **Memory Management**: Retrieves and displays user memory (STM/LTM) from Worker Agent

## Architecture

```
Supervisor Agent (Port 3002)
    ↓
Worker Agent (Port 8000)
    ↓
Sleep Analysis & Recommendations
```

## Installation

### Prerequisites

- Python 3.8+
- Worker Agent running on `http://localhost:8000`

### Setup

1. **Navigate to supervisor directory:**
```bash
cd supervisor
```

2. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables (optional):**
Create a `.env` file:
```env
SECRET_KEY=your-secret-key-here
DEBUG=False
HOST=0.0.0.0
PORT=3002
WORKER_AGENT_URL=http://localhost:8000
```

5. **Run the application:**
```bash
python app.py
```

The supervisor will start on `http://localhost:3002`

## Usage

### 1. Register/Login

- Navigate to `http://localhost:3002`
- Register a new account or login with existing credentials
- Username must be at least 3 characters
- Password must be at least 6 characters

### 2. Access Dashboard

- After login, you'll be redirected to the dashboard
- The dashboard displays:
  - User information
  - Worker agent status
  - Sleep score and confidence
  - Issues identified
  - Recommendations (sleep window, caffeine cutoff)
  - Personalized tips
  - Memory data (STM/LTM)

### 3. Add Sleep Data

- Click "Worker Agent Interface" button to open the worker agent interface
- Add sleep sessions and profile data
- Return to supervisor dashboard to see recommendations

### 4. Refresh Recommendations

- Click "Refresh" button to reload recommendations from worker agent
- Recommendations are based on user memory stored in the worker agent

## API Endpoints

### Authentication

- `POST /register` - Register new user
- `POST /login` - Login user
- `POST /logout` - Logout user
- `GET /current-user` - Get current logged-in user

### Dashboard

- `GET /dashboard` - Main dashboard page (requires auth)
- `GET /api/recommendations` - Get recommendations for current user
- `POST /api/analyze` - Trigger analysis via worker agent
- `GET /api/memory` - Get user's memory from worker agent

### Worker Agent

- `GET /api/worker/health` - Check worker agent health
- `POST /api/worker/register` - Register with worker agent

## Project Structure

```
supervisor/
├── app.py                 # Main Flask application
├── config.py              # Configuration settings
├── requirements.txt       # Dependencies
├── routes/
│   ├── auth.py           # Authentication routes
│   ├── dashboard.py      # Dashboard routes
│   ├── memory.py         # Memory management routes
│   └── worker.py         # Worker agent integration routes
├── models/
│   └── user.py           # User model and storage
├── services/
│   ├── auth_service.py   # Authentication logic
│   └── worker_client.py  # Worker agent client
├── templates/
│   ├── login.html        # Login page
│   ├── register.html    # Registration page
│   └── dashboard.html    # Main dashboard
├── utils/
│   └── logger.py         # Logging utility
└── instance/
    └── users/            # User data storage
```

## Integration with Worker Agent

The Supervisor Agent communicates with the Worker Agent via HTTP:

1. **Health Check**: Monitors worker agent availability
2. **Task Submission**: Sends sleep analysis tasks
3. **Memory Retrieval**: Fetches user memory (STM/LTM)
4. **Recommendations**: Extracts recommendations from memory

## Configuration

Key configuration options in `config.py`:

- `PORT`: Supervisor agent port (default: 3002)
- `WORKER_AGENT_URL`: Worker agent URL (default: http://localhost:8000)
- `USER_STORAGE_PATH`: Path for user data storage
- `SECRET_KEY`: Flask secret key for sessions

## Testing Flow

1. Start Worker Agent on port 8000
2. Start Supervisor Agent on port 3002
3. Register/Login via supervisor
4. Add sleep data via worker agent interface
5. View recommendations on supervisor dashboard
6. Refresh to get latest recommendations from memory

## Error Handling

- Worker agent unavailable: Shows status indicator and graceful degradation
- No recommendations: Displays helpful message to add sleep data
- Authentication errors: Redirects to login page
- API errors: Shows error messages in UI

## License

This project is part of a multi-agent system architecture.

