import os
from docx import Document
import pypandoc
import json
import datetime 
from docx.shared import Inches

def generate_docx(testcase, testsuite=None):
    docx_filename = f"testcase_{testcase.id}.docx"
    docx_path = f"/tmp/{docx_filename}"  # Store it temporarily
    # Create a DOCX document
    doc = Document()

    # Title
    doc.add_heading('Functional Test Case Document', level=1)
    doc.add_heading(f"Document Code: {testcase.oid}", level=2)
    doc.add_heading(f"Test Case Name: {testcase.name}", level=2)
    doc.add_heading(f"Version: {testcase.version}", level=2)

    # Approval Block
    doc.add_heading("Approval", level=3)
    doc.add_paragraph("Prepared by: [Your Name]")
    doc.add_paragraph("Approved by: [Approver Name]")
    doc.add_paragraph("Date: [Approval Date]")

    # Revision Chart
    doc.add_heading("Revision History", level=3)
    revision_table = doc.add_table(rows=1, cols=3)
    hdr_cells = revision_table.rows[0].cells
    hdr_cells[0].text = 'Version'
    hdr_cells[1].text = 'Date'
    hdr_cells[2].text = 'Description'

    # Add a row for the current version
    row_cells = revision_table.add_row().cells
    row_cells[0].text = testcase.version
    row_cells[1].text = datetime.datetime.now().strftime('%Y-%m-%d')
    row_cells[2].text = 'Initial creation'

    # Introduction Section
    doc.add_heading("1. Introduction", level=2)
    doc.add_heading("1.1 Purpose", level=3)
    doc.add_paragraph("This document describes the functional tests for the system...")  # Customize as needed
    doc.add_heading("1.2 Scope", level=3)
    doc.add_paragraph("The tests cover the following aspects...")  # Customize as needed
    doc.add_heading("1.3 Outline", level=3)
    doc.add_paragraph("This document includes the following sections...")  # Customize as needed
    doc.add_heading("1.4 Reference Material", level=3)
    doc.add_paragraph("List any references or related documents...")  # Customize as needed
    doc.add_heading("1.5 Definitions and Acronyms", level=3)
    doc.add_paragraph("Provide definitions and acronyms used in this document...")  # Customize as needed

    # Test Setup and Basic Configuration (Section 2)
    doc.add_heading("2. Test Setup and Basic Configuration", level=2)

    # Test Cases Section
    doc.add_heading("3. Test Cases and Reports", level=2)

    # Procedural Steps
    doc.add_heading("3.1 Test Case: " + testcase.name, level=3)

    # Parse the JSON content
    content = json.loads(testcase.content)

    # Create a 2-column table for Test Case Number and Name
    info_table = doc.add_table(rows=2, cols=2)
    info_table.autofit = False
    info_table.columns[0].width = Inches(2)  # 2:8 width ratio
    info_table.columns[1].width = Inches(8)

    info_table.cell(0, 0).text = "Test Case Number:"
    info_table.cell(0, 1).text = testcase.oid  # OID value

    info_table.cell(1, 0).text = "Test Case Name:"
    info_table.cell(1, 1).text = testcase.name

    # Add a heading for Procedural Steps
    doc.add_heading("Procedural Steps", level=2)

    # Create a 2-column table for Procedural Steps
    procedural_table = doc.add_table(rows=1, cols=2)
    procedural_table.autofit = False
    procedural_table.columns[0].width = Inches(2)  # 2:8 width ratio
    procedural_table.columns[1].width = Inches(8)

    # Define the headers
    procedural_table.cell(0, 0).text = "Step"
    procedural_table.cell(0, 1).text = "Description"

    # Populate the procedural steps
    for step, details in content['proceduralSteps'].items():
        for detail in details:
            row_cells = procedural_table.add_row().cells
            row_cells[0].text = step  # Step description
            row_cells[1].text = detail['stepDescription']  # Input description

    # Add a single column for Environment/Setup
    doc.add_heading("Environment/Setup", level=2)
    doc.add_paragraph("Specify environment/setup details here...")  # Placeholder

    # Create a 2-column table for Hardware, Software, and Other
    setup_table = doc.add_table(rows=1, cols=2)
    setup_table.autofit = False
    setup_table.columns[0].width = Inches(2)  # 2:8 width ratio
    setup_table.columns[1].width = Inches(8)

    setup_table.cell(0, 0).text = "Hardware:"
    setup_table.cell(0, 1).text = "Specify hardware here..."  # Placeholder

    setup_table.add_row().cells[0].text = "Software:"
    setup_table.add_row().cells[1].text = "Specify software here..."  # Placeholder

    # Add a single column for Intercase dependencies
    doc.add_heading("Intercase Dependencies", level=2)
    doc.add_paragraph("Specify intercase dependencies here...")  # Placeholder

    # Add a single column for Specifications
    doc.add_heading("Specifications", level=2)
    doc.add_paragraph("Specify specifications here...")  # Placeholder

    # Create a 3-column table for Input, Expected Output, and Actual Output
    spec_table = doc.add_table(rows=1, cols=3)
    spec_table.autofit = False
    spec_table.columns[0].width = Inches(4)  # 3:3:3 ratio
    spec_table.columns[1].width = Inches(4)
    spec_table.columns[2].width = Inches(4)

    # Define the headers
    spec_table.cell(0, 0).text = "Input"
    spec_table.cell(0, 1).text = "Expected Output"
    spec_table.cell(0, 2).text = "Actual Output"

    # Populate the input and expected output based on procedural steps
    for step, details in content['proceduralSteps'].items():
        for detail in details:
            row_cells = spec_table.add_row().cells
            row_cells[0].text = detail['stepDescription']  # Input description
            row_cells[1].text = detail['expectedOutput']  # Expected output
            row_cells[2].text = ""  # Leave Actual Output blank

    doc.save(docx_path)
    return [docx_filename, docx_path]



def generate_pdf(testcase, testsuite=None):
    # First, generate DOCX
    docx_filename, docx_path = generate_docx(testcase)

    # Convert DOCX to PDF
    pdf_filename = f"testcase_{testcase.id}.pdf"
    pdf_path = f"/tmp/{pdf_filename}"

    try:
        # Convert DOCX to PDF using pypandoc
        output = pypandoc.convert_file(docx_path, 'pdf', outputfile=pdf_path)
    except OSError as e:
        return None, f"Error converting to PDF: {str(e)}"
    
    return pdf_filename, pdf_path
