import React from 'react';
import {
  Box,
  Typography,
  Button,
  CircularProgress,
  Alert,
  AlertTitle,
} from '@mui/material';
import CloudDownloadIcon from '@mui/icons-material/CloudDownload';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';

function ProcessingStatus({ processing, result, onProcess }) {
  const handleDownload = () => {
    if (result && result.resultFile) {
      // Create download URL using the backend endpoint
      const downloadUrl = `http://localhost:8000/api/download/${result.resultFile}`;
      
      // Create a temporary link element and trigger download
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.download = result.resultFile;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  return (
    <Box sx={{ textAlign: 'center' }}>
      {!processing && !result && (
        <Box>
          <Typography variant="h6" sx={{ mb: 3 }}>
            Ready to Process
          </Typography>
          <Button
            variant="contained"
            startIcon={<PlayArrowIcon />}
            onClick={onProcess}
            size="large"
          >
            Start Processing
          </Button>
        </Box>
      )}

      {processing && (
        <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 2 }}>
          <CircularProgress size={48} />
          <Typography variant="h6">
            Processing Your Data...
          </Typography>
          <Typography color="textSecondary">
            This may take a few moments
          </Typography>
        </Box>
      )}

      {result && !processing && (
        <Box>
          {result.success ? (
            <Box>
              <Alert severity="success" sx={{ mb: 3 }}>
                <AlertTitle>Processing Complete</AlertTitle>
                Your data has been successfully processed and is ready for download.
              </Alert>
              <Button
                variant="contained"
                startIcon={<CloudDownloadIcon />}
                onClick={handleDownload}
                size="large"
              >
                Download Results
              </Button>
            </Box>
          ) : (
            <Alert severity="error">
              <AlertTitle>Processing Failed</AlertTitle>
              {result.error || 'An error occurred while processing your data.'}
            </Alert>
          )}
        </Box>
      )}
    </Box>
  );
}

export default ProcessingStatus;
