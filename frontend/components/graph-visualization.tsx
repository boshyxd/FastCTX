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
  status: 'pending' | 'running' | 'success' | 'error'
  output?: string
  error?: string
  timestamp: Date
}

export function GraphVisualization() {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes)
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges)
  const [selectedNode, setSelectedNode] = useState<Node | null>(null)
  const [showMiniMap, setShowMiniMap] = useState(true)
  const [mcpExecutions, setMcpExecutions] = useState<MCPExecution[]>([])
  const [mcpCommand, setMcpCommand] = useState('')
  
  const onNodeClick = useCallback((event: React.MouseEvent, node: Node) => {
    setSelectedNode(node)
  }, [])
  
  const executeMCPCommand = () => {
    if (!mcpCommand.trim()) return
    
    // Add new execution
    const newExecution: MCPExecution = {
      id: Date.now().toString(),
      command: mcpCommand,
      status: 'running',
      timestamp: new Date()
    }
    
    setMcpExecutions(prev => [newExecution, ...prev])
    setMcpCommand('')
    
    // Simulate MCP execution (will be replaced with actual MCP agent call)
    setTimeout(() => {
      setMcpExecutions(prev => prev.map(exec => 
        exec.id === newExecution.id 
          ? { 
              ...exec, 
              status: Math.random() > 0.3 ? 'success' : 'error',
              output: Math.random() > 0.3 ? 'Command executed successfully. Graph updated.' : undefined,
              error: Math.random() > 0.3 ? undefined : 'Failed to execute command: Connection timeout'
            }
          : exec
      ))
    }, 2000)
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
          initial={{ x: -320 }}
          animate={{ x: 0 }}
          transition={{ type: "spring", damping: 25, stiffness: 120 }}
          className="w-80 h-full bg-slate-900/60 backdrop-blur-xl border-r border-slate-800/50 overflow-hidden"
        >
          <div className="h-full flex flex-col">
            {/* Header */}
            <div className="p-6">
              <motion.div
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
                className="flex items-center gap-3 mb-6"
              >
                <div className="p-2 bg-gradient-to-br from-violet-500 to-indigo-600 rounded-lg">
                  <Network className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h1 className="text-xl font-bold text-white tracking-tight">FastCTX</h1>
                  <p className="text-xs text-slate-400">Knowledge Graph Explorer</p>
                </div>
              </motion.div>
            </div>
            
            {/* Main content area */}
            <div className="flex-1 px-6 overflow-y-auto">
              <Tabs defaultValue="info" className="w-full">
                <TabsList className="grid w-full grid-cols-2 bg-slate-800/30 backdrop-blur">
                  <TabsTrigger value="info" className="data-[state=active]:bg-slate-700/50">
                    <Activity className="w-3 h-3 mr-1.5" />
                    Info
                  </TabsTrigger>
                  <TabsTrigger value="controls" className="data-[state=active]:bg-slate-700/50">
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
                          </div>
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
              </div>
              
              {/* Command input */}
              <div className="flex gap-2">
                <Input
                  value={mcpCommand}
                  onChange={(e) => setMcpCommand(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && executeMCPCommand()}
                  placeholder="Enter MCP command..."
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
              
              {/* Execution history */}
              <div className="space-y-2 max-h-32 overflow-y-auto">
                {mcpExecutions.slice(0, 3).map((execution) => (
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
                        <p className="text-xs font-mono text-slate-300 truncate">{execution.command}</p>
                        {execution.output && (
                          <p className="text-xs text-green-400 mt-1">{execution.output}</p>
                        )}
                        {execution.error && (
                          <p className="text-xs text-red-400 mt-1">{execution.error}</p>
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
          >
            <Background 
              variant={BackgroundVariant.Dots} 
              gap={20} 
              size={1} 
              color="#334155"
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