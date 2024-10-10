import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import MarkdownIt from 'markdown-it';
import MdEditor from 'react-markdown-editor-lite';
import 'react-markdown-editor-lite/lib/index.css'; // Import editor styles

axios.defaults.headers.common['X-CSRFToken'] = csrftoken;

import Showdown from 'showdown';
const converter = new Showdown.Converter({
  tables: true,
  simplifiedAutoLink: true,
});

const TestCaseForm = ({ existingData, onSave }) => {
  // Initialize procedural sections
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
  const [isUploading, setIsUploading] = useState(false);

  useEffect(() => {
    if (existingData) {
      // Populate form with existing data for editing
      setTitle(existingData.title);
      setOid(existingData.oid);
      setDescription(existingData.description);
      setTestCaseId(existingData.id);
      setSections(existingData.proceduralSteps);
    }
  }, [existingData]);  // Re-run if existingData changes

  const fileInputRefs = useRef({});

  // Handle adding a new step to a specific section
  const handleAddStep = (section) => {
    setSections({
      ...sections,
      [section]: [...sections[section], { stepDescription: '', expectedOutput: '' }],
    });
  };

  // Handle removing a step from a specific section
  const handleRemoveStep = (section, index) => {
    const updatedSteps = sections[section].filter((_, i) => i !== index);
    setSections({ ...sections, [section]: updatedSteps });
  };

  // Handle changes in procedural steps
  const handleStepChange = (section, index, field, value) => {
    const updatedSteps = sections[section].map((step, i) =>
      i === index ? { ...step, [field]: value } : step
    );

    setSections({ ...sections, [section]: updatedSteps });
  };

  const handleEditorChange = (section, index, field, value) => {
    if (!isUploading) {
      handleStepChange(section, index, field, value);
    }
  };

  // Upload an image and insert the markdown link
  const handleImageUpload = async (section, index, file) => {
    setIsUploading(true);  // Disable onChange
    const formData = new FormData();
    formData.append('image', file);  // Ensure 'image' matches what the backend expects

    try {
      const response = await axios.post('/tests/api/upload-image/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      const imageUrl = response.data.url;
      const updatedStepDescription = sections[section][index].stepDescription + `\n![Image](${imageUrl})\n`;
      handleStepChange(section, index, 'stepDescription', updatedStepDescription);
    } catch (error) {
      console.error('Image upload failed:', error);
      alert('Image upload failed. Please try again.');
    } finally {
      setIsUploading(false);  // Re-enable onChange
    }
  };

  // Handle form submission
  const handleSubmit = async (e, action) => {
    e.preventDefault();

    const content = {
      description: description,
      proceduralSteps: sections,
    };

    const jsonData = {
      name: title,
      content: JSON.stringify(content),
    };

    if (oid.trim().length > 0) {
      jsonData.oid = oid.trim().toUpperCase()
    }
  
    try {
      let response;
      if (testCaseId) {
        // If testCaseId exists, update the existing test case with PUT
        response = await axios.put(`/tests/test-cases/testcases/${testCaseId}/`, jsonData, {
          headers: {
            'Content-Type': 'application/json',
          },
        });
      } else {
        // If testCaseId doesn't exist, create a new test case with POST
        response = await axios.post('/tests/test-cases/testcases/', jsonData, {
          headers: {
            'Content-Type': 'application/json',
          },
        });
        setTestCaseId(response.data.id); // Set new ID after creation
      }

      console.log('Test case saved:', response.data);
      if (onSave) onSave(response.data);

      // Redirect based on action
      if (action === 'edit') {
        // Redirect to edit page
        window.location.href = `/tests/test-cases/edit/${response.data.id}/`;
      } else if (action === 'view') {
        // Redirect to detail page
        window.location.href = `/tests/test-cases/${response.data.id}/`;
      }
    } catch (error) {
      console.error('Error saving the test case:', error);
      alert('Error saving the test case. Please try again.');
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      {/* Test Case Title */}
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

      { /* Test case OID */ }
      <div className="mb-3">
        <label htmlFor="oid" className="form-label">Test Case Identifier String (OID)</label>
        <input
          type="text"
          id="oid"
          className="form-control"
          value={oid}
          onChange={(e) => setOid(e.target.value)}
          required
        />
      </div>

      {/* Description with Markdown Editor */}
      <div className="mb-3">
        <label className="form-label">Description</label>
        <MdEditor
          value={description}
          style={{ height: '200px' }}
          renderHTML={(text) => converter.makeHtml(text)}
          onChange={({ text }) => setDescription(text)} // Update state on change
          toolbar={[
            'bold', 'italic', 'heading', '|', 'quote', 'unordered-list', 'ordered-list', '|',
            'link', 'image', '|', 'preview', 'fullscreen',
          ]}
          onImageUpload={(file) => handleImageUpload(section, index, file)}  // File upload handling
        />
      </div>

      {/* Test Case ID (Hidden for Update Scenario) */}
      {testCaseId && (
        <div className="mb-3">
          <label htmlFor="testCaseId" className="form-label">Test Case ID</label>
          <input
            type="text"
            id="testCaseId"
            className="form-control"
            value={testCaseId}
            readOnly  // Make it read-only for editing
          />
        </div>
      )}

      {/* Procedural Steps Accordion */}
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
                    <div key={index} className="step-group mb-4">
                      {/* Step Description */}
                      <div className="mb-3">
                        <label className="form-label">Step {index + 1} Description</label>
                        <MdEditor
                          value={step.stepDescription}
                          style={{ height: '200px' }}
                          renderHTML={(text) => converter.makeHtml(text)}
                          onChange={({ text }) => handleEditorChange(section, index, 'stepDescription', text)}
                          toolbar={[
                            'bold', 'italic', 'heading', '|', 'quote', 'unordered-list', 'ordered-list', '|',
                            'link', 'image', '|', 'preview', 'fullscreen',
                          ]}
                          onImageUpload={(file) => handleImageUpload(section, index, file)}  // File upload handling
                        />
                      </div>

                      {/* Expected Output */}
                      <div className="mb-3">
                        <label className="form-label">Expected Output</label>
                        <MdEditor
                          value={step.expectedOutput}
                          style={{ height: '200px' }}
                          renderHTML={(text) => converter.makeHtml(text)}
                          onChange={({ text }) => handleEditorChange(section, index, 'expectedOutput', text)}
                          toolbar={[
                            'bold', 'italic', 'heading', '|', 'quote', 'unordered-list', 'ordered-list', '|',
                            'link', 'image', '|', 'preview', 'fullscreen',
                          ]}
                          onImageUpload={(file) => handleImageUpload(section, index, file)}
                        />
                      </div>

                      <button type="button" className="btn btn-danger" onClick={() => handleRemoveStep(section, index)}>
                        Remove Step
                      </button>
                    </div>
                  ))}

                  <button type="button" className="btn btn-secondary" onClick={() => handleAddStep(section)}>
                    Add Another Step to {section}
                  </button>
                </div>
              </div>
            </div>
          );
        })}
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

export default TestCaseForm;
