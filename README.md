# Workshop Assistant Application

A full-stack web application for managing and viewing PDF lesson plans with text extraction capabilities and an AI teaching assistant powered by LiveKit.

## Architecture Overview

### Backend Architecture

The backend is built with Flask and follows a modular design pattern:

#### Core Components

1. **Flask Server (`server.py`)**
   - Handles HTTP requests and routing
   - Main endpoints:
     - `/upload` - File upload handling
     - `/lesson-plan/<id>` - PDF retrieval and deletion
     - `/lesson-plans` - List all lesson plans
   - Integrates PDF text extraction with file uploads
   - Uses Uvicorn for production deployment

2. **Database Driver (`db_driver.py`)**
   - SQLite database management using `sqlite3`
   - Configurable database path via environment variables
   - Key tables:
     - `lesson_plans`: Stores PDF metadata and extracted text
     - Schema:
       ```sql
       CREATE TABLE lesson_plans (
           id INTEGER PRIMARY KEY AUTOINCREMENT,
           title TEXT NOT NULL,
           file_path TEXT NOT NULL,
           upload_date TIMESTAMP NOT NULL,
           file_size INTEGER NOT NULL,
           content TEXT
       )
       ```
   - Provides CRUD operations for lesson plans

3. **PDF Text Extractor (`utils/pdf_extractor.py`)**
   - Handles PDF text extraction using PyPDF2
   - Extracts text content from uploaded PDFs
   - Includes logging for debugging

4. **LiveKit Agent (`agent.py`)**
   - AI teaching assistant powered by LiveKit and OpenAI
   - Real-time voice and text interaction
   - Context-aware responses based on lesson plans
   - Handles speech-to-text and text-to-speech conversion
   - Event-driven architecture using WebSocket connections

### Frontend Architecture

Built with React and Vite, featuring:

#### Key Features
- PDF upload with size and type validation
- Interactive PDF viewer with navigation
- Real-time table updates
- Delete functionality
- Voice/text chat interface with AI assistant
- Real-time audio visualization

## Setup and Installation

### Backend Setup
1. Create a Python virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. Set up environment variables (create `.env` file):
   ```
   LIVEKIT_URL=your_livekit_url
   LIVEKIT_API_KEY=your_api_key
   LIVEKIT_API_SECRET=your_api_secret
   OPENAI_API_KEY=your_openai_key
   ```

4. Run the server locally:
   ```bash
   uvicorn server:app --host 0.0.0.0 --port 5001
   ```

5. Run the LiveKit agent:
   ```bash
   python agent.py
   ```

### Frontend Setup
1. Install dependencies:
   ```bash
   cd frontend
   npm install
   ```

2. Run the development server:
   ```bash
   npm run dev
   ```

## Deployment

The application is configured for deployment on Render.com using the provided `render.yaml`:

### Key Features
- Automatic deployment from GitHub
- Persistent disk storage for database and uploads
- Environment variable management
- Automatic HTTPS
- Horizontal scaling for the LiveKit agent

### Deployment Steps
1. Fork/clone this repository
2. Create a new project on Render.com
3. Link your GitHub repository
4. Create an environment group with required variables:
   - `LIVEKIT_URL`
   - `LIVEKIT_API_KEY`
   - `LIVEKIT_API_SECRET`
   - `OPENAI_API_KEY`
5. Deploy using the provided `render.yaml`

### Database Configuration
The application uses SQLite with persistent storage:
- Development: Local SQLite file
- Production: Mounted disk on Render.com
- Environment variable `DB_PATH` controls database location
- Automatic directory creation and initialization

## Contributing
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## Data Flow

1. **File Upload Process**:
   ```
   Frontend → /upload endpoint → PDF Text Extraction → Database Storage
   ```
   - File is validated
   - Saved to uploads directory
   - Text extracted from PDF
   - Metadata and text stored in database

2. **PDF Viewing Process**:
   ```
   Frontend Request → /lesson-plan/<id> → File System → PDF Delivery
   ```
   - Frontend requests specific PDF
   - Backend validates existence
   - Sends file with proper MIME type

## API Endpoints

### POST `/upload`
- Handles PDF file uploads
- Validates file type and size
- Extracts text content
- Returns: `{ message, plan_id, text_extracted }`

### GET `/lesson-plan/<id>`
- Retrieves specific PDF file
- Returns: PDF file or error message

### DELETE `/lesson-plan/<id>`
- Removes PDF file and database entry
- Returns: Success/failure message

### GET `/lesson-plans`
- Lists all available lesson plans
- Returns: Array of lesson plan metadata


## Troubleshooting

Common issues and solutions:
1. Database errors: Delete `auto_db.sqlite` to reset
2. Missing files: Check `uploads/` directory
3. PDF viewing issues: Verify file paths in database
