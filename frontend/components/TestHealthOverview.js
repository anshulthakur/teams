import React from "react";
import { PieChart, Pie, Cell, Legend, Tooltip } from "recharts";

const TestHealthOverview = () => {
  // Placeholder percentages
  const data = [
    { name: "Pass", value: 70 },
    { name: "Fail", value: 20 },
    { name: "Skipped", value: 10 },
  ];

  const COLORS = ["#28a745", "#dc3545", "#ffc107"];

  return (
    <div className="card my-3">
      <div className="card-header">Test Health Overview</div>
      <div className="card-body d-flex justify-content-center">
        <PieChart width={400} height={300}>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            outerRadius={100}
            fill="#8884d8"
            dataKey="value"
            label
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip />
          <Legend />
        </PieChart>
      </div>
    </div>
  );
};

export default TestHealthOverview;
