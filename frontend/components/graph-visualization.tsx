'use client'

import { useCallback, useEffect, useState } from 'react'
import {
  ReactFlow,
  Node,
  Edge,
  useNodesState,
  useEdgesState,
  Controls,
  Background,
  BackgroundVariant,
  MiniMap,
  Panel,
  NodeTypes,
  Handle,
  Position,
} from '@xyflow/react'
import '@xyflow/react/dist/style.css'
import { motion, AnimatePresence } from 'framer-motion'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Switch } from '@/components/ui/switch'
import { Label } from '@/components/ui/label'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Separator } from '@/components/ui/separator'
import { Input } from '@/components/ui/input'
import { ScrollArea } from '@/components/ui/scroll-area'
import { 
  Network,
  Sparkles,
  Activity,
  GitBranch,
  Database,
  FileCode,
  Brain,
  ZoomIn,
  ZoomOut,
  Maximize2,
  Terminal,
  Play,
  CheckCircle,
  XCircle,
  Loader2
} from 'lucide-react'

const nodeTypeIcons = {
  entity: Database,
  concept: Brain,
  document: FileCode,
  relationship: GitBranch,
}

// Custom node component
function CustomNode({ data }: { data: any }) {
  const Icon = nodeTypeIcons[data.type as keyof typeof nodeTypeIcons]
  
  return (
    <div 
      className="px-4 py-2 shadow-lg rounded-lg border-2 backdrop-blur-sm transition-all duration-200 hover:shadow-xl"
      style={{
        borderColor: data.color,
        backgroundColor: data.color + '20',
      }}
    >
      <Handle type="target" position={Position.Top} className="w-2 h-2" />
      <div className="flex items-center gap-2">
        {Icon && <Icon className="w-4 h-4" style={{ color: data.color }} />}
        <div className="text-xs font-medium text-white">{data.label}</div>
      </div>
      <Handle type="source" position={Position.Bottom} className="w-2 h-2" />
    </div>
  )
}

const nodeTypes: NodeTypes = {
  custom: CustomNode,
}

// Initial nodes
const initialNodes: Node[] = [
  // Core entities
  { id: '1', position: { x: 400, y: 200 }, data: { label: 'FastCTX', type: 'entity', color: '#6366f1' }, type: 'custom' },
  { id: '2', position: { x: 600, y: 200 }, data: { label: 'Knowledge Graph', type: 'concept', color: '#8b5cf6' }, type: 'custom' },
  { id: '3', position: { x: 200, y: 200 }, data: { label: 'Neo4j DB', type: 'entity', color: '#06b6d4' }, type: 'custom' },
  { id: '4', position: { x: 400, y: 50 }, data: { label: 'LangChain', type: 'entity', color: '#10b981' }, type: 'custom' },
  { id: '5', position: { x: 400, y: 350 }, data: { label: 'Gemini', type: 'entity', color: '#f59e0b' }, type: 'custom' },
  
  // Documents
  { id: '6', position: { x: 50, y: 100 }, data: { label: 'Hello.java', type: 'document', color: '#ef4444' }, type: 'custom' },
  { id: '7', position: { x: 50, y: 200 }, data: { label: 'Main.java', type: 'document', color: '#ef4444' }, type: 'custom' },
  { id: '8', position: { x: 50, y: 300 }, data: { label: 'Utils.java', type: 'document', color: '#ef4444' }, type: 'custom' },
  
  // Concepts
  { id: '9', position: { x: 750, y: 50 }, data: { label: 'Class', type: 'concept', color: '#a855f7' }, type: 'custom' },
  { id: '10', position: { x: 750, y: 150 }, data: { label: 'Method', type: 'concept', color: '#a855f7' }, type: 'custom' },
  { id: '11', position: { x: 750, y: 250 }, data: { label: 'Import', type: 'concept', color: '#a855f7' }, type: 'custom' },
  { id: '12', position: { x: 750, y: 350 }, data: { label: 'Package', type: 'concept', color: '#a855f7' }, type: 'custom' },
  
  // Relationships
  { id: '13', position: { x: 200, y: 50 }, data: { label: 'Processing', type: 'relationship', color: '#64748b' }, type: 'custom' },
  { id: '14', position: { x: 600, y: 50 }, data: { label: 'Extraction', type: 'relationship', color: '#64748b' }, type: 'custom' },
  { id: '15', position: { x: 400, y: 450 }, data: { label: 'Transform', type: 'relationship', color: '#64748b' }, type: 'custom' },
]

// Initial edges
const initialEdges: Edge[] = [
  { id: 'e1-2', source: '1', target: '2', animated: true, style: { stroke: '#6366f144' } },
  { id: 'e1-3', source: '1', target: '3', animated: true, style: { stroke: '#06b6d444' } },
  { id: 'e1-4', source: '1', target: '4', animated: true, style: { stroke: '#10b98144' } },
  { id: 'e1-5', source: '1', target: '5', animated: true, style: { stroke: '#f59e0b44' } },
  { id: 'e4-13', source: '4', target: '13', style: { stroke: '#64748b44' } },
  { id: 'e13-6', source: '13', target: '6', style: { stroke: '#ef444444' } },
  { id: 'e13-7', source: '13', target: '7', style: { stroke: '#ef444444' } },
  { id: 'e13-8', source: '13', target: '8', style: { stroke: '#ef444444' } },
  { id: 'e5-14', source: '5', target: '14', style: { stroke: '#64748b44' } },
  { id: 'e14-9', source: '14', target: '9', style: { stroke: '#a855f744' } },
  { id: 'e14-10', source: '14', target: '10', style: { stroke: '#a855f744' } },
  { id: 'e14-11', source: '14', target: '11', style: { stroke: '#a855f744' } },
  { id: 'e14-12', source: '14', target: '12', style: { stroke: '#a855f744' } },
  { id: 'e4-15', source: '4', target: '15', style: { stroke: '#64748b44' } },
  { id: 'e15-2', source: '15', target: '2', style: { stroke: '#8b5cf644' } },
  { id: 'e2-3', source: '2', target: '3', animated: true, style: { stroke: '#06b6d444' } },
  { id: 'e6-9', source: '6', target: '9', style: { stroke: '#a855f744' } },
  { id: 'e6-10', source: '6', target: '10', style: { stroke: '#a855f744' } },
  { id: 'e7-10', source: '7', target: '10', style: { stroke: '#a855f744' } },
  { id: 'e7-11', source: '7', target: '11', style: { stroke: '#a855f744' } },
  { id: 'e8-12', source: '8', target: '12', style: { stroke: '#a855f744' } },
]

interface MCPExecution {
  id: string
  command: string
  tool?: string
  status: 'pending' | 'running' | 'success' | 'error'
  output?: string
  error?: string
  suggestion?: string
  timestamp: Date
  details?: {
    filesAnalyzed?: number
    nodesCreated?: number
    edgesCreated?: number
    matchesFound?: number
    confidence?: number
  }
}

export function GraphVisualization() {
  const [nodes, setNodes, onNodesChange] = useNodesState([])
  const [edges, setEdges, onEdgesChange] = useEdgesState([])
  const [selectedNode, setSelectedNode] = useState<Node | null>(null)
  const [showMiniMap, setShowMiniMap] = useState(true)
  const [mcpExecutions, setMcpExecutions] = useState<MCPExecution[]>([])
  const [mcpCommand, setMcpCommand] = useState('')
  const [isInitializing, setIsInitializing] = useState(false)
  const [initPath, setInitPath] = useState('/helloworld')
  const [nodeDetails, setNodeDetails] = useState<any>(null)
  const [availableTools, setAvailableTools] = useState<any[]>([])
  const [showToolSuggestions, setShowToolSuggestions] = useState(false)
  const [selectedTool, setSelectedTool] = useState<any>(null)
  const [parameterValues, setParameterValues] = useState<Record<string, string>>({})
  
  useEffect(() => {
    fetch('http://localhost:8002/api/mcp/tools')
      .then(res => res.json())
      .then(data => {
        console.log('Fetched MCP tools:', data.tools)
        setAvailableTools(data.tools || [])
      })
      .catch(console.error)
  }, [])

  const onNodeClick = useCallback(async (event: React.MouseEvent, node: Node) => {
    setSelectedNode(node)
    if (node.data.type === 'file' && node.data.content) {
      setNodeDetails(node.data)
    }
  }, [])
  
  const handleCommandChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value
    console.log('Command changed:', value)
    setMcpCommand(value)
    setShowToolSuggestions(value.startsWith('/'))
    console.log('Setting showToolSuggestions to:', value.startsWith('/'))
    
    // Check if a tool is already selected based on the command
    if (value.startsWith('/')) {
      const commandParts = value.split(' ')
      const toolCommand = commandParts[0]
      const tool = availableTools.find(t => t.command === toolCommand)
      
      if (tool && tool !== selectedTool) {
        setSelectedTool(tool)
        // Initialize parameter values for the selected tool
        const newParamValues: Record<string, string> = {}
        tool.params.forEach((param: string) => {
          newParamValues[param] = parameterValues[param] || ''
        })
        setParameterValues(newParamValues)
      } else if (!tool) {
        setSelectedTool(null)
      }
    } else {
      setSelectedTool(null)
      setParameterValues({})
    }
  }
  
  const initializeGraph = async () => {
    if (isInitializing) return
    
    setIsInitializing(true)
    setNodes([])
    setEdges([])
    
    const initExecution: MCPExecution = {
      id: Date.now().toString(),
      command: `initialize "${initPath}"`,
      tool: 'file_scanner',
      status: 'running',
      timestamp: new Date(),
      details: {
        filesAnalyzed: 0,
        nodesCreated: 0,
        edgesCreated: 0
      }
    }
    
    setMcpExecutions(prev => [initExecution, ...prev])
    
    try {
      const response = await fetch('http://localhost:8002/api/mcp/initialize', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ path: initPath })
      })
      
      const data = await response.json()
      
      const colors = ['#8b5cf6', '#06b6d4', '#10b981', '#f59e0b', '#ef4444', '#ec4899']
      const baseX = 400
      const baseY = 300
      
      const nodes: Node[] = data.nodes.map((node: any, index: number) => {
        const angle = (index / data.nodes.length) * 2 * Math.PI
        const distance = node.id === '0' ? 0 : 150 + (index % 3) * 50
        
        return {
          id: node.id,
          position: {
            x: baseX + Math.cos(angle) * distance,
            y: baseY + Math.sin(angle) * distance
          },
          data: {
            label: node.label,
            type: node.type === 'folder' ? 'entity' : 'document',
            color: colors[index % colors.length],
            ...node.data
          },
          type: 'custom'
        }
      })
      
      const edges: Edge[] = data.edges.map((edge: any) => ({
        id: edge.id,
        source: edge.source,
        target: edge.target,
        label: edge.label,
        style: {
          stroke: edge.type === 'imports' ? '#10b981' : edge.type === 'depends' ? '#f59e0b' : '#ffffff',
          strokeWidth: edge.type === 'contains' ? 1 : 2,
          opacity: edge.type === 'contains' ? 0.3 : 0.8
        },
        animated: edge.type !== 'contains',
        type: 'smoothstep'
      }))
      
      setNodes(nodes)
      setEdges(edges)
      
      setMcpExecutions(prev => prev.map(exec => 
        exec.id === initExecution.id
          ? {
              ...exec,
              status: 'success',
              output: `Successfully analyzed ${data.stats.filesAnalyzed} files. Created ${data.stats.nodesCreated} nodes and ${data.stats.edgesCreated} connections.`,
              details: data.stats
            }
          : exec
      ))
    } catch (error) {
      setMcpExecutions(prev => prev.map(exec => 
        exec.id === initExecution.id
          ? {
              ...exec,
              status: 'error',
              error: 'Failed to initialize graph'
            }
          : exec
      ))
    }
    
    setIsInitializing(false)
  }
  
  const executeMCPCommand = async () => {
    if (!mcpCommand.trim()) return
    
    // Validate required parameters
    if (selectedTool && selectedTool.params.length > 0) {
      const requiredParams = ['path', 'file_path', 'query', 'symbol_name']
      const missingRequired = selectedTool.params.filter((param: string) => 
        requiredParams.includes(param) && !parameterValues[param]?.trim()
      )
      
      if (missingRequired.length > 0) {
        const errorExecution: MCPExecution = {
          id: Date.now().toString(),
          command: mcpCommand,
          status: 'error',
          error: `Missing required parameters: ${missingRequired.join(', ')}`,
          timestamp: new Date()
        }
        setMcpExecutions(prev => [errorExecution, ...prev])
        return
      }
    }
    
    // Build the full command with parameters if a tool is selected
    let fullCommand = mcpCommand
    if (selectedTool && selectedTool.params.length > 0) {
      // Build command with parameter values
      const paramArgs = selectedTool.params.map((param: string) => 
        parameterValues[param] || ''
      ).filter(val => val.trim() !== '')
      
      if (paramArgs.length > 0) {
        fullCommand = `${selectedTool.command} ${paramArgs.join(' ')}`
      }
    }
    
    const newExecution: MCPExecution = {
      id: Date.now().toString(),
      command: fullCommand,
      status: 'running',
      timestamp: new Date()
    }
    
    setMcpExecutions(prev => [newExecution, ...prev])
    setMcpCommand('')
    setSelectedTool(null)
    setParameterValues({})
    
    try {
      const response = await fetch('http://localhost:8002/api/mcp/execute', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ command: fullCommand })
      })
      
      const data = await response.json()
      
      setMcpExecutions(prev => prev.map(exec => 
        exec.id === newExecution.id 
          ? { 
              ...exec, 
              tool: data.tool,
              status: data.status,
              output: data.output,
              error: data.error,
              suggestion: data.suggestion,
              details: data.details
            }
          : exec
      ))
    } catch (error) {
      setMcpExecutions(prev => prev.map(exec => 
        exec.id === newExecution.id
          ? {
              ...exec,
              status: 'error',
              error: 'Failed to execute command'
            }
          : exec
      ))
    }
  }
  
  return (
    <div className="relative w-full h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-indigo-950/20 overflow-hidden">
      {/* Animated background elements */}
      <div className="absolute inset-0">
        <motion.div
          className="absolute top-1/4 left-1/4 w-96 h-96 bg-violet-600/10 rounded-full filter blur-[128px]"
          animate={{
            x: [0, 100, 0],
            y: [0, -50, 0],
          }}
          transition={{
            duration: 20,
            repeat: Infinity,
            ease: "easeInOut"
          }}
        />
        <motion.div
          className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-blue-600/10 rounded-full filter blur-[128px]"
          animate={{
            x: [0, -100, 0],
            y: [0, 50, 0],
          }}
          transition={{
            duration: 25,
            repeat: Infinity,
            ease: "easeInOut"
          }}
        />
      </div>
      
      <div className="relative z-10 flex h-full">
        {/* Animated sidebar */}
        <motion.div
          initial={{ x: -400 }}
          animate={{ x: 0 }}
          transition={{ type: "spring", damping: 25, stiffness: 120 }}
          className="w-96 h-full bg-slate-900/60 backdrop-blur-xl border-r border-slate-800/50 overflow-hidden"
        >
          <div className="h-full flex flex-col">
            {/* Header */}
            <div className="p-6">
              <motion.div
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
                className="space-y-4"
              >
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-gradient-to-br from-violet-500 to-indigo-600 rounded-lg">
                    <Network className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <h1 className="text-xl font-bold text-white tracking-tight">FastCTX</h1>
                    <p className="text-xs text-slate-400">Knowledge Graph Explorer</p>
                  </div>
                </div>
                
                {/* Quick Initialize Section */}
                <div className="space-y-2">
                  <div className="flex gap-2">
                    <Input
                      value={initPath}
                      onChange={(e) => setInitPath(e.target.value)}
                      placeholder="Path to analyze..."
                      className="bg-slate-800/50 border-slate-700/50 text-white placeholder:text-slate-500 text-sm flex-1"
                    />
                    <Button
                      onClick={initializeGraph}
                      disabled={isInitializing}
                      size="sm"
                      className="bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-700 hover:to-indigo-700 text-white"
                    >
                      {isInitializing ? (
                        <Loader2 className="w-4 h-4 animate-spin" />
                      ) : (
                        <Network className="w-4 h-4" />
                      )}
                    </Button>
                  </div>
                  {nodes.length === 0 && !isInitializing && (
                    <p className="text-[10px] text-slate-500">Initialize to build knowledge graph</p>
                  )}
                  {isInitializing && (
                    <p className="text-[10px] text-blue-400">Building graph...</p>
                  )}
                </div>
              </motion.div>
            </div>
            
            {/* Main content area */}
            <div className="flex-1 px-6 overflow-y-auto">
              <Tabs defaultValue="info" className="w-full">
                <TabsList className="grid w-full grid-cols-2 bg-slate-800/30 backdrop-blur border border-slate-700/50">
                  <TabsTrigger value="info" className="data-[state=active]:bg-slate-700/50 data-[state=active]:text-white text-slate-300">
                    <Activity className="w-3 h-3 mr-1.5" />
                    Info
                  </TabsTrigger>
                  <TabsTrigger value="controls" className="data-[state=active]:bg-slate-700/50 data-[state=active]:text-white text-slate-300">
                    <Sparkles className="w-3 h-3 mr-1.5" />
                    Controls
                  </TabsTrigger>
                </TabsList>
              
              <AnimatePresence mode="wait" initial={false}>
                <TabsContent value="info" className="space-y-4 mt-4">
                  <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    transition={{ duration: 0.2 }}
                  >
                    {selectedNode ? (
                      <Card className="bg-slate-800/30 backdrop-blur border-slate-700/50 overflow-hidden">
                        <motion.div
                          initial={{ opacity: 0, scale: 0.95 }}
                          animate={{ opacity: 1, scale: 1 }}
                          className="p-4 space-y-3"
                        >
                          <div className="flex items-start justify-between">
                            <div className="flex items-center gap-2">
                              {(() => {
                                const Icon = nodeTypeIcons[selectedNode.data.type as keyof typeof nodeTypeIcons]
                                return Icon ? <Icon className="w-4 h-4 text-slate-400" /> : null
                              })()}
                              <h3 className="text-sm font-semibold text-white">{selectedNode.data.label}</h3>
                            </div>
                            <Badge 
                              variant="secondary" 
                              className="bg-gradient-to-r from-violet-600/20 to-indigo-600/20 text-violet-300 border-violet-500/20 text-xs"
                            >
                              {selectedNode.data.type}
                            </Badge>
                          </div>
                          <Separator className="bg-slate-700/50" />
                          <div className="text-xs text-slate-400 space-y-1">
                            <p>Node ID: <span className="font-mono text-slate-300">{selectedNode.id}</span></p>
                            <p>Type: <span className="text-slate-300">{selectedNode.data.type}</span></p>
                            {selectedNode.data.path && (
                              <p>Path: <span className="font-mono text-slate-300 text-[10px]">{selectedNode.data.path}</span></p>
                            )}
                          </div>
                          {selectedNode.data.content && (
                            <>
                              <Separator className="bg-slate-700/50" />
                              <div className="space-y-2">
                                <h4 className="text-xs font-semibold text-white">Code Preview</h4>
                                <div className="bg-slate-900/50 rounded p-2 overflow-x-auto">
                                  <pre className="text-[10px] text-slate-300 font-mono">{selectedNode.data.content}</pre>
                                </div>
                              </div>
                            </>
                          )}
                          {selectedNode.data.analysis && (
                            <>
                              <Separator className="bg-slate-700/50" />
                              <div className="space-y-2">
                                <h4 className="text-xs font-semibold text-white">Analysis</h4>
                                <div className="text-[10px] text-slate-400 space-y-1">
                                  {selectedNode.data.analysis.type && (
                                    <p>Type: <span className="text-slate-300">{selectedNode.data.analysis.type}</span></p>
                                  )}
                                  {selectedNode.data.analysis.functions && (
                                    <p>Functions: <span className="text-slate-300">{selectedNode.data.analysis.functions.join(', ')}</span></p>
                                  )}
                                  {selectedNode.data.analysis.imports && (
                                    <p>Imports: <span className="text-slate-300">{selectedNode.data.analysis.imports.join(', ')}</span></p>
                                  )}
                                </div>
                              </div>
                            </>
                          )}
                        </motion.div>
                      </Card>
                    ) : (
                      <Card className="bg-slate-800/30 backdrop-blur border-slate-700/50">
                        <div className="p-8 text-center">
                          <div className="w-12 h-12 mx-auto mb-3 rounded-full bg-slate-700/30 flex items-center justify-center">
                            <GitBranch className="w-6 h-6 text-slate-500" />
                          </div>
                          <p className="text-sm text-slate-400">Click on a node to explore</p>
                        </div>
                      </Card>
                    )}
                    
                    <Card className="bg-slate-800/30 backdrop-blur border-slate-700/50">
                      <div className="p-4 space-y-3">
                        <h4 className="text-xs font-semibold text-white uppercase tracking-wider">Statistics</h4>
                        <div className="grid grid-cols-2 gap-3">
                          <div className="space-y-1">
                            <p className="text-2xl font-bold text-white">{nodes.length}</p>
                            <p className="text-xs text-slate-400">Total Nodes</p>
                          </div>
                          <div className="space-y-1">
                            <p className="text-2xl font-bold text-white">{edges.length}</p>
                            <p className="text-xs text-slate-400">Total Links</p>
                          </div>
                        </div>
                      </div>
                    </Card>
                  </motion.div>
                </TabsContent>
                
                <TabsContent value="controls" className="space-y-4 mt-4">
                  <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    transition={{ duration: 0.2 }}
                  >
                    <Card className="bg-slate-800/30 backdrop-blur border-slate-700/50">
                      <div className="p-4 space-y-4">
                        <div className="flex items-center justify-between">
                          <Label className="text-xs font-medium text-slate-300">Show Mini Map</Label>
                          <Switch
                            checked={showMiniMap}
                            onCheckedChange={setShowMiniMap}
                          />
                        </div>
                      </div>
                    </Card>
                    
                    <Card className="bg-slate-800/30 backdrop-blur border-slate-700/50">
                      <div className="p-4 space-y-4">
                        <div className="space-y-2">
                          <Label className="text-xs font-medium text-slate-300">Initialize Graph</Label>
                          <p className="text-xs text-slate-500">Build knowledge graph from codebase</p>
                        </div>
                        <div className="space-y-2">
                          <Input
                            value={initPath}
                            onChange={(e) => setInitPath(e.target.value)}
                            placeholder="Enter path to analyze..."
                            className="bg-slate-800/50 border-slate-700/50 text-white placeholder:text-slate-500 text-sm"
                          />
                          <Button
                            onClick={initializeGraph}
                            disabled={isInitializing}
                            className="w-full bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-700 hover:to-indigo-700 text-white"
                          >
                            {isInitializing ? (
                              <>
                                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                                Initializing...
                              </>
                            ) : (
                              <>
                                <Network className="w-4 h-4 mr-2" />
                                Initialize
                              </>
                            )}
                          </Button>
                        </div>
                      </div>
                    </Card>
                  </motion.div>
                </TabsContent>
              </AnimatePresence>
              </Tabs>
            </div>
            
          {/* MCP Executor at bottom */}
          <div className="p-6 border-t border-slate-700/50 bg-slate-900/80">
            <div className="space-y-3">
              <div className="flex items-center gap-2 mb-2">
                <Terminal className="w-4 h-4 text-slate-400" />
                <h3 className="text-sm font-semibold text-white">MCP Executor</h3>
                <span className="text-xs text-slate-500">
                  ({availableTools.length} tools available)
                </span>
              </div>
              
              {/* Command input */}
              <div className="relative">
                <div className="flex gap-2">
                  <Input
                    value={mcpCommand}
                    onChange={handleCommandChange}
                    onKeyPress={(e) => e.key === 'Enter' && executeMCPCommand()}
                    placeholder="Enter command or type / for tools..."
                    className="bg-slate-800/50 border-slate-700/50 text-white placeholder:text-slate-500 font-mono text-sm"
                  />
                  <Button
                    onClick={executeMCPCommand}
                    size="icon"
                    className="bg-slate-800/50 hover:bg-slate-700/50 border border-slate-700/50"
                  >
                    <Play className="w-4 h-4" />
                  </Button>
                </div>
                
                {/* Tool suggestions dropdown */}
                {showToolSuggestions && mcpCommand.startsWith('/') && (
                  <div className="absolute bottom-full left-0 right-0 mb-2 max-h-48 overflow-y-auto bg-slate-800 border border-slate-700 rounded-lg shadow-lg">
                    {(() => {
                      const filteredTools = availableTools.filter(tool => tool.command.toLowerCase().includes(mcpCommand.toLowerCase()))
                      console.log('Available tools:', availableTools)
                      console.log('MCP command:', mcpCommand)
                      console.log('Filtered tools:', filteredTools)
                      console.log('showToolSuggestions:', showToolSuggestions)
                      return filteredTools.map((tool, index) => (
                        <button
                          key={index}
                          onClick={() => {
                            setMcpCommand(tool.command + ' ')
                            setShowToolSuggestions(false)
                            setSelectedTool(tool)
                            // Initialize parameter values
                            const newParamValues: Record<string, string> = {}
                            tool.params.forEach((param: string) => {
                              newParamValues[param] = ''
                            })
                            setParameterValues(newParamValues)
                          }}
                          className="w-full px-3 py-2 text-left hover:bg-slate-700/50 transition-colors"
                        >
                          <div className="flex items-center justify-between">
                            <span className="text-sm font-mono text-violet-400">{tool.command}</span>
                            <span className="text-xs text-slate-500">{tool.params.join(', ')}</span>
                          </div>
                          <p className="text-xs text-slate-400 mt-0.5">{tool.description}</p>
                        </button>
                      ))
                    })()}
                    {mcpCommand === '/' && (
                      <div className="px-3 py-2 text-xs text-slate-500 border-t border-slate-700">
                        Type to filter tools or use natural language
                      </div>
                    )}
                  </div>
                )}
              </div>
              
              {/* Parameter inputs */}
              {selectedTool && selectedTool.params.length > 0 && (
                <div className="mt-3 p-3 bg-slate-800/30 border border-slate-700/50 rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-semibold text-violet-400">{selectedTool.command}</span>
                      <span className="text-xs text-slate-500">Parameters</span>
                    </div>
                    <button
                      onClick={() => {
                        setSelectedTool(null)
                        setParameterValues({})
                        setMcpCommand('')
                      }}
                      className="text-xs text-slate-500 hover:text-slate-300 transition-colors"
                    >
                      Clear
                    </button>
                  </div>
                  <div className="space-y-2">
                    {selectedTool.params.map((param: string) => {
                      const isRequired = ['path', 'file_path', 'query', 'symbol_name'].includes(param)
                      const hasValue = parameterValues[param]?.trim() !== ''
                      
                      return (
                        <div key={param} className="flex items-center gap-2">
                          <label className="text-xs text-slate-400 min-w-[80px] flex items-center gap-1">
                            {param}
                            {isRequired && <span className="text-red-400">*</span>}:
                          </label>
                          <Input
                            value={parameterValues[param] || ''}
                            onChange={(e) => {
                              setParameterValues(prev => ({
                                ...prev,
                                [param]: e.target.value
                              }))
                            }}
                            onKeyPress={(e) => e.key === 'Enter' && executeMCPCommand()}
                            placeholder={`Enter ${param}...`}
                            className={`flex-1 h-8 bg-slate-900/50 border-slate-700/50 text-white placeholder:text-slate-600 text-xs ${
                              isRequired && !hasValue ? 'border-red-900/50' : ''
                            }`}
                          />
                        </div>
                      )
                    })}
                  </div>
                  <div className="mt-2 text-xs text-slate-500">
                    Press Enter to execute or click the play button
                  </div>
                </div>
              )}
              
              {/* Execution history */}
              <div className="space-y-2 max-h-48 overflow-y-auto">
                {mcpExecutions.map((execution) => (
                  <div
                    key={execution.id}
                    className="px-3 py-2 bg-slate-800/30 rounded border border-slate-700/50"
                  >
                    <div className="flex items-start gap-2">
                      {execution.status === 'running' && (
                        <Loader2 className="w-3 h-3 text-blue-400 animate-spin mt-0.5" />
                      )}
                      {execution.status === 'success' && (
                        <CheckCircle className="w-3 h-3 text-green-400 mt-0.5" />
                      )}
                      {execution.status === 'error' && (
                        <XCircle className="w-3 h-3 text-red-400 mt-0.5" />
                      )}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <p className="text-xs font-mono text-slate-300 truncate">{execution.command}</p>
                          {execution.tool && (
                            <Badge variant="outline" className="text-[10px] bg-slate-700/30 border-slate-600/50 text-slate-400">
                              {execution.tool}
                            </Badge>
                          )}
                        </div>
                        {execution.output && (
                          <p className="text-xs text-green-400 mt-1 whitespace-pre-wrap">{execution.output}</p>
                        )}
                        {execution.error && (
                          <p className="text-xs text-red-400 mt-1">{execution.error}</p>
                        )}
                        {!execution.tool && execution.status === 'error' && (
                          <p className="text-xs text-yellow-400 mt-1">💡 {execution.suggestion || "Try using '/' to see available tools"}</p>
                        )}
                        {execution.details && (
                          <div className="flex gap-3 mt-1">
                            {execution.details.filesAnalyzed !== undefined && (
                              <span className="text-[10px] text-slate-500">📄 {execution.details.filesAnalyzed}</span>
                            )}
                            {execution.details.nodesCreated !== undefined && (
                              <span className="text-[10px] text-slate-500">🔵 {execution.details.nodesCreated}</span>
                            )}
                            {execution.details.edgesCreated !== undefined && (
                              <span className="text-[10px] text-slate-500">🔗 {execution.details.edgesCreated}</span>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
          </div>
        </motion.div>
        
        {/* Graph container */}
        <div className="flex-1 relative">
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onNodeClick={onNodeClick}
            nodeTypes={nodeTypes}
            fitView
            attributionPosition="bottom-left"
            className="bg-transparent"
            defaultEdgeOptions={{
              style: {
                stroke: '#ffffff',
                strokeWidth: 1.5
              },
              type: 'smoothstep'
            }}
          >
            <Background 
              variant={BackgroundVariant.Dots} 
              gap={20} 
              size={1} 
              color="#1e293b"
            />
            <Controls 
              className="bg-slate-800/60 backdrop-blur-xl border-slate-700/50 shadow-lg"
              showZoom
              showFitView
              showInteractive
            />
            {showMiniMap && (
              <MiniMap 
                className="bg-slate-800/60 backdrop-blur-xl border-slate-700/50 shadow-lg"
                nodeColor={(node) => node.data.color || '#6366f1'}
                maskColor="rgb(15, 23, 42, 0.7)"
              />
            )}
          </ReactFlow>
        </div>
      </div>
    </div>
  )
}