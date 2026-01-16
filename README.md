# Employee Management System (EMS)

A comprehensive full-stack application for managing employees, teams, and tasks within an organization. Built with FastAPI (Backend) and React (Frontend).

## Features

### Authentication & Authorization
- **User Registration**: New users can register and wait for Admin approval.
- **Secure Login**: JWT-based authentication supporting both Username and Email.
- **Role-Based Access Control (RBAC)**:
    - **Admin**: Full access to manage users, teams, and system settings.
    - **Manager**: Manage assigned teams and tasks.
    - **Employee**: View tasks and update status.

### Team Management
- **Create Teams**: Admins can create teams and assign managers.
- **manage Members**: Add or remove members from teams dynamically.
- **Team Dashboard**: Managers can view their team's performance and composition.

### Task Management
- **Create Tasks**: Assign tasks to individual users or entire teams.
- **Subtasks & Progress**: Break down tasks into subtasks with real-time progress tracking.
- **Task Details**: Detailed view for editing descriptions, reassigning teams, and managing subtasks.
- **Status Tracking**: Open, In Progress, Completed states.

### Admin Dashboard
- **User Management**: View, filter, search, and delete users.
- **Pending Approvals**: Review and approve/reject new user registrations.
- **System Overview**: Centralized control over organizational structure.

## Tech Stack

### Backend
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL (SQLAlchemy ORM)
- **Authentication**: OAuth2 with Password hashing (Bcrypt) and JWT tokens
- **Testing**: Pytest

### Frontend
- **Framework**: React.js (Vite)
- **Styling**: CSS Modules / Vanilla CSS
- **HTTP Client**: Axios with Interceptors for Auth consistency

## Setup Instructions

### Prerequisites
- Python 3.9+
- Node.js & npm
- PostgreSQL (Ensure it is running)

### Backend Setup
1. **Navigate to project root**:
   ```bash
   cd d:\EMS
   ```
2. **Create and Activate Virtual Environment**:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```
3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Environment Variables**:
   Ensure a `.env` file exists with:
   ```env
   PROJECT_NAME="EMPLOYEE_MANAGEMENT_SYSTEM"
   VERSION="1.0.0"
   DATABASE_URL="postgresql://user:password@localhost:5432/dbname"
   SECRET_KEY=your_secret_key
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```
5. **Run Database Seeder (Optional)**:
   Populates DB with Admin, Managers, and Teams.
   ```bash
   python db_seeder.py
   ```
6. **Start Server**:
   ```bash
   uvicorn app.main:app --reload
   ```
   Server runs at `http://127.0.0.1:8000`. API Docs at `/docs`.

### Frontend Setup
1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```
2. **Install Dependencies**:
   ```bash
   npm install
   ```
3. **Start Development Server**:
   ```bash
   npm run dev
   ```
   App runs at `http://localhost:5173`.

## Testing

Run the automated test suite to verify backend functionality:
```bash
pytest
```
Specific tests:
- `tests/test_admin_enhancements.py`: Verify Admin features.
- `tests/test_task_management.py`: Verify Task/Subtask features.
- `tests/test_team_flow.py`: Verify Team Logic.
