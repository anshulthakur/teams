import React, { useState, useEffect } from 'react';
import axios from 'axios';

const ImageBrowser = ({ onSelect, onClose }) => {
  const [images, setImages] = useState([]);

  // Fetch images from the server when the component mounts
  useEffect(() => {
    axios.get('/api/list-images/')
      .then(response => setImages(response.data))
      .catch(error => console.error('Error fetching images:', error));
  }, []);

  return (
    <div className="modal fade show" id="imageBrowserModal" tabIndex="-1" aria-labelledby="imageBrowserModalLabel" aria-modal="true" role="dialog" style={{ display: 'block', backgroundColor: 'rgba(0, 0, 0, 0.5)' }}>
      <div className="modal-dialog modal-lg">
        <div className="modal-content">
          <div className="modal-header">
            <h5 className="modal-title" id="imageBrowserModalLabel">Select an Image</h5>
            <button type="button" className="btn-close" aria-label="Close" onClick={onClose}></button>
          </div>
          <div className="modal-body">
            <div className="row">
              {/* Display the list of images */}
              {images.length > 0 ? (
                images.map((image, index) => (
                  <div key={index} className="col-md-4 mb-3">
                    <img
                      src={image} 
                      alt={`Image ${index + 1}`}
                      className="img-thumbnail"
                      style={{ cursor: 'pointer', maxWidth: '100%', height: 'auto' }}
                      onClick={() => onSelect(image)} // Call onSelect with the selected image URL
                    />
                  </div>
                ))
              ) : (
                <p>No images available.</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ImageBrowser;
