import React, { useState } from 'react';
import {
  Box,
  Card,
  CardHeader,
  CardContent,
  ToggleButton,
  ToggleButtonGroup,
  Typography
} from '@mui/material';
import DocumentPanel from './components/DocumentPanel';
import MarkmapViewer from './components/MarkmapViewer';
import AnimationViewer from './components/AnimationViewer';

function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [documentText, setDocumentText] = useState('');
  const [showFullContext, setShowFullContext] = useState(false);
  const [viewMode, setViewMode] = useState('mindmap');
  const [summary, setSummary] = useState('');
  const [mindmapMarkdown, setMindmapMarkdown] = useState('');
  const [animationURL, setAnimationURL] = useState('');

  const handleToggleView = (event, newView) => {
    if (newView) setViewMode(newView);
  };

  const handleUpload = async () => {
    if (!selectedFile) return;
    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData,
      });
      if (!response.ok) throw new Error('File upload failed');
      const data = await response.json();
      setDocumentText(data.extractedText || '');
    } catch (error) {
      console.error(error);
      alert('Error uploading file.');
    }
  };

  const runPipeline = async () => {
    if (!documentText) {
      alert('No document text available. Please upload or enter text first.');
      return;
    }

    try {
      const summaryRes = await fetch('/api/summary', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: documentText }),
      });
      if (!summaryRes.ok) throw new Error('Summary generation failed');
      const summaryData = await summaryRes.json();
      setSummary(summaryData.summary);

      if (viewMode === 'mindmap') {
        const mindmapRes = await fetch('/api/mindmap', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ text: documentText }),
        });
        if (!mindmapRes.ok) throw new Error('Mindmap generation failed');
        const mindmapData = await mindmapRes.json();
        setMindmapMarkdown(mindmapData.mindmapMarkdown);
        setAnimationURL('');
      } else {
        const animationRes = await fetch('/api/animation', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ text: documentText }),
        });
        if (!animationRes.ok) throw new Error('Animation generation failed');
        const animationData = await animationRes.json();
        setAnimationURL(animationData.animationUrl);
        setMindmapMarkdown('');
      }
    } catch (error) {
      console.error(error);
      alert('Error running pipeline.');
    }
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        background: 'linear-gradient(45deg, #e1f5fe 0%, #fffde7 100%)',
        p: 2,
        boxSizing: 'border-box',
      }}
    >
      <Typography
        variant="h3"
        align="center"
        sx={{
          mb: 3,
          fontWeight: 'bold',
          color: '#1a237e',
          fontSize: { xs: '1.8rem', sm: '2.5rem', md: '3rem' },
        }}
      >
        EduVision – Concepts in Motion
      </Typography>

      <Box
        sx={{
          display: 'flex',
          flexDirection: { xs: 'column', md: 'row' },
          height: 'calc(100vh - 120px)', // subtract header + padding
          gap: 2,
        }}
      >
        {/* Left - Document Panel (1/3 width) */}
        <Box
          sx={{
            width: { xs: '100%', md: '33.33%' },
            height: '100%',
          }}
        >
          <DocumentPanel
            selectedFile={selectedFile}
            setSelectedFile={setSelectedFile}
            documentText={documentText}
            setDocumentText={setDocumentText}
            showFullContext={showFullContext}
            setShowFullContext={setShowFullContext}
            handleUpload={handleUpload}
            runPipeline={runPipeline}
          />
        </Box>

        {/* Right - Summary + Mindmap/Animation (2/3 width) */}
        <Box
          sx={{
            width: { xs: '100%', md: '66.66%' },
            display: 'flex',
            flexDirection: 'column',
            height: '100%',
            gap: 2,
          }}
        >
          {/* Summary Panel (1/6 height) */}
          <Card sx={{ flexBasis: '16.66%' }}>
            <CardHeader title="Summary" />
            <CardContent>
              <Box sx={{ height: '100%', overflowY: 'auto' }}>
                {summary ? (
                  <Typography variant="body1">{summary}</Typography>
                ) : (
                  <Typography variant="body2" color="text.secondary">
                    No summary yet. (Run Pipeline)
                  </Typography>
                )}
              </Box>
            </CardContent>
          </Card>

          {/* Mindmap/Animation Panel (2/3 height) */}
          <Card
            sx={{
              flexBasis: '66.66%',
              display: 'flex',
              flexDirection: 'column',
              flexGrow: 1,
            }}
          >
            <CardHeader
              title={viewMode === 'mindmap' ? 'Mindmap' : 'Animation'}
              action={
                <ToggleButtonGroup
                  value={viewMode}
                  exclusive
                  onChange={handleToggleView}
                >
                  <ToggleButton value="mindmap">Mindmap</ToggleButton>
                  <ToggleButton value="animation">Animation</ToggleButton>
                </ToggleButtonGroup>
              }
            />
            <CardContent sx={{ flexGrow: 1, overflow: 'auto' }}>
              {viewMode === 'mindmap' ? (
                mindmapMarkdown ? (
                  <MarkmapViewer markdown={mindmapMarkdown} />
                ) : (
                  <Typography variant="body2" color="text.secondary">
                    No mindmap yet. (Run Pipeline)
                  </Typography>
                )
              ) : animationURL ? (
                <AnimationViewer animationURL={animationURL} />
              ) : (
                <Typography variant="body2" color="text.secondary">
                  No animation yet. (Run Pipeline)
                </Typography>
              )}
            </CardContent>
          </Card>
        </Box>
      </Box>
    </Box>
  );
}

export default App;
