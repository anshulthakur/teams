import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';
import TestSuiteForm from './TestSuiteForm';

const TestSuiteEdit = () => {
  const { id } = useParams(); // Get the id from the URL params (if any)
  const [testSuiteData, setTestSuiteData] = useState(null);
  const [loading, setLoading] = useState(true); // Loading state

  useEffect(() => {
    const fetchTestSuiteData = async () => {
      try {
        if (id) {
          // Fetch the test suite data if an id exists (editing case)
          const response = await axios.get(`/tests/test-cases/testsuites/${id}/`);

          const testsuiteBody = {
            name: response.data.name,
            content: response.data.content, // Assume description, etc., are in content
            id: response.data.id,
            testcases: response.data.testcases || [],
            availableTestcases: [] // Fetch available test cases if needed
          };

          setTestSuiteData(testsuiteBody);
        }
      } catch (error) {
        console.error('Error fetching test suite data:', error);
      } finally {
        setLoading(false); // Stop loading
      }
    };

    if (id) {
      fetchTestSuiteData(); // Fetch data for editing
    } else {
      setLoading(false); // Render blank form for new suite
    }
  }, [id]);

  return (
    <div>
      {loading ? (
        <p>Loading...</p>
      ) : (
        <TestSuiteForm existingData={testSuiteData} />
      )}
    </div>
  );
};

export default TestSuiteEdit;
