// TestCaseForm.js

import React, { useState, useRef } from 'react';
import axios from 'axios';
import MarkdownIt from 'markdown-it';
import MdEditor from 'react-markdown-editor-lite';
import 'react-markdown-editor-lite/lib/index.css'; // Import editor styles
import { Modal } from 'bootstrap'; // Assuming Bootstrap is used for modals

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

  // Refs for file inputs (optional if using hidden file inputs)
  const fileInputRefs = useRef({});

  // Function to retrieve CSRF token from meta tag
  const getCookie = (name) => {
    const cookieValue = document.cookie
      .split('; ')
      .find(row => row.startsWith(name + '='));
    return cookieValue ? decodeURIComponent(cookieValue.split('=')[1]) : null;
  };

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

  // Handle image upload
  const handleImageUpload = async (section, index, file) => {
    const formData = new FormData();
    formData.append('image', file);

    try {
      const response = await axios.post('/api/upload-image/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
          'X-CSRFToken': getCookie('csrf-token'),
        },
      });
      const imageUrl = response.data.url;

      // Insert the image markdown into the stepDescription at the end
      const updatedStepDescription = sections[section][index].stepDescription + `\n![Image](${imageUrl})\n`;
      handleStepChange(section, index, 'stepDescription', updatedStepDescription);
    } catch (error) {
      console.error('Image upload failed:', error);
      alert('Image upload failed. Please try again.');
    }
  };

  // Custom image handler for the editor
  const handleImageClick = (section, index) => {
    // Trigger a file input click
    const fileInput = fileInputRefs.current[`${section}-${index}-image`];
    if (fileInput) {
      fileInput.click();
    }
  };

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();

    const jsonData = {
      title,
      description,
      testCaseId,
      proceduralSteps: sections,
    };
    console.log(jsonData);
    // // Determine API endpoint and method based on existingData
    // const apiUrl = existingData ? `/api/test-cases/${existingData.id}/` : '/api/test-cases/';
    // const method = existingData ? 'put' : 'post';

    // try {
    //   const response = await axios({
    //     method: method,
    //     url: apiUrl,
    //     data: jsonData,
    //     headers: {
    //       'Content-Type': 'application/json',
    //       'X-CSRFToken': getCookie('csrf-token'),
    //     },
    //   });
    //   console.log('Test case saved:', response.data);
    //   if (onSave) onSave(response.data); // Callback to parent component

    //   // Close the modal
    //   const modalElement = document.getElementById('testCaseModal');
    //   if (modalElement) {
    //     const modal = Modal.getInstance(modalElement);
    //     if (modal) modal.hide();
    //   }
    // } catch (error) {
    //   console.error('There was an error saving the test case!', error);
    //   alert('There was an error saving the test case. Please try again.');
    // }
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

      {/* Description */}
      <div className="mb-3">
        <label htmlFor="description" className="form-label">Description</label>
        <textarea
          id="description"
          className="form-control"
          rows="3"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          required
        ></textarea>
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
        {Object.keys(sections).map((section, idx) => (
          <div key={idx} className="accordion-item">
            <h2 className="accordion-header" id={`heading-${section}`}>
              <button
                className="accordion-button collapsed"
                type="button"
                data-bs-toggle="collapse"
                data-bs-target={`#collapse-${section}`}
                aria-expanded="false"
                aria-controls={`collapse-${section}`}
              >
                {section}
              </button>
            </h2>
            <div
              id={`collapse-${section}`}
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
                        onChange={({ text }) => handleStepChange(section, index, 'stepDescription', text)}
                        config={{
                          view: {
                            menu: true,
                            md: true,
                            html: false, // Hide HTML view
                            both: false,
                          },
                          shortcuts: true,
                        }}
                        toolbar={[
                          'bold',
                          'italic',
                          'heading',
                          '|',
                          'quote',
                          'unordered-list',
                          'ordered-list',
                          '|',
                          'link',
                          'image',
                          '|',
                          'preview',
                          'fullscreen',
                        ]}
                        onImageUpload={(file) => {
                          // Handle image upload
                          handleImageUpload(section, index, file);
                        }}
                        onImageClick={() => handleImageClick(section, index)}
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
                      <label className="form-label">Expected Output / Success Criteria</label>
                      <MdEditor
                        value={step.expectedOutput}
                        style={{ height: '200px' }}
                        renderHTML={(text) => converter.makeHtml(text)}
                        onChange={({ text }) => handleStepChange(section, index, 'expectedOutput', text)}
                        config={{
                          view: {
                            menu: true,
                            md: true,
                            html: false, // Hide HTML view
                            both: false,
                          },
                          shortcuts: true,
                        }}
                        toolbar={[
                          'bold',
                          'italic',
                          'heading',
                          '|',
                          'quote',
                          'unordered-list',
                          'ordered-list',
                          '|',
                          'link',
                          'image',
                          '|',
                          'preview',
                          'fullscreen',
                        ]}
                        onImageUpload={(file) => {
                          // Handle image upload
                          handleImageUpload(section, index, file);
                        }}
                        onImageClick={() => handleImageClick(section, index)}
                      />
                      {/* Hidden File Input for Image Upload */}
                      <input
                        type="file"
                        accept="image/*"
                        style={{ display: 'none' }}
                        ref={(el) => (fileInputRefs.current[`${section}-${index}-output-image`] = el)}
                        onChange={(e) => {
                          if (e.target.files && e.target.files[0]) {
                            handleImageUpload(section, index, e.target.files[0]);
                          }
                        }}
                      />
                    </div>

                    {/* Remove Step Button */}
                    <button
                      type="button"
                      className="btn btn-danger"
                      onClick={() => handleRemoveStep(section, index)}
                    >
                      Remove Step
                    </button>
                  </div>
                ))}

                {/* Add Step Button */}
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => handleAddStep(section)}
                >
                  Add Another Step to {section}
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Submit Button */}
      <button type="submit" className="btn btn-primary mt-4">Save Test Case</button>
    </form>
  );
};

export default TestCaseForm;
