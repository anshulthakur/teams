import React from "react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from "recharts";

const TestRunSummary = () => {
  // Placeholder data for fixtures
  const data = [
    { name: "Run 1", passed: 45, failed: 5, skipped: 0 },
    { name: "Run 2", passed: 40, failed: 10, skipped: 0 },
    { name: "Run 3", passed: 48, failed: 2, skipped: 0 },
    { name: "Run 4", passed: 42, failed: 8, skipped: 0 },
  ];

  return (
    <div className="card my-3">
      <div className="card-header">Latest Test Run Summary</div>
      <div className="card-body">
        <LineChart width={500} height={300} data={data} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey="passed" stroke="#28a745" name="Passed" />
          <Line type="monotone" dataKey="failed" stroke="#dc3545" name="Failed" />
          <Line type="monotone" dataKey="skipped" stroke="#ffc107" name="Skipped" />
        </LineChart>
      </div>
    </div>
  );
};

export default TestRunSummary;
