// TestCaseForm.js

import React, { useState, useRef } from 'react';
import axios from 'axios';
import MarkdownIt from 'markdown-it';
import MdEditor from 'react-markdown-editor-lite';
import 'react-markdown-editor-lite/lib/index.css'; // Import editor styles

axios.defaults.headers.common['X-CSRFToken'] = csrftoken;

// Initialize Showdown or Remarkable
import Showdown from 'showdown';
const converter = new Showdown.Converter({
  tables: true,
  simplifiedAutoLink: true,
});

const TestCaseForm = ({ existingData, onSave }) => {
  // Initialize procedural sections
  const initialSections = existingData?.proceduralSteps || {
    Setup: [{ stepDescription: '', expectedOutput: '' }],
    Start: [{ stepDescription: '', expectedOutput: '' }],
    Measure: [{ stepDescription: '', expectedOutput: '' }],
    Stop: [{ stepDescription: '', expectedOutput: '' }],
    Shutdown: [{ stepDescription: '', expectedOutput: '' }],
    Contingencies: [{ stepDescription: '', expectedOutput: '' }],
  };

  const [sections, setSections] = useState(initialSections);
  const [title, setTitle] = useState(existingData?.title || '');
  const [description, setDescription] = useState(existingData?.description || '');
  const [testCaseId, setTestCaseId] = useState(existingData?.testCaseId || '');
  const [isUploading, setIsUploading] = useState(false);

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
  const handleSubmit = async (e) => {
    e.preventDefault();

    const content = {
      description: description,
      id: testCaseId,
      proceduralSteps: sections
    };
    const jsonData = {
      name: title,
      content: JSON.stringify(content)
    };
    
    console.log(jsonData);
    // Uncomment when API is ready
    try {
      const response = await axios.post('/tests/test-cases/testcases/', jsonData, {
        headers: {
          'Content-Type': 'application/json',
        },
      });
      console.log('Test case saved:', response.data);
      if (onSave) onSave(response.data); // Callback to parent component
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

      {/* Test Case ID */}
      <div className="mb-3">
        <label htmlFor="testCaseId" className="form-label">Test Case ID</label>
        <input
          type="text"
          id="testCaseId"
          className="form-control"
          value={testCaseId}
          onChange={(e) => setTestCaseId(e.target.value)}
          required
        />
      </div>

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
                        {/* Hidden File Input for Image Upload */}
                        <input
                          type="file"
                          accept="image/*"
                          style={{ display: 'none' }}
                          ref={(el) => (fileInputRefs.current[`${section}-${index}-image`] = el)}
                          onChange={(e) => {
                            if (e.target.files && e.target.files[0]) {
                              handleImageUpload(section, index, e.target.files[0]);
                            }
                          }}
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

      <button type="submit" className="btn btn-primary mt-4">Save Test Case</button>
    </form>
  );
};

export default TestCaseForm;
