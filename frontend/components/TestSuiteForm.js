import React, { useState, useEffect } from 'react';
import axios from 'axios';

const TestSuiteForm = ({ existingData }) => {
  const [name, setName] = useState(existingData?.name || '');
  const [content, setContent] = useState(existingData?.content || '');
  const [testcases, setTestCases] = useState(existingData?.testcases || []);

  // Handle form submission
  const handleSubmit = async (e, action) => {
    e.preventDefault();

    const payload = {
      name,
      content,
      testcases
    };

    try {
      let response;
      if (existingData?.id) {
        // Update existing test suite
        response = await axios.put(`/tests/test-suites/${existingData.id}/`, payload);
      } else {
        // Create new test suite
        response = await axios.post('/tests/test-suites/', payload);
      }

      // Redirect based on the action
      if (action === 'view') {
        window.location.href = `/tests/test-suites/${response.data.id}/`;
      } else if (action === 'edit') {
        window.location.href = `/tests/test-suites/edit/${response.data.id}/`;
      }
    } catch (error) {
      console.error('Error saving test suite:', error);
    }
  };

  // Add/remove test cases
  const handleAddTestCase = (id) => {
    setSelectedTestCases([...selectedTestCases, id]);
  };

  const handleRemoveTestCase = (id) => {
    setSelectedTestCases(selectedTestCases.filter(tcId => tcId !== id));
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
            {suiteData.availableTestcases.map(tc => (
              <li key={tc.id} className="list-group-item">
                {tc.name}
                <button onClick={() => handleAddTestCase(tc.id)} className="btn btn-primary btn-sm float-end">
                  Add
                </button>
              </li>
            ))}
          </ul>
        </div>

        <div className="col-md-6">
          <h5>Selected Test Cases</h5>
          <ul className="list-group">
            {suiteData.testcases.filter(tc => selectedTestCases.includes(tc.id)).map(tc => (
              <li key={tc.id} className="list-group-item">
                {tc.name}
                <button onClick={() => handleRemoveTestCase(tc.id)} className="btn btn-danger btn-sm float-end">
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