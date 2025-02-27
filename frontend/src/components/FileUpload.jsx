import { useState } from 'react';
import './FileUpload.css';

const FileUpload = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadStatus, setUploadStatus] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    
    if (!file) return;
    
    if (file.type !== 'application/pdf') {
      setUploadStatus('Please select a PDF file');
      return;
    }
    
    if (file.size > 10 * 1024 * 1024) { // 10MB limit
      setUploadStatus('File size must be less than 10MB');
      return;
    }
    
    setSelectedFile(file);
    setUploadStatus('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const formData = new FormData();
    formData.append('file', selectedFile);
    
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/upload`, {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        throw new Error('Upload failed');
      }

      setUploadStatus('File uploaded successfully!');
      setSelectedFile(null);
      
      // Dispatch a custom event to notify the table to refresh
      window.dispatchEvent(new CustomEvent('lessonPlanUploaded'));
      
    } catch (error) {
      console.error('Error:', error);
      setUploadStatus('Failed to upload file: ' + error.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="file-upload">
      <input
        type="file"
        accept=".pdf"
        onChange={handleFileSelect}
        className="file-input"
      />
      {selectedFile && (
        <div className="selected-file">
          Selected: {selectedFile.name}
        </div>
      )}
      <button 
        onClick={handleSubmit} 
        disabled={!selectedFile || isLoading}
        className="upload-button"
      >
        {isLoading ? 'Uploading...' : 'Upload'}
      </button>
      {uploadStatus && (
        <div className={`status-message ${uploadStatus.includes('success') ? 'success' : 'error'}`}>
          {uploadStatus}
        </div>
      )}
    </div>
  );
};

export default FileUpload; 