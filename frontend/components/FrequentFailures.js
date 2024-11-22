import React from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid } from "recharts";

const FrequentFailures = ({ data }) => {
  const chartData = data.map((failure) => ({
    name: failure.testcase__name,
    failures: failure.failures,
  }));

  return (
    <div>
      <h2>Frequent Failures</h2>
      <div className="row">
        <div className="col-md-6">
          <BarChart width={500} height={300} data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="failures" fill="#007bff" />
          </BarChart>
        </div>
        <div className="col-md-6">
          <table className="table table-bordered">
            <thead>
              <tr>
                <th>Test Case</th>
                <th>Failure Count</th>
              </tr>
            </thead>
            <tbody>
              {data.map((failure, index) => (
                <tr key={index}>
                  <td>{failure.testcase__name}</td>
                  <td>{failure.failures}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default FrequentFailures;
