import React from "react";
import Highlights from "./Highlights";
import TestHealthOverview from "./TestHealthOverview";
import FrequentFailures from "./FrequentFailures";
import TestRunSummary from "./TestRunSummary";

const OverviewPage = () => {
  return (
    <div className="container mt-5">
      <h1>Testing Overview</h1>
      <Highlights />
      <TestHealthOverview />
      <FrequentFailures />
      <TestRunSummary />
    </div>
  );
};

export default OverviewPage;
