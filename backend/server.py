import os
from livekit import api
from flask import Flask, request, jsonify, send_file
from dotenv import load_dotenv
from flask_cors import CORS
from livekit.api import LiveKitAPI, ListRoomsRequest
import uuid
from werkzeug.utils import secure_filename
from db_driver import DatabaseDriver
from utils.pdf_extractor import extract_text_from_pdf

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

UPLOAD_FOLDER = os.getenv('UPLOAD_PATH', 'uploads')
ALLOWED_EXTENSIONS = {'pdf'}
MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB limit

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

db = DatabaseDriver()

async def generate_room_name():
    name = "room-" + str(uuid.uuid4())[:8]
    rooms = await get_rooms()
    while name in rooms:
        name = "room-" + str(uuid.uuid4())[:8]
    return name

async def get_rooms():
    api = LiveKitAPI()
    rooms = await api.room.list_rooms(ListRoomsRequest())
    await api.aclose()
    return [room.name for room in rooms.rooms]

@app.route("/getToken")
async def get_token():
    name = request.args.get("name", "my name")
    room = request.args.get("room", None)
    
    if not room:
        room = await generate_room_name()
        
    token = api.AccessToken(os.getenv("LIVEKIT_API_KEY"), os.getenv("LIVEKIT_API_SECRET")) \
        .with_identity(name)\
        .with_name(name)\
        .with_grants(api.VideoGrants(
            room_join=True,
            room=room
        ))
    
    return token.to_jwt()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        print("No file in request")
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        print("Empty filename")
        return jsonify({'error': 'No selected file'}), 400
    
    if not allowed_file(file.filename):
        print(f"Invalid file type: {file.filename}")
        return jsonify({'error': 'File type not allowed'}), 400
    
    try:
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        print(f"Attempting to save file to: {file_path}")
        
        # Save file to disk
        file.save(file_path)
        print(f"File saved successfully to {file_path}")
        
        # Extract text from PDF
        try:
            extracted_text = extract_text_from_pdf(file_path)
            print(f"Extracted {len(extracted_text)} characters from {filename}")
        except Exception as e:
            print(f"Warning: Failed to extract text from PDF: {str(e)}")
            extracted_text = None  # Continue without text if extraction fails
        
        # Save file info and extracted text to database
        file_size = os.path.getsize(file_path)
        try:
            print(f"Saving to database: {filename}, size: {file_size}")
            plan_id = db.save_lesson_plan(
                title=filename,
                file_path=file_path,
                file_size=file_size,
                content=extracted_text
            )
            print(f"Successfully saved to database with ID: {plan_id}")
        except Exception as db_error:
            print(f"Database error: {str(db_error)}")
            print(f"Error type: {type(db_error)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            # If database save fails, clean up the file
            if os.path.exists(file_path):
                os.remove(file_path)
            raise db_error
        
        return jsonify({
            'message': 'File uploaded successfully',
            'plan_id': plan_id,
            'text_extracted': extracted_text is not None
        }), 200
        
    except Exception as e:
        print(f"Upload error: {str(e)}")
        print(f"Error type: {type(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

@app.route('/lesson-plan/<int:plan_id>', methods=['GET', 'DELETE'])
def lesson_plan(plan_id):
    print(f"Current working directory: {os.getcwd()}")
    print(f"Absolute path to uploads folder: {os.path.abspath(UPLOAD_FOLDER)}")
    
    if request.method == 'DELETE':
        try:
            plan = db.get_lesson_plan(plan_id)
            if not plan:
                return jsonify({'error': 'Plan not found'}), 404
                
            # Delete file from disk if it exists
            if os.path.exists(plan['file_path']):
                os.remove(plan['file_path'])
                
            # Delete from database
            db.delete_lesson_plan(plan_id)
            return jsonify({'message': 'Plan deleted successfully'}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
            
    # Existing GET logic...
    print(f"Received request for plan_id: {plan_id}")
    plan = db.get_lesson_plan(plan_id)
    print(f"Retrieved plan from DB: {plan}")
    
    if not plan:
        return jsonify({'error': 'Plan not found'}), 404
    
    try:
        abs_file_path = os.path.abspath(plan['file_path'])
        print(f"Attempting to send file: {abs_file_path}")
        if not os.path.exists(abs_file_path):
            print(f"File does not exist at path: {abs_file_path}")
            return jsonify({'error': 'File not found on disk'}), 404
            
        return send_file(
            abs_file_path,
            mimetype='application/pdf',
            as_attachment='download' in request.args
        )
    except Exception as e:
        print(f"Error sending file: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/lesson-plans', methods=['GET'])
def list_lesson_plans():
    try:
        plans = db.get_all_lesson_plans()
        # Filter out plans where files don't exist
        valid_plans = []
        for plan in plans:
            # Get full file path from database
            full_plan = db.get_lesson_plan(plan['id'])
            if full_plan and os.path.exists(full_plan['file_path']):
                valid_plans.append(plan)
            else:
                # Optionally clean up database entries for missing files
                db.delete_lesson_plan(plan['id'])
        
        return jsonify(valid_plans), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/active-lesson-plan', methods=['POST'])
def set_active_plan():
    try:
        data = request.get_json()
        plan_id = data.get('plan_id')
        db.set_active_lesson_plan(plan_id)
        return jsonify({'message': 'Active plan updated successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)