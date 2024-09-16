import React from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Dashboard from './components/Dashboard';

const App = () => {
  return (
    <Router>
      <Routes>
        <Route path="/tests/test-cases/create/" element={<Dashboard message="Welcome to the test case form page"/>} />
        {/* Add other routes as needed */}
      </Routes>
    </Router>
  );
}

const root = createRoot(document.getElementById("app"));
root.render(<App />);