import React from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, Legend, CartesianGrid } from "recharts";

const LatestTestRunSummary = ({ data }) => {
    const chartData = [...data].reverse().map((run) => ({
      name: run.run,
      PASS: run.results.PASS || 0,
      FAIL: run.results.FAIL || 0,
      SKIPPED: run.results.SKIPPED || 0,
      ERROR: run.results.ERROR || 0,
    }));
  
    return (
      <div>
        <h2>Latest Test Runs</h2>
        <div className="row">
          <div className="col-md-6">
            <BarChart width={500} height={300} data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="PASS" fill="#28a745" />
              <Bar dataKey="FAIL" fill="#dc3545" />
              <Bar dataKey="SKIPPED" fill="#ffc107" />
              <Bar dataKey="ERROR" fill="#6c757d" />
            </BarChart>
          </div>
          <div className="col-md-6">
            <table className="table table-bordered">
              <thead>
                <tr>
                  <th>Run</th>
                  <th>PASS</th>
                  <th>FAIL</th>
                  <th>SKIPPED</th>
                  <th>ERROR</th>
                </tr>
              </thead>
              <tbody>
                {data.map((run, index) => (
                  <tr key={index}>
                    <td>{run.run}</td>
                    <td>{run.results.PASS || 0}</td>
                    <td>{run.results.FAIL || 0}</td>
                    <td>{run.results.SKIPPED || 0}</td>
                    <td>{run.results.ERROR || 0}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    );
  };
  
  export default LatestTestRunSummary;
  