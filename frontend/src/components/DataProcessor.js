import React, { useState } from 'react';
import {
  Box,
  Stepper,
  Step,
  StepLabel,
  Button,
  Typography,
} from '@mui/material';
import axios from 'axios';
import config from '../config';
import FileUpload from './FileUpload';
import TransformationConfig from './TransformationConfig';
import ProcessingStatus from './ProcessingStatus';

const steps = ['Upload Data', 'Configure Transformations', 'Process & Download'];

function DataProcessor() {
  const [activeStep, setActiveStep] = useState(0);
  const [selectedFile, setSelectedFile] = useState(null);
  const [configState, setConfig] = useState({
    transformations: [],
    input_column: '',
    batch_size: 1000
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [processingStatus, setProcessingStatus] = useState(null);
  const [result, setResult] = useState(null);

  const handleNext = () => {
    setActiveStep((prevStep) => prevStep + 1);
  };

  const handleBack = () => {
    setActiveStep((prevStep) => prevStep - 1);
  };

  const handleFileSelect = (file) => {
    console.log('File selected:', file); // Debug log
    setSelectedFile(file);
    handleNext();
  };

  const handleConfigUpdate = (newConfig) => {
    setConfig(newConfig);
  };

  const handleProcess = async () => {
    if (!selectedFile || !configState.input_column || configState.transformations.length === 0) {
      setError('Please upload a file, select an input column, and add at least one transformation');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      // Upload file first
      const formData = new FormData();
      formData.append('file', selectedFile);
      
      const uploadResponse = await axios.post(`${config.API_BASE_URL}/api/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      const fileId = uploadResponse.data.file_id;
      
      // Format the processing config according to the backend schema
      const processingConfig = {
        transformations: configState.transformations.map(t => ({
          type: t.type,
          params: t.params || {}
        })),
        input_column: configState.input_column,
        output_column: configState.output_column || `processed_${configState.input_column}`,
        batch_size: configState.batch_size || 1000
      };

      // Debug log
      console.log('Config State:', configState);
      console.log('Processing Config:', processingConfig);
      
      // Start processing with properly formatted config
      const response = await axios.post(`${config.API_BASE_URL}/api/process/${fileId}`, processingConfig, {
        headers: { 'Content-Type': 'application/json' }
      });

      console.log('Process Response:', response.data);
      
      // Start polling for status
      setProcessingStatus('processing');
      pollStatus(fileId);
      
    } catch (err) {
      console.error('Processing error:', err);
      console.error('Error response:', err.response?.data);
      setError(err.response?.data?.detail || 'Error processing file');
      setProcessingStatus('error');
    } finally {
      setLoading(false);
    }
  };

  const pollStatus = async (fileId) => {
    try {
      const statusResponse = await axios.get(`${config.API_BASE_URL}/api/status/${fileId}`);
      const statusData = statusResponse.data;
      
      if (statusData.status === 'completed') {
        setResult({
          success: true,
          resultFile: statusData.result_file
        });
        setProcessingStatus('completed');
      } else if (statusData.status === 'processing') {
        setTimeout(() => pollStatus(fileId), 1000); // Check again in 1 second
      } else {
        throw new Error(statusData.error || 'Processing failed');
      }
    } catch (err) {
      console.error('Error polling status:', err);
      setError(err.response?.data?.detail || 'Error polling status');
      setProcessingStatus('error');
    }
  };

  const getStepContent = (step) => {
    switch (step) {
      case 0:
        return (
          <Box sx={{ maxWidth: 600, mx: 'auto', p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Upload Your Data File
            </Typography>
            <FileUpload onFileSelect={handleFileSelect} />
            {selectedFile && (
              <Typography variant="body2" sx={{ mt: 2, color: 'success.main' }}>
                Selected file: {selectedFile.name}
              </Typography>
            )}
          </Box>
        );
      case 1:
        return (
          <TransformationConfig
            config={configState}
            onConfigUpdate={handleConfigUpdate}
          />
        );
      case 2:
        return (
          <ProcessingStatus
            loading={loading}
            error={error}
            processingStatus={processingStatus}
            result={result}
            onProcess={handleProcess}
          />
        );
      default:
        return 'Unknown step';
    }
  };

  return (
    <Box sx={{ width: '100%', p: 3 }}>
      <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
        {steps.map((label) => (
          <Step key={label}>
            <StepLabel>{label}</StepLabel>
          </Step>
        ))}
      </Stepper>

      <Box sx={{ mt: 4, mb: 4 }}>
        {getStepContent(activeStep)}
      </Box>

      <Box sx={{ display: 'flex', justifyContent: 'space-between', pt: 2 }}>
        <Button
          variant="outlined"
          onClick={handleBack}
          disabled={activeStep === 0}
        >
          Back
        </Button>

        {activeStep < steps.length - 1 && (
          <Button
            variant="contained"
            onClick={handleNext}
            disabled={
              (activeStep === 0 && !selectedFile) ||
              (activeStep === 1 && (!configState.input_column || configState.transformations.length === 0))
            }
          >
            Next
          </Button>
        )}
      </Box>
    </Box>
  );
}

export default DataProcessor;
