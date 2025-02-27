import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './LessonPlansTable.css';

const LessonPlansTable = () => {
    const navigate = useNavigate();
    const [plans, setPlans] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [selectedPlanId, setSelectedPlanId] = useState(null);

    useEffect(() => {
        fetchPlans();
        
        // Listen for new uploads
        window.addEventListener('lessonPlanUploaded', fetchPlans);
        
        return () => {
            window.removeEventListener('lessonPlanUploaded', fetchPlans);
        };
    }, []);

    const fetchPlans = async () => {
        try {
            const response = await fetch(`${import.meta.env.VITE_API_URL}/lesson-plans`);
            const data = await response.json();
            setPlans(data);
        } catch (error) {
            console.error('Error fetching lesson plans:', error);
        } finally {
            setLoading(false);
        }
    };

    const formatDate = (dateString) => {
        return new Date(dateString).toLocaleDateString();
    };

    const formatFileSize = (bytes) => {
        const mb = bytes / (1024 * 1024);
        return `${mb.toFixed(2)} MB`;
    };

    const handleDownload = (planId, title) => {
        window.open(`/api/lesson-plan/${planId}?download=true`, '_blank');
    };

    const handleView = (planId) => {
        navigate(`/plan/${planId}`);
    };

    const handleDelete = async (planId, title) => {
        if (!window.confirm(`Are you sure you want to delete "${title}"?`)) {
            return;
        }

        try {
            const response = await fetch(`/api/lesson-plan/${planId}`, {
                method: 'DELETE',
            });

            if (!response.ok) {
                throw new Error('Failed to delete plan');
            }

            // Refresh the plans list
            fetchPlans();
        } catch (err) {
            setError(err.message);
        }
    };

    const handleSelect = async (planId) => {
        try {
            // Toggle selection
            const newPlanId = selectedPlanId === planId ? null : planId;
            
            // Update backend
            const response = await fetch('/api/active-lesson-plan', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ plan_id: newPlanId }),
            });

            if (!response.ok) {
                throw new Error('Failed to update active plan');
            }

            // Update local state
            setSelectedPlanId(newPlanId);
            
        } catch (error) {
            console.error('Error updating active plan:', error);
            setError('Failed to update active plan');
        }
    };

    if (loading) return <div className="loading">Loading plans...</div>;
    if (error) return <div className="error">Error: {error}</div>;

    return (
        <div className="plans-table-container">
            <h2>Uploaded Lesson Plans</h2>
            {plans.length === 0 ? (
                <p className="no-plans">No lesson plans uploaded yet.</p>
            ) : (
                <table className="plans-table">
                    <thead>
                        <tr>
                            <th>Select</th>
                            <th>Title</th>
                            <th>Upload Date</th>
                            <th>Size</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {plans.map((plan) => (
                            <tr 
                                key={plan.id} 
                                className={selectedPlanId === plan.id ? 'selected-row' : ''}
                            >
                                <td>
                                    <button 
                                        onClick={() => handleSelect(plan.id)}
                                        className={`select-button ${selectedPlanId === plan.id ? 'selected' : ''}`}
                                    >
                                        {selectedPlanId === plan.id ? 'Deselect' : 'Select'}
                                    </button>
                                </td>
                                <td>{plan.title}</td>
                                <td>{formatDate(plan.upload_date)}</td>
                                <td>{formatFileSize(plan.file_size)}</td>
                                <td>
                                    <div className="action-buttons">
                                        <button
                                            onClick={() => handleView(plan.id)}
                                            className="view-button"
                                        >
                                            View
                                        </button>
                                        <button
                                            onClick={() => handleDownload(plan.id, plan.title)}
                                            className="download-button"
                                        >
                                            Download
                                        </button>
                                        <button
                                            onClick={() => handleDelete(plan.id, plan.title)}
                                            className="delete-button"
                                        >
                                            Delete
                                        </button>
                                    </div>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            )}
        </div>
    );
};

export default LessonPlansTable; 