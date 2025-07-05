// Dummy graph data based on backend knowledge graph structure
export interface GraphNode {
  id: string
  name: string
  type: 'entity' | 'concept' | 'document' | 'relationship'
  size?: number
  color?: string
  metadata?: Record<string, any>
  x?: number
  y?: number
}

export interface GraphLink {
  source: string
  target: string
  type: string
  strength?: number
}

export interface GraphData {
  nodes: GraphNode[]
  links: GraphLink[]
}

// Generate dummy knowledge graph data with better initial spacing
export const generateDummyGraphData = (): GraphData => {
  // Helper to spread nodes in a circle
  const spreadNodes = (count: number, radius: number, centerX: number, centerY: number) => {
    const positions = []
    for (let i = 0; i < count; i++) {
      const angle = (i / count) * 2 * Math.PI
      positions.push({
        x: centerX + radius * Math.cos(angle),
        y: centerY + radius * Math.sin(angle)
      })
    }
    return positions
  }
  
  const nodes: GraphNode[] = [
    // Core entities - center
    { id: '1', name: 'FastCTX', type: 'entity', size: 12, color: '#6366f1', x: 0, y: 0 },
    { id: '2', name: 'Knowledge Graph', type: 'concept', size: 10, color: '#8b5cf6', x: 150, y: 0 },
    { id: '3', name: 'Neo4j DB', type: 'entity', size: 10, color: '#06b6d4', x: -150, y: 0 },
    { id: '4', name: 'LangChain', type: 'entity', size: 8, color: '#10b981', x: 0, y: -150 },
    { id: '5', name: 'Gemini', type: 'entity', size: 8, color: '#f59e0b', x: 0, y: 150 },
    
    // Documents - outer ring
    { id: '6', name: 'Hello.java', type: 'document', size: 6, color: '#ef4444', x: -250, y: -100 },
    { id: '7', name: 'Main.java', type: 'document', size: 6, color: '#ef4444', x: -250, y: 100 },
    { id: '8', name: 'Utils.java', type: 'document', size: 6, color: '#ef4444', x: -250, y: 0 },
    
    // Concepts - right side
    { id: '9', name: 'Class', type: 'concept', size: 7, color: '#a855f7', x: 250, y: -150 },
    { id: '10', name: 'Method', type: 'concept', size: 7, color: '#a855f7', x: 250, y: -50 },
    { id: '11', name: 'Import', type: 'concept', size: 7, color: '#a855f7', x: 250, y: 50 },
    { id: '12', name: 'Package', type: 'concept', size: 7, color: '#a855f7', x: 250, y: 150 },
    
    // Relationships - scattered
    { id: '13', name: 'Processing', type: 'relationship', size: 5, color: '#64748b', x: -100, y: -200 },
    { id: '14', name: 'Extraction', type: 'relationship', size: 5, color: '#64748b', x: 100, y: -200 },
    { id: '15', name: 'Transform', type: 'relationship', size: 5, color: '#64748b', x: 0, y: 250 },
  ]

  const links: GraphLink[] = [
    // System connections
    { source: '1', target: '2', type: 'contains', strength: 1 },
    { source: '1', target: '3', type: 'uses', strength: 0.8 },
    { source: '1', target: '4', type: 'integrates', strength: 0.8 },
    { source: '1', target: '5', type: 'powered_by', strength: 0.7 },
    
    // Processing flow
    { source: '4', target: '13', type: 'performs', strength: 0.6 },
    { source: '13', target: '6', type: 'processes', strength: 0.5 },
    { source: '13', target: '7', type: 'processes', strength: 0.5 },
    { source: '13', target: '8', type: 'processes', strength: 0.5 },
    
    // Entity extraction
    { source: '5', target: '14', type: 'enables', strength: 0.7 },
    { source: '14', target: '9', type: 'extracts', strength: 0.6 },
    { source: '14', target: '10', type: 'extracts', strength: 0.6 },
    { source: '14', target: '11', type: 'extracts', strength: 0.6 },
    { source: '14', target: '12', type: 'extracts', strength: 0.6 },
    
    // Graph transformation
    { source: '4', target: '15', type: 'performs', strength: 0.7 },
    { source: '15', target: '2', type: 'creates', strength: 0.8 },
    { source: '2', target: '3', type: 'stored_in', strength: 0.9 },
    
    // Document relationships
    { source: '6', target: '9', type: 'contains', strength: 0.5 },
    { source: '6', target: '10', type: 'contains', strength: 0.5 },
    { source: '7', target: '10', type: 'contains', strength: 0.5 },
    { source: '7', target: '11', type: 'contains', strength: 0.5 },
    { source: '8', target: '12', type: 'defines', strength: 0.5 },
  ]

  return { nodes, links }
}

// Get node color based on type
export const getNodeColor = (node: GraphNode): string => {
  return node.color || '#6366f1'
}

// Calculate node size
export const getNodeSize = (node: GraphNode): number => {
  return node.size || 6
}