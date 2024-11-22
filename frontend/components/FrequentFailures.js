import React from "react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from "recharts";

const FrequentFailures = () => {
  // Placeholder data for fixtures
  const data = [
    { name: "TC001", failures: 15 },
    { name: "TC005", failures: 10 },
    { name: "TC003", failures: 8 },
    { name: "TC002", failures: 6 },
  ];

  return (
    <div className="card my-3">
      <div className="card-header">Frequent Failures</div>
      <div className="card-body">
        <BarChart width={500} height={300} data={data} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Bar dataKey="failures" fill="#dc3545" name="Failures" />
        </BarChart>
      </div>
    </div>
  );
};

export default FrequentFailures;
