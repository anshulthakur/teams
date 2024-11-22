import React from "react";
import { PieChart, Pie, Cell, Tooltip } from "recharts";
const COLORS = {
  PASS: "#28a745", // Green for success
  FAIL: "#dc3545", // Red for failures
  SKIPPED: "#ffc107", // Yellow for skipped
  ERROR: "#6c757d", // Grey for errors
};

const TestHealthOverview = ({ data }) => {
  const chartData = Object.entries(data).map(([key, value]) => ({ name: key, value }));

  return (
    <div>
      <h2>Test Health Overview (Lifetime)</h2>
      <div className="row">
        <div className="col-md-6">
          <PieChart width={400} height={300}>
            <Pie data={chartData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={100}>
              {chartData.map((entry) => (
                <Cell key={entry.name} fill={COLORS[entry.name] || "#8884d8"} />
              ))}
            </Pie>
            <Tooltip />
          </PieChart>
        </div>
        <div className="col-md-6">
          <table className="table table-bordered">
            <thead>
              <tr>
                <th>Status</th>
                <th>Count</th>
              </tr>
            </thead>
            <tbody>
              {chartData.map((entry) => (
                <tr key={entry.name}>
                  <td>{entry.name}</td>
                  <td>{entry.value}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default TestHealthOverview;
