import React from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import TestSuiteEdit from './components/TestSuiteEdit';

const App = () => {
  return (
    <Router>
      <Routes>
        <Route path="/tests/test-suites/create/" element={<TestSuiteEdit/>} />
        <Route path="/tests/test-suites/edit/:id" element={<TestSuiteEdit />} />
        {/* Add other routes as needed */}
      </Routes>
    </Router>
  );
}

const root = createRoot(document.getElementById("app"));
root.render(<App />);