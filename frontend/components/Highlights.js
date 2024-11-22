import React from "react";

const Highlights = () => {
  // Placeholder data for fixtures
  const highlights = [
    { id: 1, message: "Test Case TC001 failed 5 times in a row!" },
    { id: 2, message: "High variability observed in Test Case TC045." },
  ];

  return (
    <div className="card my-3">
      <div className="card-header">Highlights</div>
      <ul className="list-group list-group-flush">
        {highlights.map((highlight) => (
          <li key={highlight.id} className="list-group-item">
            {highlight.message}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default Highlights;
