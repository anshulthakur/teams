import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';
import TestCaseForm from './TestCaseForm';

const TestCaseEdit = () => {
  const { id } = useParams(); // Get the id from the URL params (if any)
  const [testCaseData, setTestCaseData] = useState(null);
  const [loading, setLoading] = useState(true); // Loading state

  useEffect(() => {
    const fetchTestCaseData = async () => {
      try {
        if (id) {
          // If there is an id, fetch the existing test case data
          const response = await axios.get(`/tests/test-cases/testcases/${id}/`);
          if (response.data.content){
            const content = JSON.parse(response.data.content);

            const testcaseBody = {
              title: response.data.name,
              oid: response.data.oid,
              description: content.description,
              id: response.data.id,
              proceduralSteps: content.proceduralSteps,
            };
            setTestCaseData(testcaseBody);
          }
          else{
            const testcaseBody = {
              title: response.data.name,
              oid: response.data.oid,
              description: '',
              id: response.data.id,
              proceduralSteps: {
                Setup: [{ stepDescription: '', expectedOutput: '' }],
                Start: [{ stepDescription: '', expectedOutput: '' }],
                Measure: [{ stepDescription: '', expectedOutput: '' }],
                Stop: [{ stepDescription: '', expectedOutput: '' }],
                Shutdown: [{ stepDescription: '', expectedOutput: '' }],
                Contingencies: [{ stepDescription: '', expectedOutput: '' }],
              },
            };
            setTestCaseData(testcaseBody);
          }
        }
      } catch (error) {
        console.error('Error fetching test case data:', error);
      } finally {
        setLoading(false); // Stop loading whether data is fetched or not
      }
    };

    if (id) {
      // Fetch data only if there's an ID (i.e., editing an existing test case)
      fetchTestCaseData();
    } else {
      // If no id, it's a new test case, so no need to fetch data
      setLoading(false); // Stop loading and render blank form
    }
  }, [id]);

  return (
    <div>
      {loading ? (
        <p>Loading...</p>
      ) : (
        <TestCaseForm existingData={testCaseData} />
      )}
    </div>
  );
};

export default TestCaseEdit;
