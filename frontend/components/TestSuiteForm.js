import React, { useState, useEffect } from 'react';
import axios from 'axios';

axios.defaults.headers.common['X-CSRFToken'] = csrftoken;

const TestSuiteForm = ({ existingData }) => {
  const [name, setName] = useState(existingData?.name || '');
  const [content, setContent] = useState(existingData?.content || '');
  const [availableTestCases, setAvailableTestCases] = useState([]); // Store available test cases
  const [selectedTestCases, setSelectedTestCases] = useState(existingData?.testcases || []); // Store selected test cases

  useEffect(() => {
    const fetchAvailableTestCases = async () => {
      try {
        const response = await axios.get('/tests/test-cases/testcases/'); // Fetch all available test cases from the server
  
        if (response.data.count > 0) {
          // Get the list of selected test case IDs from existingData
          const selectedTestCaseIds = existingData?.testcases.map(tc => tc.id) || [];
  
          // Filter the available test cases to exclude those already in selectedTestCases
          const filteredTestCases = response.data.results.filter(tc => !selectedTestCaseIds.includes(tc.id));
  
          setAvailableTestCases(filteredTestCases); // Set the filtered available test cases
        }
      } catch (error) {
        console.error('Error fetching available test cases:', error);
      }
    };
  
    fetchAvailableTestCases();
  }, [existingData]);
  

  // Handle form submission
  const handleSubmit = async (e, action) => {
    e.preventDefault();

    const payload = {
      name: name,
      content: content,
      testcases: selectedTestCases.map(tc => tc.id), // Send only the selected test case IDs
    };

    try {
      let response;
      console.log(payload);
      if (existingData?.id) {
        // Update existing test suite
        response = await axios.put(`/tests/test-cases/testsuites/${existingData.id}/`, payload);
      } else {
        // Create new test suite
        response = await axios.post('/tests/test-cases/testsuites/', payload);
      }

      console.log(response);
      //Redirect based on the action
      if (action === 'view') {
        window.location.href = `/tests/test-suites/${response.data.id}/`;
      } else if (action === 'edit') {
        window.location.href = `/tests/test-suites/edit/${response.data.id}/`;
      }
    } catch (error) {
      console.error('Error saving test suite:', error);
    }
  };

  // Add test case to the selected list
  const handleAddTestCase = (id) => {
    const selected = availableTestCases.find(test => test.id === id);
    setAvailableTestCases(availableTestCases.filter(test => test.id !== id));
    setSelectedTestCases([...selectedTestCases, selected]);
  };

  // Remove test case from the selected list
  const handleRemoveTestCase = (id) => {
    const removed = selectedTestCases.find(test => test.id === id);
    setSelectedTestCases(selectedTestCases.filter(test => test.id !== id));
    setAvailableTestCases([...availableTestCases, removed]);
  };

  return (
    <form onSubmit={(e) => handleSubmit(e, 'view')}>
      <div className="mb-3">
        <label htmlFor="name" className="form-label">Test Suite Name</label>
        <input
          type="text"
          id="name"
          className="form-control"
          value={name}
          onChange={(e) => setName(e.target.value)}
          required
        />
      </div>

      <div className="mb-3">
        <label htmlFor="content" className="form-label">Description</label>
        <textarea
          id="content"
          className="form-control"
          rows="4"
          value={content}
          onChange={(e) => setContent(e.target.value)}
        />
      </div>

      {/* Dual-pane test case selection */}
      <div className="row">
        <div className="col-md-6">
          <h5>Available Test Cases</h5>
          <ul className="list-group">
            {availableTestCases.map(tc => (
              <li key={tc.id} className="list-group-item">
                {tc.name}
                <button
                  type="button"
                  className="btn btn-primary btn-sm float-end"
                  onClick={() => handleAddTestCase(tc.id)}
                >
                  Add
                </button>
              </li>
            ))}
          </ul>
        </div>

        <div className="col-md-6">
          <h5>Selected Test Cases</h5>
          <ul className="list-group">
            {selectedTestCases.map(tc => (
              <li key={tc.id} className="list-group-item">
                {tc.name}
                <button
                  type="button"
                  className="btn btn-danger btn-sm float-end"
                  onClick={() => handleRemoveTestCase(tc.id)}
                >
                  Remove
                </button>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Save Buttons */}
      <button
        type="button"
        className="btn btn-primary mt-4"
        onClick={(e) => handleSubmit(e, 'view')}
      >
        Save and View
      </button>
      <button
        type="button"
        className="btn btn-secondary mt-4"
        onClick={(e) => handleSubmit(e, 'edit')}
      >
        Save and Continue Editing
      </button>
    </form>
  );
};

export default TestSuiteForm;
