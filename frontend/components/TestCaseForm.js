import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Editor from './Editor'


axios.defaults.headers.common['X-CSRFToken'] = csrftoken;

const TestCaseForm = ({ existingData, onSave }) => {
  const [sections, setSections] = useState({
    Setup: [{ stepDescription: '', expectedOutput: '' }],
    Start: [{ stepDescription: '', expectedOutput: '' }],
    Measure: [{ stepDescription: '', expectedOutput: '' }],
    Stop: [{ stepDescription: '', expectedOutput: '' }],
    Shutdown: [{ stepDescription: '', expectedOutput: '' }],
    Contingencies: [{ stepDescription: '', expectedOutput: '' }],
  });

  const [title, setTitle] = useState('');
  const [oid, setOid] = useState('');
  const [description, setDescription] = useState('');
  const [testCaseId, setTestCaseId] = useState('');

  useEffect(() => {
    if (existingData) {

      setTitle(existingData.title);
      setOid(existingData.oid);
      setDescription(existingData.description);
      setTestCaseId(existingData.id);
      setSections(existingData.proceduralSteps);
    }
  }, [existingData]);

  const handleAddStep = (section) => {
    setSections({
      ...sections,
      [section]: [...sections[section], { stepDescription: '', expectedOutput: '' }],
    });
  };

  const handleRemoveStep = (section, index) => {
    const updatedSteps = sections[section].filter((_, i) => i !== index);
    setSections({ ...sections, [section]: updatedSteps });
  };

  const handleStepChange = (section, index, field, value) => {
    const updatedSteps = sections[section].map((step, i) =>
      i === index ? { ...step, [field]: value } : step
    );
    setSections({ ...sections, [section]: updatedSteps });
  };

  const handleSubmit = async (e, action) => {
    e.preventDefault();

    const content = {
      description,
      proceduralSteps: sections,
    };

    const jsonData = {
      name: title,
      content: JSON.stringify(content),
    };

    if (oid.trim().length > 0) {
      jsonData.oid = oid.trim().toUpperCase();
    }

    try {
      let response;
      if (testCaseId) {
        response = await axios.put(`/tests/test-cases/testcases/${testCaseId}/`, jsonData, {
          headers: {
            'Content-Type': 'application/json',
          },
        });
      } else {
        response = await axios.post('/tests/test-cases/testcases/', jsonData, {
          headers: {
            'Content-Type': 'application/json',
          },
        });
        setTestCaseId(response.data.id);
      }

      if (onSave) onSave(response.data);

      if (action === 'edit') {
        window.location.href = `/tests/test-cases/edit/${response.data.id}/`;
      } else if (action === 'view') {
        window.location.href = `/tests/test-cases/${response.data.id}/`;
      }
    } catch (error) {
      console.error('Error saving the test case:', error);
      alert('Error saving the test case. Please try again.');
    }
  };

  return (
    <>
    <form onSubmit={handleSubmit}>
      {/* Title */}
      <div className="mb-3">
        <label htmlFor="title" className="form-label">Test Case Title</label>
        <input
          type="text"
          id="title"
          className="form-control"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          required
        />
      </div>

      {/* OID */}
      <div className="mb-3">
        <label htmlFor="oid" className="form-label">OID</label>
        <input
          type="text"
          id="oid"
          className="form-control"
          value={oid}
          onChange={(e) => setOid(e.target.value)}
        />
      </div>

      {/* Description */}
      <div className="mb-3">
        <label htmlFor="description" className="form-label">Description</label>
        <div className="border p-3">
          <Editor markdown={description} onChange={setDescription}/>
        </div>
      </div>

      {/* Procedural Steps */}
      <div className="accordion" id="proceduralStepsAccordion">
        {Object.keys(sections).map((section, idx) => {
          const collapseId = `collapse-${section}`;
          return (
            <div key={idx} className="accordion-item">
              <h2 className="accordion-header" id={`heading-${section}`}>
                <button
                  className="accordion-button collapsed"
                  type="button"
                  data-bs-toggle="collapse"
                  data-bs-target={`#${collapseId}`}
                  aria-expanded="false"
                  aria-controls={collapseId}
                >
                  {section}
                </button>
              </h2>
              <div
                id={collapseId}
                className="accordion-collapse collapse"
                aria-labelledby={`heading-${section}`}
                data-bs-parent="#proceduralStepsAccordion"
              >
                <div className="accordion-body">
                  {sections[section].map((step, index) => (
                    <div key={index} className="mb-4">
                      <label className="form-label">Step Description</label>
                      <div className="border p-3">
                        <Editor markdown={step.stepDescription}
                          onChange={(value) => handleStepChange(section, index, 'stepDescription', value)}
                        />
                      </div>
                      <label className="form-label">Expected Output</label>
                      <div className="border p-3">
                        <Editor markdown={step.expectedOutput}
                          onChange={(value) => handleStepChange(section, index, 'expectedOutput', value)}
                        />
                      </div>
                      <button
                        type="button"
                        className="btn btn-danger mt-2"
                        onClick={() => handleRemoveStep(section, index)}
                      >
                        Remove Step
                      </button>
                    </div>
                  ))}
                  <button
                    type="button"
                    className="btn btn-secondary"
                    onClick={() => handleAddStep(section)}
                  >
                    Add Another Step
                  </button>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Save Buttons */}
      <button type="button" className="btn btn-primary mt-4" onClick={(e) => handleSubmit(e, 'view')}>
        Save and View
      </button>
      <button type="button" className="btn btn-secondary mt-4" onClick={(e) => handleSubmit(e, 'edit')}>
        Save and Continue Editing
      </button>
    </form>
    <div id="editor-popup-container"></div>
  </>
  );
};

export default TestCaseForm;
