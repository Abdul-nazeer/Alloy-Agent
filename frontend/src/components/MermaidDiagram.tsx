import { useEffect, useRef, useState } from 'react';
import mermaid from 'mermaid';

interface MermaidDiagramProps {
  chart: string;
  className?: string;
}

let mermaidInitialized = false;

export default function MermaidDiagram({ chart, className = '' }: MermaidDiagramProps) {
  const ref = useRef<HTMLDivElement>(null);
  const [svg, setSvg] = useState<string>('');

  useEffect(() => {
    // Initialize mermaid only once
    if (!mermaidInitialized) {
      mermaid.initialize({
        startOnLoad: false,
        theme: 'dark',
        themeVariables: {
          primaryColor: '#00E5FF',
          primaryTextColor: '#ffffff',
          primaryBorderColor: '#00E5FF',
          lineColor: '#00E5FF',
          secondaryColor: '#FF6A00',
          tertiaryColor: '#00FF85',
          background: '#0A0A0A',
          mainBkg: '#0A0A0A',
          secondBkg: '#050505',
          textColor: '#B8C1CC',
          border1: '#00E5FF',
          border2: '#FF6A00',
          fontFamily: 'ui-monospace, monospace',
        },
        flowchart: {
          curve: 'basis',
          padding: 20,
        },
      });
      mermaidInitialized = true;
    }

    // Render the diagram
    const renderDiagram = async () => {
      try {
        const id = `mermaid-${Math.random().toString(36).substr(2, 9)}`;
        const { svg: renderedSvg } = await mermaid.render(id, chart);
        setSvg(renderedSvg);
      } catch (error) {
        console.error('Mermaid rendering error:', error);
      }
    };

    renderDiagram();
  }, [chart]);

  return (
    <div 
      ref={ref} 
      className={className}
      dangerouslySetInnerHTML={{ __html: svg }}
      style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
      }}
    />
  );
}
