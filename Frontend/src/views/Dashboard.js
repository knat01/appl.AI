import React, { useState, useEffect } from "react";
import axios from 'axios';
import { Button, Card, CardHeader, CardBody, CardTitle, Container, Row, Col, FormGroup, Label, Input, Table, Modal, ModalHeader, ModalBody, ModalFooter } from "reactstrap";

function EmailPreviewModal({ recipientEmail, emailBody, isOpen, toggle }) {
  return (
    <Modal isOpen={isOpen} toggle={toggle}>
      <ModalHeader toggle={toggle}>Job Application Email Preview</ModalHeader>
      <ModalBody>
        <p><strong>Email to be sent to:</strong> {recipientEmail}</p>
        <hr />
        <p><strong>Email Body:</strong></p>
        <pre style={{ color: 'black' }}>{emailBody}</pre> 
      </ModalBody> 
      <ModalFooter>
        <Button color="secondary" onClick={toggle}>Close</Button>
        {/* Optionally, add a "Send Email" button here to open the user's email client */}
      </ModalFooter>
    </Modal>
  );
}


function Dashboard() {
  const [file, setFile] = useState(null);
  const [error, setError] = useState("");
  const [jobData, setJobData] = useState([]);
  const [apiKey, setApiKey] = useState("");
  const [modal, setModal] = useState(true);
  const [showUpload, setShowUpload] = useState(false);
  const [images, setImages] = useState([]);
  const [description, setDescription] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const [isLoadingAnalyze, setIsLoadingAnalyze] = useState(false); 
  const [isLoadingResume, setIsLoadingResume] = useState(false); 
  const [isLoadingCoverLetter, setIsLoadingCoverLetter] = useState(false); 
  const [isLoadingApply, setIsLoadingApply] = useState(false); 
  const [startIndex, setStartIndex] = useState(5); 
  const [loadMoreJobsLoading, setLoadMoreJobsLoading] = useState(false); 

  const [emailPreviewModalData, setEmailPreviewModalData] = useState({
    recipientEmail: "",
    emailBody: "",
    isOpen: false
  });

  // State to track loading status for each job item
  const [loadingStates, setLoadingStates] = useState({}); 


  const postImage = async ({ image, description }) => {
    const formData = new FormData();
    formData.append("image", image);
    formData.append("description", description);

    try {
      const result = await axios.post('http://localhost:8080/images', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setJobData(result.data.emailResults);
      console.log("Response from backend:", result.data); 
      return result.data;
    } catch (err) {
      console.error('Error posting image:', err);
      setError('Error posting image');
      return null;
    }
  };

  const submit = async (event) => {
    event.preventDefault();
    setError("");
    setIsLoadingAnalyze(true); 

    try {
      const result = await postImage({ image: file, description });
      if (result && result.imagePath) {
        setImages([result.imagePath, ...images]);
      } else {
        setError('Image upload failed: No imagePath returned');
      }
    } catch (err) {
      console.error('Error posting image:', err);
      setError('Error posting image');
    } finally {
      setIsLoadingAnalyze(false); 
    }
  };


  const fileSelected = event => {
    const file = event.target.files[0];
    setFile(file);
  };

  const handleGenerateResume = async (jobItem) => {
    setLoadingStates((prevStates) => ({ ...prevStates, [jobItem.job_link]: { resume: true } })); 

    try {
      const response = await axios.post('http://localhost:8080/generate-resume', { jobItem });
      console.log('Response from backend:', response.data);
  
      if (response.data && response.data.resume) {
        // Create and submit form
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = 'https://www.overleaf.com/docs';
        form.target = '_blank';

        const input = document.createElement('input');
        input.type = 'hidden';
        input.name = 'snip_uri';
        input.value = response.data.resume;  // Ensure this is the correct property
        form.appendChild(input);

        document.body.appendChild(form);
        form.submit();
        document.body.removeChild(form);
      } else {
        console.error('No resume data URL provided by backend');
      }
    } catch (error) {
      console.error('Error generating resume:', error);
      alert("An error occurred while generating the resume. Please try again later.");
    } finally {
      setLoadingStates((prevStates) => ({ ...prevStates, [jobItem.job_link]: { resume: false } })); 
    }
  };

  const handleGenerateCoverLetter = async (jobItem) => {
    setLoadingStates((prevStates) => ({ ...prevStates, [jobItem.job_link]: { coverLetter: true } })); 

    try {
      const response = await axios.post('http://localhost:8080/generate-cover-letter', { jobItem });
      console.log('Response from backend:', response.data);

      if (response.data && response.data.cover_letter) {
        // Create and submit form
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = 'https://www.overleaf.com/docs?engine=lualatex';  // Specify the engine parameter
        form.target = '_blank'; // This will open the document in a new tab

        const input = document.createElement('input');
        input.type = 'hidden';
        input.name = 'snip_uri';
        input.value = response.data.cover_letter; // Use the data URL from the backend response
        form.appendChild(input);

        document.body.appendChild(form);
        form.submit(); // Automatically submit the form to Overleaf
        document.body.removeChild(form); // Clean up by removing the form after submission
      } else {
        console.error('No cover letter data URL provided by the backend');
        alert("No cover letter data was provided. Please try again.");
      }
    } catch (error) {
      console.error('Error generating cover letter:', error);
      alert("An error occurred while generating the cover letter. Please try again later.");
    } finally {
      setLoadingStates((prevStates) => ({ ...prevStates, [jobItem.job_link]: { coverLetter: false } })); 
    }
};

  const handleApplyToJob = (jobItem) => {
    setLoadingStates((prevStates) => ({ ...prevStates, [jobItem.job_link]: { apply: true } })); 

    try {
      // Logic to apply to job based on jobItem
      console.log("Applying to job:", jobItem);
    } finally {
      setLoadingStates((prevStates) => ({ ...prevStates, [jobItem.job_link]: { apply: false } })); 
    }
  };


  const handleGenerateEmail = async (jobItem) => {
    setLoadingStates((prevStates) => ({ ...prevStates, [jobItem.job_link]: { apply: true } })); 

    try {
      const response = await axios.post('http://localhost:8080/generate-email', { jobItem });
      const { emailBody, recipientEmail } = response.data;
      setEmailPreviewModalData({ recipientEmail, emailBody, isOpen: true });
    } catch (error) {
      console.error('Error generating email:', error);
      alert("An error occurred while generating the email. Please try again later.");
    } finally {
      setLoadingStates((prevStates) => ({ ...prevStates, [jobItem.job_link]: { apply: false } })); 
    }
  };

  const handleApiKeySubmit = (e) => {
    e.preventDefault();
    axios.post('http://localhost:8080/set-api-key', { apiKey })
      .then(response => {
        console.log("API key sent to backend:", response.data);
        setModal(false);
        setShowUpload(true);
      })
      .catch(error => {
        console.error("Error sending API key:", error);
        setError("Failed to set API key");
      });
  };

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleFindMoreJobs = async () => {
    setLoadMoreJobsLoading(true);

    try {
      const response = await axios.post('http://localhost:8080/find-more-jobs', { startIndex });
      const moreJobs = response.data.emailResults;

      if (moreJobs.length > 0) {
        setJobData([...jobData, ...moreJobs]);
        setStartIndex(startIndex + 5);
      } else {
        alert("No more jobs found or scraping is still in progress. Please try again later.");
      }
    } catch (error) {
      console.error('Error fetching more jobs:', error);
    } finally {
      setLoadMoreJobsLoading(false);
    }
  };

  return (
    <Container>
      <h1 className="text-center mt-4">Appl.ai - Your Job Application Automater</h1>

      {/* API Key Modal */}
      <Modal isOpen={modal} toggle={() => setModal(!modal)} backdrop="static" className="modal-dialog-centered">
        <ModalHeader toggle={() => setModal(!modal)}>Enter OpenAI API Key</ModalHeader>
        <ModalBody>
          <form onSubmit={handleApiKeySubmit}>
            <FormGroup>
              <Label for="apiKeyInput">API Key:</Label>
              <Input
                type="text"
                id="apiKeyInput"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                style={{ color: 'black' }}
              />
            </FormGroup>
            <Button type="submit" color="primary">Submit</Button>{' '}
            <Button color="secondary" onClick={() => setModal(!modal)}>Cancel</Button>
          </form>
          {error && <div className="error-message">{error}</div>}
        </ModalBody>
      </Modal>

      {/* Resume Upload Component (Shown after API key is entered) */}
      {showUpload && (
        <Row className="mt-4">
          <Col md="6" className="mx-auto">
            <Card>
              <CardBody className="text-center">
                <CardTitle tag="h5">Upload Your Resume (PDF Format)</CardTitle>
                <Input type="file" accept=".pdf" onChange={handleFileChange} />
                <Button color="primary" onClick={submit} disabled={!file} className="mt-3">
                  {isLoadingAnalyze ? <div className="button-overlay">Scraping Jobs from the Web for you...</div> : "Analyze and Find Jobs"} 
                </Button>
              </CardBody>
            </Card>
          </Col>
        </Row>
      )}

      {/* Table Section */}
      {jobData.length > 0 && (
        <Row>
          <Col md="12">
            <Card>
              <CardHeader>
                <CardTitle tag="h4">Job Details</CardTitle>
              </CardHeader>
              <CardBody>
                <Table className="tablesorter">
                  <thead className="text-primary">
                    <tr>
                      <th>No.</th>
                      <th>Company</th>
                      <th>Position</th>
                      <th>Pay</th>
                      <th>Location</th>
                      <th>Posting Link</th>
                      <th>Actions</th> 
                    </tr>
                  </thead>
                  <tbody>
                    {jobData.map((item, index) => (
                      <tr key={index}>
                        <td>{index + 1}</td>
                        <td>{item.company_name}</td>
                        <td>{item.position}</td>
                        <td>{item.pay}</td>
                        <td>{item.location}</td>
                        <td>
                          <a href={item.job_link} target="_blank" rel="noopener noreferrer">Link</a>
                        </td>
                        <td> 
  <Button color="primary" size="sm" onClick={() => handleGenerateResume(item)} style={{ marginRight: '5px' }} disabled={loadingStates[item.job_link]?.resume}> 
    {loadingStates[item.job_link]?.resume && <div className="button-overlay">Loading...</div>}
    {!loadingStates[item.job_link]?.resume && "Generate Resume"}
  </Button>
  <Button color="primary" size="sm" onClick={() => handleGenerateCoverLetter(item)} style={{ marginRight: '5px' }} disabled={loadingStates[item.job_link]?.coverLetter}> 
    {loadingStates[item.job_link]?.coverLetter && <div className="button-overlay">Loading...</div>}
    {!loadingStates[item.job_link]?.coverLetter && "Generate Cover Letter"}
  </Button>
  <Button color="primary" size="sm" onClick={() => handleGenerateEmail(item)} disabled={loadingStates[item.job_link]?.apply}> 
    {loadingStates[item.job_link]?.apply && <div className="button-overlay">Loading...</div>}
    {!loadingStates[item.job_link]?.apply && "Apply to Job"}
  </Button>
</td>
</tr>
))}
</tbody>
</Table>
</CardBody>
</Card>
</Col>
</Row>
)}
{/* Email Preview Modal */}
<EmailPreviewModal 
        recipientEmail={emailPreviewModalData.recipientEmail}
        emailBody={emailPreviewModalData.emailBody}
        isOpen={emailPreviewModalData.isOpen}
        toggle={() => setEmailPreviewModalData({ ...emailPreviewModalData, isOpen: false })}
      />
</Container>
);
}

export default Dashboard;