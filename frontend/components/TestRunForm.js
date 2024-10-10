import React, { useState, useEffect } from 'react';
import axios from 'axios';

axios.defaults.headers.common['X-CSRFToken'] = csrftoken;

const TestRunForm = ({ existingData }) => {
    const [availableTestCases, setAvailableTestCases] = useState([]); // List of all test cases
    const [selectedTestCases, setSelectedTestCases] = useState([]);   // Selected test cases for the run
    const [notes, setNotes] = useState(existingData?.notes || '');    // Notes field
    const [executions, setExecutions] = useState([]);                 // Test Execution entries

    // Fetch test cases on mount
    useEffect(() => {
        const fetchTestCases = async () => {
            try {
                const response = await axios.get('/tests/test-cases/testcases/');
                if (response.data.count > 0) {
                    setAvailableTestCases(response.data.results);
                }
            } catch (error) {
                console.error('Error fetching test cases:', error);
            }
        };

        fetchTestCases();
    }, []);

    // Function to parse human-readable duration to Django format HH:MM:SS
    const parseDuration = (input) => {
        const regex = /(?:(\d+)h)?\s*(?:(\d+)m)?\s*(?:(\d+)s)?/;
        const matches = regex.exec(input.trim());

        const hours = parseInt(matches[1] || 0, 10);
        const minutes = parseInt(matches[2] || 0, 10);
        const seconds = parseInt(matches[3] || 0, 10);

        const formattedDuration = `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
        return formattedDuration;
    };

    // Move test case from available to selected using oid
    const handleAddTestCase = (oid) => {
        const selected = availableTestCases.find(test => test.oid === oid);
        setAvailableTestCases(availableTestCases.filter(test => test.oid !== oid));
        setSelectedTestCases([...selectedTestCases, selected]);
    };

    // Move test case back from selected to available using oid
    const handleRemoveTestCase = (oid) => {
        const removed = selectedTestCases.find(test => test.oid === oid);
        setSelectedTestCases(selectedTestCases.filter(test => test.oid !== oid));
        setAvailableTestCases([...availableTestCases, removed]);
    };

    // Handler for updating execution results
    const handleExecutionChange = (oid, field, value) => {
        const updatedExecutions = executions.map(exec => {
            if (exec.testcase === oid) {
                return { ...exec, [field]: value };
            }
            return exec;
        });
        setExecutions(updatedExecutions);
    };

    // Initialize the test execution rows when a test case is added
    useEffect(() => {
        const newExecutions = selectedTestCases.map(test => ({
            testcase: test.oid,  // Now using OID instead of ID
            result: 'NOT RUN',
            notes: '',
            duration: ''
        }));
        setExecutions(newExecutions);
    }, [selectedTestCases]);

    // Submit handler to send the OID of each test case
    const handleSubmit = async (e) => {
        e.preventDefault();
        const payload = {
            notes,
            executions: executions.map(exec => ({
                testcase: exec.testcase,  // OID sent here
                result: exec.result,
                notes: exec.notes,
                duration: parseDuration(exec.duration), // Convert to HH:MM:SS
            }))
        };

        try {
            let response;
            if (existingData?.id) {
                // Update existing test run
                response = await axios.put(`/tests/test-cases/testruns/${existingData.id}/`, payload);
            } else {
                // Create new test run
                response = await axios.post('/tests/test-cases/testruns/', payload);
            }
            /* Redirect to detail page */
            window.location.href = `/tests/test-runs/${response.data.id}/`;
        } catch (error) {
            console.error('Error saving test run:', error);
        }
    };

    return (
        <div className="container mt-4">
            <form onSubmit={handleSubmit}>
                {/* Notes Section */}
                <div className="mb-3">
                    <label htmlFor="notes" className="form-label">Notes</label>
                    <textarea
                        id="notes"
                        className="form-control"
                        rows="4"
                        value={notes}
                        onChange={(e) => setNotes(e.target.value)}
                        placeholder="Add any high-level notes or description for the test run..."
                    />
                </div>

                {/* Dual Pane Select */}
                <div className="row">
                    <div className="col-md-5">
                        <h5>Available Test Cases</h5>
                        <ul className="list-group">
                            {availableTestCases.map(test => (
                                <li key={test.oid} className="list-group-item d-flex justify-content-between align-items-center">
                                    {test.name}
                                    <button
                                        type="button"
                                        className="btn btn-sm btn-primary"
                                        onClick={() => handleAddTestCase(test.oid)}
                                    >
                                        Add
                                    </button>
                                </li>
                            ))}
                        </ul>
                    </div>

                    <div className="col-md-2 text-center">
                        <h5>Actions</h5>
                        <p>&larr; Add / Remove &rarr;</p>
                    </div>

                    <div className="col-md-5">
                        <h5>Selected Test Cases</h5>
                        <ul className="list-group">
                            {selectedTestCases.map(test => (
                                <li key={test.oid} className="list-group-item d-flex justify-content-between align-items-center">
                                    {test.name}
                                    <button
                                        type="button"
                                        className="btn btn-sm btn-danger"
                                        onClick={() => handleRemoveTestCase(test.oid)}
                                    >
                                        Remove
                                    </button>
                                </li>
                            ))}
                        </ul>
                    </div>
                </div>

                {/* Test Execution Inputs */}
                {selectedTestCases.length > 0 && (
                    <div className="mt-4">
                        <h5>Test Execution Details</h5>
                        <table className="table table-bordered">
                            <thead>
                                <tr>
                                    <th>Test Case</th>
                                    <th>Result</th>
                                    <th>Notes</th>
                                    <th>Duration</th>
                                </tr>
                            </thead>
                            <tbody>
                                {selectedTestCases.map(test => (
                                    <tr key={test.oid}>
                                        <td>{test.name}</td>
                                        <td>
                                            <select
                                                className="form-select"
                                                value={executions.find(exec => exec.testcase === test.oid)?.result || 'NOT RUN'}
                                                onChange={(e) =>
                                                    handleExecutionChange(test.oid, 'result', e.target.value)
                                                }
                                            >
                                                <option value="PASS">PASS</option>
                                                <option value="FAIL">FAIL</option>
                                                <option value="SKIPPED">SKIPPED</option>
                                                <option value="ERROR">ERROR</option>
                                                <option value="NOT RUN">NOT RUN</option>
                                            </select>
                                        </td>
                                        <td>
                                            <input
                                                type="text"
                                                className="form-control"
                                                value={executions.find(exec => exec.testcase === test.oid)?.notes || ''}
                                                onChange={(e) =>
                                                    handleExecutionChange(test.oid, 'notes', e.target.value)
                                                }
                                            />
                                        </td>
                                        <td>
                                            <input
                                                type="text"
                                                className="form-control"
                                                placeholder="e.g. 5m 30s"
                                                value={executions.find(exec => exec.testcase === test.oid)?.duration || ''}
                                                onChange={(e) =>
                                                    handleExecutionChange(test.oid, 'duration', e.target.value)
                                                }
                                            />
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}

                <button type="submit" className="btn btn-success">Save Test Run</button>
            </form>
        </div>
    );
};

export default TestRunForm;
