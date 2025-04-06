import React from 'react';

const AnimationViewer = ({ animationURL }) => {
  if (!animationURL) {
    return null;
  }
  return (
    <video
      src={animationURL}
      controls
      style={{ width: '100%', maxHeight: '400px' }}
    />
  );
};

export default AnimationViewer;
