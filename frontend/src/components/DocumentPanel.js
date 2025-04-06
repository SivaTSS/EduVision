import React from 'react';
import {
  Box,
  Button,
  TextField,
  Typography,
  Paper,
  Switch,
  FormControlLabel
} from '@mui/material';

/**
 * DocumentPanel
 * -------------
 * Handles:
 * - Drag & drop area
 * - Manual text input
 * - "Upload" button
 * - "Run Pipeline" button
 * - "Show Full Context" toggle
 *
 * Props:
 * - selectedFile: file or null
 * - setSelectedFile: function to update selectedFile
 * - documentText: string
 * - setDocumentText: function to update text
 * - showFullContext: boolean
 * - setShowFullContext: function to toggle context
 * - handleUpload: function to upload file
 * - runPipeline: function to run pipeline
 */
const DocumentPanel = ({
  selectedFile,
  setSelectedFile,
  documentText,
  setDocumentText,
  showFullContext,
  setShowFullContext,
  handleUpload,
  runPipeline
}) => {
  // Drag & drop handlers
  const handleDragOver = (e) => {
    e.preventDefault();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    if (e.dataTransfer.files?.[0]) {
      setSelectedFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files?.[0]) {
      setSelectedFile(e.target.files[0]);
    }
  };

  return (
    <Paper sx={{ p: 2 }} elevation={3}>
      <Typography variant="h6" sx={{ mb: 2 }}>
        Document
      </Typography>

      {/* Drag-and-drop area */}
      <Box
        sx={{
          border: '2px dashed #ccc',
          borderRadius: '8px',
          p: 2,
          textAlign: 'center',
          mb: 2
        }}
        onDragOver={handleDragOver}
        onDrop={handleDrop}
      >
        <Typography variant="body1" sx={{ mb: 1 }}>
          Drag & Drop files here
        </Typography>
        <Typography variant="body2" color="text.secondary">
          or
        </Typography>
        <Button variant="contained" component="label" sx={{ mt: 1 }}>
          Select File
          <input type="file" hidden onChange={handleFileChange} />
        </Button>
      </Box>

      {/* Manually typed text area */}
      <TextField
        label="Or paste custom text"
        multiline
        rows={4}
        fullWidth
        value={documentText}
        onChange={(e) => setDocumentText(e.target.value)}
        sx={{ mb: 2 }}
      />

      {/* Upload & Run Pipeline */}
      <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
        <Button
          variant="contained"
          color="primary"
          onClick={handleUpload}
          disabled={!selectedFile}
        >
          Upload
        </Button>
        <Button variant="contained" color="secondary" onClick={runPipeline}>
          Run Pipeline
        </Button>
      </Box>

      {/* Toggle Full Context */}
      {documentText && (
        <FormControlLabel
          control={
            <Switch
              checked={showFullContext}
              onChange={() => setShowFullContext(!showFullContext)}
            />
          }
          label="Show Full Context"
        />
      )}

      {/* Full Document Text (hidden unless toggled) */}
      {showFullContext && (
        <Paper
          variant="outlined"
          sx={{
            p: 2,
            mt: 2,
            maxHeight: 200,
            overflowY: 'auto'
          }}
        >
          <Typography variant="body2">{documentText}</Typography>
        </Paper>
      )}
    </Paper>
  );
};

export default DocumentPanel;
