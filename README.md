# Workshop Assistant Application

A full-stack web application for managing and viewing PDF lesson plans with text extraction capabilities.

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
   - Manages file storage in `uploads/` directory

2. **Database Driver (`db_driver.py`)**
   - SQLite database management using `sqlite3`
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

### Frontend Architecture

Built with React and Vite, featuring:

#### Key Features
- PDF upload with size and type validation
- Interactive PDF viewer with navigation
- Real-time table updates
- Delete functionality

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

3. Run the server:
   ```bash
   python server.py
   ```
   Server runs on `http://localhost:5001`

### Frontend Setup
1. Install Node.js dependencies:
   ```bash
   cd frontend
   npm install
   ```

2. Run the development server:
   ```bash
   npm run dev
   ```
   Frontend runs on `http://localhost:5173`

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
