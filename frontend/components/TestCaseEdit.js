import React from 'react';

import TestCaseForm from './TestCaseForm';

const TestCaseEdit = ({message}) => {
  return (
    <div>
        <div>{message}</div>
        <TestCaseForm />
    </div>
  );
};

export default TestCaseEdit;