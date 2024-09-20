import React from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import TestCaseEdit from './components/TestCaseEdit';

const App = () => {
  return (
    <Router>
      <Routes>
        <Route path="/tests/test-cases/create/" element={<TestCaseEdit message="Welcome to the test case form page"/>} />
        {/* Add other routes as needed */}
      </Routes>
    </Router>
  );
}

const root = createRoot(document.getElementById("app"));
root.render(<App />);