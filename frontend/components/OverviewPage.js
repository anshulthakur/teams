import React, { useState, useEffect } from "react";
import TestHealthOverview from "./TestHealthOverview";
import FrequentFailures from "./FrequentFailures";
import LatestTestRunSummary from "./LatestTestRunSummary";
import StableUnstableTests from "./StableUnstableTests";

const OverviewPage = () => {
  const [testHealth, setTestHealth] = useState({});
  const [frequentFailures, setFrequentFailures] = useState([]);
  const [latestRuns, setLatestRuns] = useState([]);
  const [stableUnstableTests, setStableUnstableTests] = useState({ stable_tests: [], unstable_tests: [] });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchMetrics = async () => {
      setLoading(true);
      try {
        const [healthRes, failuresRes, runsRes, stableUnstableRes] = await Promise.all([
          fetch("/tests/metrics/test-health-overview/"),
          fetch("/tests/metrics/frequent-failures/?limit=5"),
          fetch("/tests/metrics/latest-test-run-summary/?limit=5"),
          fetch("/tests/metrics/stable-unstable-tests/?limit=10"),
        ]);

        setTestHealth(await healthRes.json());
        setFrequentFailures(await failuresRes.json());
        setLatestRuns(await runsRes.json());
        setStableUnstableTests(await stableUnstableRes.json());
      } catch (error) {
        console.error("Error fetching metrics:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchMetrics();
  }, []);

  if (loading) return <p>Loading...</p>;

  return (
    <div>
      <h1 className="pb-2 mb-2">Testing at a glance</h1>
      <LatestTestRunSummary data={latestRuns} />
      <TestHealthOverview data={testHealth} />
      <FrequentFailures data={frequentFailures} />
      <StableUnstableTests data={stableUnstableTests} />
    </div>
  );
};

export default OverviewPage;
