import React, { useEffect, useRef } from 'react';
import { Transformer } from 'markmap-lib';
import { Markmap } from 'markmap-view';
import * as d3 from 'd3';

const transformer = new Transformer();

const MarkmapViewer = ({ markdown }) => {
  const containerRef = useRef(null);

  useEffect(() => {
    if (!markdown) return;

    const { root } = transformer.transform(markdown);

    if (containerRef.current) {
      containerRef.current.innerHTML = '';
      const svg = d3.select(containerRef.current).append('svg');
      Markmap.create(svg.node(), null, root);
    }
  }, [markdown]);

  return (
    <div
      style={{
        height: '400px',
        border: '2px solid #ccc',
        borderRadius: '8px',
      }}
    >
      <div ref={containerRef}></div>
    </div>
  );
};

export default MarkmapViewer;
