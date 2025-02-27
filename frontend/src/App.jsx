import { useState } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './App.css'
import LiveKitModal from './components/LiveKitModal';
import FileUpload from './components/FileUpload';
import LessonPlansTable from './components/LessonPlansTable';
import PlanViewer from './components/PlanViewer';
import logo from './assets/logo-svg.svg'

function App() {
  const [showSupport, setShowSupport] = useState(false);

  const handleSupportClick = () => {
    setShowSupport(true)
  }

  const HomePage = () => (
    <>
      <main className="main-content">
        <section className="hero">
          <h1>AI Assistance to Order</h1>
          <p>Upload your session plan</p>
          <FileUpload />
        </section>

        <LessonPlansTable />

        <div className="center-container">
          <button className="support-button" onClick={handleSupportClick}>
            Launch Assistant
          </button>
        </div>
      </main>
    </>
  );

  return (
    <Router>
      <div className="app">
        <img src={logo} alt="ATS York Logo" className="logo-image" />
        <header className="header">
          <div className="app-title">Workshop Assistant</div>
        </header>

        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/plan/:planId" element={<PlanViewer />} />
        </Routes>

        {showSupport && <LiveKitModal setShowSupport={setShowSupport}/>}
      </div>
    </Router>
  );
}

export default App;
