import React, { useEffect, useRef } from 'react';

export default function InsuranceGlobe() {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    let animationFrameId;
    
    // Set canvas size
    const resize = () => {
      canvas.width = 600;
      canvas.height = 600;
    };
    resize();
    
    // Globe properties
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    const radius = 180;
    
    // Particles (nodes)
    const numNodes = 60;
    const nodes = [];
    
    for (let i = 0; i < numNodes; i++) {
      // Spherical coordinates
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos((Math.random() * 2) - 1);
      
      nodes.push({
        theta,
        phi,
        speed: 0.002 + Math.random() * 0.003,
        size: 1 + Math.random() * 2,
        connections: []
      });
    }
    
    // Establish some connections between nearby nodes on the sphere surface
    for (let i = 0; i < nodes.length; i++) {
        for (let j = i + 1; j < nodes.length; j++) {
            // Rough proximity check in spherical coords for simplicity
            const dTheta = Math.abs(nodes[i].theta - nodes[j].theta);
            const dPhi = Math.abs(nodes[i].phi - nodes[j].phi);
            if (dTheta < 0.8 && dPhi < 0.8) {
                if (Math.random() > 0.5 && nodes[i].connections.length < 3) {
                    nodes[i].connections.push(j);
                }
            }
        }
    }

    let rotationY = 0;

    const render = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      
      rotationY += 0.003;
      
      // Draw outer subtle glow
      const gradient = ctx.createRadialGradient(centerX, centerY, radius * 0.8, centerX, centerY, radius * 1.5);
      gradient.addColorStop(0, 'rgba(50, 129, 183, 0.15)'); // primary
      gradient.addColorStop(0.5, 'rgba(90, 175, 213, 0.05)'); // accent-1
      gradient.addColorStop(1, 'rgba(242, 252, 252, 0)');
      
      ctx.fillStyle = gradient;
      ctx.beginPath();
      ctx.arc(centerX, centerY, radius * 1.5, 0, Math.PI * 2);
      ctx.fill();

      // Sort nodes by Z index for basic depth sorting
      const projectedNodes = nodes.map((node, index) => {
        // Rotate around Y axis
        const currentTheta = node.theta + rotationY;
        
        // Convert to Cartesian coordinates
        const x3d = radius * Math.sin(node.phi) * Math.cos(currentTheta);
        const y3d = radius * Math.cos(node.phi);
        const z3d = radius * Math.sin(node.phi) * Math.sin(currentTheta);
        
        return {
           x: centerX + x3d,
           y: centerY + y3d,
           z: z3d,
           size: node.size,
           originalIndex: index,
           connections: node.connections
        };
      });
      
      projectedNodes.sort((a, b) => a.z - b.z);
      
      // Draw connections
      ctx.lineWidth = 1.5; // Thicker lines for visibility
      for (const node of projectedNodes) {
          // Only draw lines for front-facing or mid-facing nodes to reduce clutter
          if (node.z > -radius * 0.5) {
              const alphaLine = (node.z + radius) / (radius * 2); // 0 to 1 based on depth
              // Use #3281B7 (primary) for lines to make them contrast well
              ctx.strokeStyle = `rgba(50, 129, 183, ${alphaLine * 0.6})`;
              
              for (const targetIdx of node.connections) {
                  const targetNode = projectedNodes.find(n => n.originalIndex === targetIdx);
                  if (targetNode) {
                      ctx.beginPath();
                      ctx.moveTo(node.x, node.y);
                      ctx.lineTo(targetNode.x, targetNode.y);
                      ctx.stroke();
                  }
              }
          }
      }

      // Draw nodes
      for (const node of projectedNodes) {
        // Calculate opacity based on Z depth
        const depthRatio = (node.z + radius) / (radius * 2); // 0 (back) to 1 (front)
        const alpha = 0.4 + (depthRatio * 0.6); // Base opacity increased
        const currentSize = node.size * (0.8 + depthRatio * 0.7); // Larger nodes
        
        ctx.beginPath();
        ctx.arc(node.x, node.y, currentSize, 0, Math.PI * 2);
        
        if (depthRatio > 0.8) {
            // #67CFC3 (accent-3) for front nodes
            ctx.fillStyle = `rgba(103, 207, 195, ${alpha})`; 
            ctx.shadowBlur = 15; // Stronger glow
            ctx.shadowColor = '#67CFC3';
        } else {
            // #5AAFD5 (accent-1) for back nodes
            ctx.fillStyle = `rgba(90, 175, 213, ${alpha})`;
            ctx.shadowBlur = 0;
        }
        
        ctx.fill();
      }
      
      // Draw subtle latitude/longitude rings
      // Using #3281B7 (primary) for better contrast on light bg
      ctx.strokeStyle = 'rgba(50, 129, 183, 0.25)';
      ctx.lineWidth = 1.5;
      ctx.beginPath();
      ctx.ellipse(centerX, centerY, radius, radius * 0.3, 0, 0, Math.PI * 2);
      ctx.stroke();
      
      ctx.beginPath();
      ctx.ellipse(centerX, centerY, radius * 0.3, radius, 0, 0, Math.PI * 2);
      ctx.stroke();

      animationFrameId = requestAnimationFrame(render);
    };
    
    render();
    
    return () => {
      cancelAnimationFrame(animationFrameId);
    };
  }, []);

  return (
    <div className="relative w-full h-[500px] flex items-center justify-center">
      <canvas 
        ref={canvasRef} 
        className="w-[500px] h-[500px] pointer-events-none"
        style={{ filter: 'drop-shadow(0 0 40px rgba(90,175,213,0.15))' }}
      />
    </div>
  );
}
