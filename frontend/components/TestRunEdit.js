import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';
import TestRunForm from './TestRunForm';

const TestRunEdit = () => {
  const { id } = useParams(); // Get the id from the URL params (if any)
  const [testRunData, setTestRunData] = useState(null);
  const [loading, setLoading] = useState(true); // Loading state

  useEffect(() => {
    const fetchTestRunData = async () => {
      try {
        if (id) {
          // If there is an id, fetch the existing test case data
          const response = await axios.get(`/tests/test-cases/testruns/${id}/`);
          const content = JSON.parse(response.data.content);

          const testrunBody = {
            notes: response.data.notes,
            executions: response.data.executions,
            id: response.data.id,
            date: response.data.date
          };

          setTestRunData(testrunBody);
        }
      } catch (error) {
        console.error('Error fetching test run data:', error);
      } finally {
        setLoading(false); // Stop loading whether data is fetched or not
      }
    };

    if (id) {
      // Fetch data only if there's an ID (i.e., editing an existing test run)
      fetchTestRunData();
    } else {
      // If no id, it's a new test run, so no need to fetch data
      setLoading(false); // Stop loading and render blank form
    }
  }, [id]);

  return (
    <div>
      {loading ? (
        <p>Loading...</p>
      ) : (
        <TestRunForm existingData={testRunData} />
      )}
    </div>
  );
};

export default TestRunEdit;
