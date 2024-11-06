import React, { useState, useEffect } from 'react';
import axios from 'axios';

axios.defaults.headers.common['X-CSRFToken'] = csrftoken;

const TestSuiteForm = ({ existingData }) => {
  const [name, setName] = useState(existingData?.name || '');
  const [content, setContent] = useState(existingData?.content || '');
  const [availableTestCases, setAvailableTestCases] = useState([]); // Store all available test cases
  const [selectedTestCases, setSelectedTestCases] = useState(existingData?.testcases || []); // Store selected test cases
  const [searchQuery, setSearchQuery] = useState(''); // Search query for filtering test cases
  const [currentPage, setCurrentPage] = useState(1); // Current page in pagination
  const [itemsPerPage, setItemsPerPage] = useState(10); // Items per page option (10, 25, 50, 100)

  useEffect(() => {
    const fetchAllTestCases = async () => {
      try {
        let allTestCases = [];
        let nextPageUrl = '/tests/test-cases/testcases/';

        while (nextPageUrl) {
          const response = await axios.get(nextPageUrl);
          const selectedTestCaseIds = existingData?.testcases.map(tc => tc.id) || [];

          // Filter out already selected test cases
          const filteredTestCases = response.data.results.filter(tc => !selectedTestCaseIds.includes(tc.id));
          allTestCases = allTestCases.concat(filteredTestCases);

          nextPageUrl = response.data.next;
        }

        setAvailableTestCases(allTestCases);
      } catch (error) {
        console.error('Error fetching test cases:', error);
      }
    };

    fetchAllTestCases();
  }, [existingData]);

  // Filter and paginate test cases based on search query, items per page, and current page
  const filteredTestCases = availableTestCases.filter(tc => 
    tc.name.toLowerCase().includes(searchQuery.toLowerCase()) || 
    tc.oid.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const totalItems = filteredTestCases.length;
  const totalPages = Math.ceil(totalItems / itemsPerPage);
  const paginatedTestCases = filteredTestCases.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  );

  // Handle form submission
  const handleSubmit = async (e, action) => {
    e.preventDefault();

    const payload = {
      name,
      content,
      testcases: selectedTestCases.map(tc => tc.id),
    };

    try {
      let response;
      if (existingData?.id) {
        response = await axios.put(`/tests/test-cases/testsuites/${existingData.id}/`, payload);
      } else {
        response = await axios.post('/tests/test-cases/testsuites/', payload);
      }

      if (action === 'view') {
        window.location.href = `/tests/test-suites/${response.data.id}/`;
      } else if (action === 'edit') {
        window.location.href = `/tests/test-suites/edit/${response.data.id}/`;
      }
    } catch (error) {
      console.error('Error saving test suite:', error);
    }
  };

  // Pagination control handlers
  const handlePageChange = (newPage) => {
    setCurrentPage(newPage);
  };

  const handleItemsPerPageChange = (e) => {
    setItemsPerPage(Number(e.target.value));
    setCurrentPage(1); // Reset to the first page on items-per-page change
  };

  const handleAddTestCase = (id) => {
    const selected = availableTestCases.find(test => test.id === id);
    setAvailableTestCases(availableTestCases.filter(test => test.id !== id));
    setSelectedTestCases([...selectedTestCases, selected]);
  };

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

      {/* Search and Pagination Controls */}
      <div className="mb-3">
        <input
          type="text"
          className="form-control mb-2"
          placeholder="Search test cases..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />

        <label className="form-label">Items per page:</label>
        <select
          className="form-select mb-3"
          value={itemsPerPage}
          onChange={handleItemsPerPageChange}
        >
          {[10, 25, 50, 100].map(num => (
            <option key={num} value={num}>{num}</option>
          ))}
        </select>

        {/* Pagination */}
        <nav>
          <ul className="pagination">
            {[...Array(totalPages).keys()].map(page => (
              <li
                key={page + 1}
                className={`page-item ${currentPage === page + 1 ? 'active' : ''}`}
                onClick={() => handlePageChange(page + 1)}
              >
                <button className="page-link">{page + 1}</button>
              </li>
            ))}
          </ul>
        </nav>
      </div>

      {/* Dual-pane test case selection with pagination */}
      <div className="row">
        <div className="col-md-6">
          <h5>Available Test Cases</h5>
          <ul className="list-group">
            {paginatedTestCases.map(tc => (
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
