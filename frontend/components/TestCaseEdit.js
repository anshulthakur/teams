import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';

import axios from 'axios';
import TestCaseForm from './TestCaseForm';

const TestCaseEdit = () => {
  const { id } = useParams();
  const [testCaseData, setTestCaseData] = useState(null);
  const testcaseId = parseInt(id, 10);  // Convert the id to an integer

  useEffect(() => {
    const fetchTestCaseData = async () => {
        try {
            const response = await axios.get(`/tests/test-cases/testcases/${id}/`);
            
            var content = JSON.parse(response.data.content);
            console.log(content);
            var testcaseBody = {
              title: response.data.name,
              description: content.description,
              id: content.id,
              proceduralSteps: content.proceduralSteps
            }

            setTestCaseData(testcaseBody);
        } catch (error) {
            console.error('Error fetching test case data:', error);
        }
      };

      if (id) {
          fetchTestCaseData();
      }
  }, [id]);

  if (!testCaseData) {
      return <div>Loading...</div>;
  }
  return (
    <div>
        <TestCaseForm existingData={testCaseData}/>
    </div>
  );
};

export default TestCaseEdit;