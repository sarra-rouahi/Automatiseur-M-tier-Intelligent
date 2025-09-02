import { useState, useEffect, useCallback } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import ReactFlow, {
  
  Controls,
  Background,
  BackgroundVariant,
  useNodesState,
  useEdgesState,
  addEdge,
} from 'reactflow'
import 'reactflow/dist/style.css'
import { Button } from '../components/ui/button'
import { Input } from '../components/ui/input'
import { ArrowLeft, Play, Save, Mail, Brain, Eye, Calendar, FileText, Send, GitBranch, Settings } from 'lucide-react'
import axios from 'axios'

// -------------------- TYPES --------------------
interface NodeData {
  id: string
  name: string
  description?: string
  category: string
}

interface AvailableNodes {
  triggers: NodeData[]
  actions: NodeData[]
  conditions: NodeData[]
}

interface CustomNodeProps {
  data: any
  selected: boolean
}

// -------------------- Nœud personnalisé --------------------
const CustomNode = ({ data, selected }: CustomNodeProps) => {
  const getNodeIcon = (name: string) => {
    if (name.includes('Email')) return <Mail className="h-4 w-4" />
    if (name.includes('Classification')) return <Brain className="h-4 w-4" />
    if (name.includes('OCR')) return <Eye className="h-4 w-4" />
    if (name.includes('Calendrier')) return <Calendar className="h-4 w-4" />
    if (name.includes('Résumé')) return <FileText className="h-4 w-4" />
    if (name.includes('Envoyer')) return <Send className="h-4 w-4" />
    if (name.includes('Condition')) return <GitBranch className="h-4 w-4" />
    return <Settings className="h-4 w-4" />
  }

  const getNodeColor = (category: string) => {
    switch (category) {
      case 'api_third_party': return 'bg-blue-100 border-blue-300 text-blue-800'
      case 'ai_capability': return 'bg-purple-100 border-purple-300 text-purple-800'
      case 'utility': return 'bg-gray-100 border-gray-300 text-gray-800'
      default: return 'bg-gray-100 border-gray-300 text-gray-800'
    }
  }

  return (
    <div className={`px-4 py-2 shadow-md rounded-md border-2 ${getNodeColor(data.category)} ${selected ? 'ring-2 ring-blue-500' : ''}`}>
      <div className="flex items-center gap-2">
        {getNodeIcon(data.label)}
        <div className="font-bold text-sm">{data.label}</div>
      </div>
      {data.description && <div className="text-xs mt-1 opacity-75">{data.description}</div>}
    </div>
  )
}

const nodeTypes = { custom: CustomNode }

// -------------------- WorkflowEditor --------------------
export default function WorkflowEditor() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()

  const [nodes, setNodes, onNodesChange] = useNodesState([])
  const [edges, setEdges, onEdgesChange] = useEdgesState([])
  const [selectedNode, setSelectedNode] = useState<any>(null)
  const [availableNodes, setAvailableNodes] = useState<AvailableNodes>({ triggers: [], actions: [], conditions: [] })
  const [workflowName, setWorkflowName] = useState('Nouveau flux')
  const [workflowDescription, setWorkflowDescription] = useState('')
  const [showNodePanel, setShowNodePanel] = useState(true)
  const [saving, setSaving] = useState(false)
  const [executing, setExecuting] = useState(false)

  useEffect(() => {
    loadAvailableNodes()
    if (id && id !== 'new') loadWorkflow(id)
  }, [id])

  const loadAvailableNodes = async () => {
    try {
      const response = await axios.get('/trigemail/') // Trigger Emails
      setAvailableNodes(prev => ({ ...prev, triggers: response.data }))
    } catch (error) {
      console.error('Erreur lors du chargement des nœuds:', error)
    }
  }

  const loadWorkflow = async (workflowId: string) => {
    try {
      const response = await axios.get(`/emails/${workflowId}`)
      const workflow = response.data
      setWorkflowName(workflow.name)
      setWorkflowDescription(workflow.description || '')
      setNodes(workflow.flow_data?.nodes || [])
      setEdges(workflow.flow_data?.edges || [])
    } catch (error) {
      console.error('Erreur lors du chargement du flux:', error)
    }
  }

  const onConnect = useCallback((params: any) => setEdges((eds) => addEdge(params, eds)), [setEdges])
  const onNodeClick = useCallback((_: any, node: any) => setSelectedNode(node), [])

  const addNodeToFlow = (node: NodeData) => {
    const newNode = {
      id: `${node.id}_${Date.now()}`,
      type: 'custom',
      position: { x: Math.random() * 400, y: Math.random() * 400 },
      data: { label: node.name, description: node.description, category: node.category, configuration: {} }
    }
    setNodes(nds => [...nds, newNode])
  }

  const saveWorkflow = async () => {
    setSaving(true)
    try {
      const workflowData = { name: workflowName, description: workflowDescription, flow_data: { nodes, edges } }
      if (id && id !== 'new') await axios.put(`/emails/${id}`, workflowData)
      else {
        const response = await axios.post('/emails/', { ...workflowData, project_id: 1 })
        navigate(`/workflow/${response.data.id}`)
      }
    } catch (error) {
      console.error('Erreur lors de la sauvegarde:', error)
    } finally { setSaving(false) }
  }

  const executeWorkflow = async () => {
    setExecuting(true)
    try {
      if (id && id !== 'new') {
        await axios.post(`/trigemail/${id}/execute`, {})
        alert('Test du flux lancé avec succès !')
      } else alert('Veuillez d\'abord sauvegarder le flux')
    } catch (error) {
      console.error('Erreur lors de l\'exécution:', error)
      alert('Erreur lors du test du flux')
    } finally { setExecuting(false) }
  }

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b px-4 py-3">
        <div className="flex items-center justify-between">
          <Button variant="ghost" size="sm" onClick={() => navigate('/dashboard')}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Retour
          </Button>
          <div className="flex gap-2">
            <Input value={workflowName} onChange={(e) => setWorkflowName(e.target.value)} />
            <Button variant="outline" onClick={saveWorkflow} disabled={saving}>
              <Save className="h-4 w-4 mr-2" />
              {saving ? 'Sauvegarde...' : 'Sauvegarder'}
            </Button>
            <Button onClick={executeWorkflow} disabled={executing}>
              <Play className="h-4 w-4 mr-2" />
              {executing ? 'Test...' : 'Tester'}
            </Button>
          </div>
        </div>
      </header>

      {/* ReactFlow Editor */}
      <div className="flex-1 flex">
        {showNodePanel && (
          <div className="w-80 bg-white border-r overflow-y-auto p-4">
            <h3 className="font-semibold mb-4">Nœuds disponibles</h3>
            {availableNodes.triggers.map(trigger => (
              <div key={trigger.id} className="p-2 border rounded cursor-pointer mb-2 hover:bg-gray-100" onClick={() => addNodeToFlow(trigger)}>
                <span>{trigger.name}</span>
              </div>
            ))}
          </div>
        )}
        <div className="flex-1">
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            onNodeClick={onNodeClick}
            nodeTypes={nodeTypes}
            fitView
          >
            <Controls />
            <Background variant={BackgroundVariant.Dots} gap={12} size={1} />
          </ReactFlow>
        </div>
      </div>
    </div>
  )
}
