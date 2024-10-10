import React from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import TestRunEdit from './components/TestRunEdit';

const App = () => {
  return (
    <Router>
      <Routes>
        <Route path="/tests/test-runs/create/" element={<TestRunEdit/>} />
        {/* Add other routes as needed */}
      </Routes>
    </Router>
  );
}

const root = createRoot(document.getElementById("app"));
root.render(<App />);