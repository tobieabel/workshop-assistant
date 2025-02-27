import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Document, Page } from 'react-pdf';
import { pdfjs } from 'react-pdf';
import 'react-pdf/dist/esm/Page/AnnotationLayer.css';
import 'react-pdf/dist/esm/Page/TextLayer.css';
import './PlanViewer.css';

// Set worker source directly
pdfjs.GlobalWorkerOptions.workerSrc = `//unpkg.com/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.js`;

const PlanViewer = () => {
    const { planId } = useParams();
    const navigate = useNavigate();
    const [numPages, setNumPages] = useState(null);
    const [pageNumber, setPageNumber] = useState(1);
    const [loading, setLoading] = useState(true);

    function onDocumentLoadSuccess({ numPages }) {
        setNumPages(numPages);
        setLoading(false);
    }

    const onDocumentLoadError = (error) => {
        console.error('Error loading PDF:', error);
        if (error.message) console.error('Error message:', error.message);
        if (error.name) console.error('Error name:', error.name);
        setLoading(false);
    };

    const goBack = () => {
        navigate('/');
    };

    return (
        <div className="plan-viewer">
            <div className="viewer-header">
                <button onClick={goBack} className="back-button">
                    ← Back to List
                </button>
                {numPages && (
                    <div className="page-navigation">
                        <button
                            onClick={() => setPageNumber(prev => Math.max(prev - 1, 1))}
                            disabled={pageNumber <= 1}
                        >
                            Previous
                        </button>
                        <span>Page {pageNumber} of {numPages}</span>
                        <button
                            onClick={() => setPageNumber(prev => Math.min(prev + 1, numPages))}
                            disabled={pageNumber >= numPages}
                        >
                            Next
                        </button>
                    </div>
                )}
            </div>
            
            <div className="document-container">
                {loading && <div className="loading">Loading PDF...</div>}
                <Document
                    file={`/api/lesson-plan/${planId}`}
                    onLoadSuccess={onDocumentLoadSuccess}
                    onLoadError={onDocumentLoadError}
                    loading={<div className="loading">Loading PDF...</div>}
                    error={<div className="error">Failed to load PDF. Please try again.</div>}
                >
                    <Page 
                        pageNumber={pageNumber} 
                        renderTextLayer={true}
                        renderAnnotationLayer={true}
                        scale={1.2}
                    />
                </Document>
            </div>
        </div>
    );
};

export default PlanViewer; 