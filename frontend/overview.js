import React from "react";
import { createRoot } from "react-dom/client";
import OverviewPage from "./components/OverviewPage";

// Entry point for the React application
const App = () => {
  return <OverviewPage />;
};

const root = createRoot(document.getElementById("app")); // The div where the React app will mount
root.render(<App />);
