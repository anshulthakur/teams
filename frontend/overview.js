import React from "react";
import { createRoot } from "react-dom/client";
import OverviewPage from "./components/OverviewPage";

const App = () => {
  return (
    <div>
      <OverviewPage />
    </div>
  );
};

const root = createRoot(document.getElementById("overview-root"));
root.render(<App />);
