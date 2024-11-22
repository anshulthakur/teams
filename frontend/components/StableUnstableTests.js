import React from "react";
import { PieChart, Pie, Cell, Tooltip } from "recharts";

const COLORS = ["#00C49F", "#FF8042"];

const StableUnstableTests = ({ data }) => {
  const stableData = data.stable_tests.map((test) => ({
    name: test.name,
    value: test.pass_ratio * 100,
  }));

  const unstableData = data.unstable_tests.map((test) => ({
    name: test.name,
    value: test.fail_ratio * 100,
  }));

  return (
    <div>
      <h2>Stable and Unstable Tests</h2>
      <div className="row">
        <div className="col-md-6">
          <h3>Most Stable Tests</h3>
          {/* <PieChart width={400} height={300}>
            <Pie data={stableData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={100} fill="#00C49F">
              {stableData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[0]} />
              ))}
            </Pie>
            <Tooltip />
          </PieChart> */}
          <table className="table table-bordered mt-3">
            <thead>
              <tr>
                <th>Test Case</th>
                <th>Pass Rate (%)</th>
              </tr>
            </thead>
            <tbody>
              {stableData.map((test, index) => (
                <tr key={index}>
                  <td>{test.name}</td>
                  <td>{test.value.toFixed(2)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="col-md-6">
          <h3>Most Unstable Tests</h3>
          {/* <PieChart width={400} height={300}>
            <Pie data={unstableData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={100} fill="#FF8042">
              {unstableData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[1]} />
              ))}
            </Pie>
            <Tooltip />
          </PieChart> */}
          <table className="table table-bordered mt-3">
            <thead>
              <tr>
                <th>Test Case</th>
                <th>Fail Rate (%)</th>
              </tr>
            </thead>
            <tbody>
              {unstableData.map((test, index) => (
                <tr key={index}>
                  <td>{test.name}</td>
                  <td>{test.value.toFixed(2)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default StableUnstableTests;
