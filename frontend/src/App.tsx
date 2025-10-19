import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Link, useParams, useNavigate } from 'react-router-dom'
import { Bell, Home, FileText, Database, Brain, Download, Activity, Heart, Menu, X, UserPlus, CheckCircle2, Shield } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger, DialogFooter } from '@/components/ui/dialog'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Checkbox } from '@/components/ui/checkbox'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

interface Project {
  projectId: string
  name: string
  piName: string
  piEmail: string
  fabricWorkspaceUrl?: string
  mlWorkspaceUrl?: string
  status: string
  createdAt: string
  description: string
  stats?: {
    notebooks: number
    datasets: number
    models: number
    recentActivity: number
  }
}

interface Notebook {
  notebookId: string
  name: string
  language: string
  author: string
  modified: string
  status: string
  fabricUrl: string
}

interface Dataset {
  datasetId: string
  name: string
  rows: number
  size: string
  tables: number
  security: string
  accessLevel: string
}

interface Model {
  modelId: string
  name: string
  version: string
  framework: string
  status: string
  gpus: number
  latency: string
  accuracy: number
  mlStudioUrl: string
}

interface ExportRequest {
  requestId: string
  requestNumber: string
  projectId: string
  requestorEmail: string
  datasetName: string
  rowCount?: number
  justification: string
  status: string
  piReviewerEmail: string
  requestedAt: string
  reviewedAt?: string
  reviewNotes?: string
  downloadUrl?: string
  downloadExpiresAt?: string
}

interface Notification {
  notificationId: string
  userId: string
  type: string
  message: string
  isRead: boolean
  relatedEntityType?: string
  relatedEntityId?: string
  createdAt: string
}

interface ActivityItem {
  activityId: string
  activityType: string
  user: string
  timestamp: string
  details: string
}

function Sidebar({ isOpen, onClose }: { isOpen: boolean; onClose: () => void }) {
  const [unreadCount, setUnreadCount] = useState(0)

  useEffect(() => {
    fetch(`${API_URL}/api/v1/notifications`)
      .then(res => res.json())
      .then(data => {
        setUnreadCount(data.filter((n: Notification) => !n.isRead).length)
      })
  }, [])

  return (
    <>
      {isOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden" onClick={onClose} />
      )}
      <aside className={`fixed lg:static inset-y-0 left-0 z-50 w-64 bg-gray-900 border-r border-gray-800 transform transition-transform duration-200 ease-in-out ${isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}`}>
        <div className="flex flex-col h-full">
          <div className="p-6 border-b border-gray-800">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Heart className="w-8 h-8 text-red-500" />
                <div>
                  <h1 className="text-xl font-bold text-white">AdventHealth</h1>
                  <p className="text-xs text-gray-400">Research Platform</p>
                </div>
              </div>
              <button onClick={onClose} className="lg:hidden text-gray-400 hover:text-white">
                <X className="w-6 h-6" />
              </button>
            </div>
          </div>
          
          <nav className="flex-1 p-4 space-y-2">
            <Link to="/" className="flex items-center gap-3 px-4 py-3 text-gray-300 hover:bg-gray-800 rounded-lg transition-colors">
              <Home className="w-5 h-5" />
              <span>Dashboard</span>
            </Link>
            <Link to="/exports" className="flex items-center gap-3 px-4 py-3 text-gray-300 hover:bg-gray-800 rounded-lg transition-colors">
              <Download className="w-5 h-5" />
              <span>Export Requests</span>
            </Link>
            <Link to="/notifications" className="flex items-center gap-3 px-4 py-3 text-gray-300 hover:bg-gray-800 rounded-lg transition-colors">
              <Bell className="w-5 h-5" />
              <span className="flex-1">Notifications</span>
              {unreadCount > 0 && (
                <Badge className="bg-red-500">{unreadCount}</Badge>
              )}
            </Link>
            <div className="pt-4 border-t border-gray-800">
              <Link to="/request-access" className="flex items-center gap-3 px-4 py-3 text-green-400 hover:bg-gray-800 rounded-lg transition-colors">
                <UserPlus className="w-5 h-5" />
                <span>Request Access</span>
              </Link>
            </div>
          </nav>

          <div className="p-4 border-t border-gray-800">
            <div className="text-sm text-gray-400">
              <p className="font-medium text-white">Dr. Sarah Smith</p>
              <p className="text-xs">dr.smith@adventhealth.com</p>
              <p className="text-xs mt-1">AdventHealth Orlando</p>
            </div>
          </div>
        </div>
      </aside>
    </>
  )
}

function Dashboard() {
  const [projects, setProjects] = useState<Project[]>([])
  const navigate = useNavigate()

  useEffect(() => {
    fetch(`${API_URL}/api/v1/user/projects`)
      .then(res => res.json())
      .then(data => setProjects(data))
  }, [])

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold text-white mb-2">Research Projects</h2>
        <p className="text-gray-400">Cardiovascular research studies and analysis</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {projects.map(project => (
          <Card key={project.projectId} className="bg-gray-800 border-gray-700 hover:border-gray-600 transition-colors cursor-pointer" onClick={() => navigate(`/project/${project.projectId}`)}>
            <CardHeader>
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <CardTitle className="text-white text-xl mb-2">{project.name}</CardTitle>
                  <CardDescription className="text-gray-400">{project.description}</CardDescription>
                </div>
                <Badge className={project.status === 'Active' ? 'bg-green-500' : 'bg-gray-500'}>
                  {project.status}
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex items-center gap-2 text-sm text-gray-400">
                  <span className="font-medium text-white">PI:</span>
                  <span>{project.piName}</span>
                </div>
                
                {project.stats && (
                  <div className="grid grid-cols-4 gap-4 pt-3 border-t border-gray-700">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-blue-400">{project.stats.notebooks}</div>
                      <div className="text-xs text-gray-500">Notebooks</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-green-400">{project.stats.datasets}</div>
                      <div className="text-xs text-gray-500">Datasets</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-purple-400">{project.stats.models}</div>
                      <div className="text-xs text-gray-500">Models</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-orange-400">{project.stats.recentActivity}</div>
                      <div className="text-xs text-gray-500">Activity</div>
                    </div>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}

function ProjectDetails() {
  const { projectId } = useParams()
  const [project, setProject] = useState<any>(null)
  const [notebooks, setNotebooks] = useState<Notebook[]>([])
  const [datasets, setDatasets] = useState<Dataset[]>([])
  const [models, setModels] = useState<Model[]>([])
  const [activities, setActivities] = useState<ActivityItem[]>([])
  const [showExportDialog, setShowExportDialog] = useState(false)
  const [selectedDataset, setSelectedDataset] = useState('')
  const [exportJustification, setExportJustification] = useState('')
  const [exportRowCount, setExportRowCount] = useState('')
  const [showInferenceDialog, setShowInferenceDialog] = useState(false)
  const [inferenceResult, setInferenceResult] = useState<any>(null)
  const [runningInference, setRunningInference] = useState(false)

  useEffect(() => {
    if (projectId) {
      fetch(`${API_URL}/api/v1/projects/${projectId}`)
        .then(res => res.json())
        .then(data => {
          setProject(data)
          setNotebooks(data.notebooks || [])
          setDatasets(data.datasets || [])
          setModels(data.models || [])
        })
      
      fetch(`${API_URL}/api/v1/projects/${projectId}/activity`)
        .then(res => res.json())
        .then(data => setActivities(data))
    }
  }, [projectId])

  const handleExportRequest = async () => {
    const response = await fetch(`${API_URL}/api/v1/exports/request`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        projectId,
        datasetName: selectedDataset,
        rowCount: exportRowCount ? parseInt(exportRowCount) : null,
        justification: exportJustification
      })
    })
    
    if (response.ok) {
      setShowExportDialog(false)
      setSelectedDataset('')
      setExportJustification('')
      setExportRowCount('')
      alert('Export request submitted successfully!')
    }
  }

  const handleRunInference = async (notebookId: string) => {
    setRunningInference(true)
    setShowInferenceDialog(true)
    setInferenceResult(null)
    
    try {
      const response = await fetch(`${API_URL}/api/v1/notebooks/${notebookId}/run-inference`, {
        method: 'POST'
      })
      const data = await response.json()
      setInferenceResult(data)
    } catch (error) {
      console.error('Inference failed:', error)
    } finally {
      setRunningInference(false)
    }
  }

  if (!project) return <div className="text-white">Loading...</div>

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold text-white mb-2">{project.name}</h2>
        <p className="text-gray-400">{project.description}</p>
        <div className="flex items-center gap-4 mt-4">
          <Badge className="bg-green-500">{project.status}</Badge>
          <span className="text-sm text-gray-400">PI: {project.piName}</span>
        </div>
      </div>

      <Tabs defaultValue="notebooks" className="w-full">
        <TabsList className="bg-gray-800 border-gray-700">
          <TabsTrigger value="notebooks" className="data-[state=active]:bg-gray-700">
            <FileText className="w-4 h-4 mr-2" />
            Notebooks ({notebooks.length})
          </TabsTrigger>
          <TabsTrigger value="datasets" className="data-[state=active]:bg-gray-700">
            <Database className="w-4 h-4 mr-2" />
            Datasets ({datasets.length})
          </TabsTrigger>
          <TabsTrigger value="models" className="data-[state=active]:bg-gray-700">
            <Brain className="w-4 h-4 mr-2" />
            Models ({models.length})
          </TabsTrigger>
          <TabsTrigger value="activity" className="data-[state=active]:bg-gray-700">
            <Activity className="w-4 h-4 mr-2" />
            Activity
          </TabsTrigger>
        </TabsList>

        <TabsContent value="notebooks" className="space-y-4">
          {notebooks.map(notebook => (
            <Card key={notebook.notebookId} className="bg-gray-800 border-gray-700">
              <CardContent className="p-6">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-white mb-2">{notebook.name}</h3>
                    <div className="flex items-center gap-4 text-sm text-gray-400">
                      <span>Language: {notebook.language}</span>
                      <span>Author: {notebook.author}</span>
                      <span>Modified: {new Date(notebook.modified).toLocaleDateString()}</span>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge className={notebook.status === 'Running' ? 'bg-blue-500' : 'bg-gray-600'}>
                      {notebook.status}
                    </Badge>
                    {notebook.name.includes('Inference') && (
                      <Button 
                        size="sm" 
                        className="bg-green-600 hover:bg-green-700"
                        onClick={() => handleRunInference(notebook.notebookId)}
                      >
                        Run Inference
                      </Button>
                    )}
                    <Button size="sm" className="bg-blue-600 hover:bg-blue-700">
                      Open
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </TabsContent>

        <TabsContent value="datasets" className="space-y-4">
          <div className="flex justify-end mb-4">
            <Dialog open={showExportDialog} onOpenChange={setShowExportDialog}>
              <DialogTrigger asChild>
                <Button className="bg-green-600 hover:bg-green-700">
                  <Download className="w-4 h-4 mr-2" />
                  Request Export
                </Button>
              </DialogTrigger>
              <DialogContent className="bg-gray-800 border-gray-700 text-white">
                <DialogHeader>
                  <DialogTitle>Request Data Export</DialogTitle>
                  <DialogDescription className="text-gray-400">
                    Submit a request to export data. The PI will review and approve.
                  </DialogDescription>
                </DialogHeader>
                <div className="space-y-4">
                  <div>
                    <Label htmlFor="dataset">Dataset</Label>
                    <Select value={selectedDataset} onValueChange={setSelectedDataset}>
                      <SelectTrigger className="bg-gray-900 border-gray-700">
                        <SelectValue placeholder="Select dataset" />
                      </SelectTrigger>
                      <SelectContent className="bg-gray-900 border-gray-700">
                        {datasets.map(ds => (
                          <SelectItem key={ds.datasetId} value={ds.name}>{ds.name}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label htmlFor="rowCount">Number of Rows (optional)</Label>
                    <Input
                      id="rowCount"
                      type="number"
                      value={exportRowCount}
                      onChange={(e) => setExportRowCount(e.target.value)}
                      className="bg-gray-900 border-gray-700"
                      placeholder="Leave empty for full dataset"
                    />
                  </div>
                  <div>
                    <Label htmlFor="justification">Justification</Label>
                    <Textarea
                      id="justification"
                      value={exportJustification}
                      onChange={(e) => setExportJustification(e.target.value)}
                      className="bg-gray-900 border-gray-700"
                      placeholder="Explain why you need to export this data..."
                      rows={4}
                    />
                  </div>
                </div>
                <DialogFooter>
                  <Button variant="outline" onClick={() => setShowExportDialog(false)} className="border-gray-700">
                    Cancel
                  </Button>
                  <Button onClick={handleExportRequest} className="bg-green-600 hover:bg-green-700">
                    Submit Request
                  </Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          </div>
          
          {datasets.map(dataset => (
            <Card key={dataset.datasetId} className="bg-gray-800 border-gray-700">
              <CardContent className="p-6">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-white mb-2">{dataset.name}</h3>
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="text-gray-400">Rows:</span>
                        <span className="text-white ml-2">{dataset.rows.toLocaleString()}</span>
                      </div>
                      <div>
                        <span className="text-gray-400">Size:</span>
                        <span className="text-white ml-2">{dataset.size}</span>
                      </div>
                      <div>
                        <span className="text-gray-400">Tables:</span>
                        <span className="text-white ml-2">{dataset.tables}</span>
                      </div>
                      <div>
                        <span className="text-gray-400">Access:</span>
                        <span className="text-white ml-2">{dataset.accessLevel}</span>
                      </div>
                    </div>
                  </div>
                  <Badge className="bg-red-500">{dataset.security}</Badge>
                </div>
              </CardContent>
            </Card>
          ))}
        </TabsContent>

        <Dialog open={showInferenceDialog} onOpenChange={setShowInferenceDialog}>
          <DialogContent className="bg-gray-800 border-gray-700 text-white max-w-4xl">
            <DialogHeader>
              <DialogTitle>Inference Results - H100 GPU</DialogTitle>
              <DialogDescription className="text-gray-400">
                Real-time ECG arrhythmia detection inference
              </DialogDescription>
            </DialogHeader>
            {runningInference ? (
              <div className="py-12 text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-500 mx-auto mb-4"></div>
                <p className="text-gray-400">Running inference on H100 GPU...</p>
              </div>
            ) : inferenceResult ? (
              <div className="space-y-4">
                <Alert className="bg-green-900 border-green-700">
                  <CheckCircle2 className="w-4 h-4" />
                  <AlertDescription className="text-green-200">
                    <strong>Inference Complete!</strong> Latency: {inferenceResult.result.inference_time_ms}ms (Target: &lt;50ms)
                  </AlertDescription>
                </Alert>
                
                <Card className="bg-gray-900 border-gray-700">
                  <CardHeader>
                    <CardTitle className="text-white text-sm">Console Output</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <pre className="text-xs text-gray-300 font-mono whitespace-pre-wrap bg-black p-4 rounded">
                      {inferenceResult.output}
                    </pre>
                  </CardContent>
                </Card>

                <div className="grid grid-cols-2 gap-4">
                  <Card className="bg-gray-900 border-gray-700">
                    <CardHeader>
                      <CardTitle className="text-white text-sm">Model Details</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-400">Model:</span>
                        <span className="text-white">{inferenceResult.result.model}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-400">GPU:</span>
                        <span className="text-white">{inferenceResult.result.gpu_used}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-400">Latency:</span>
                        <span className="text-green-400">{inferenceResult.result.inference_time_ms}ms</span>
                      </div>
                    </CardContent>
                  </Card>

                  <Card className="bg-gray-900 border-gray-700">
                    <CardHeader>
                      <CardTitle className="text-white text-sm">Prediction</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-400">Class:</span>
                        <span className="text-white font-semibold">{inferenceResult.result.predicted_class.replace('_', ' ').toUpperCase()}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-400">Confidence:</span>
                        <span className="text-green-400">{(inferenceResult.result.confidence * 100).toFixed(1)}%</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-400">Timestamp:</span>
                        <span className="text-white text-xs">{new Date(inferenceResult.result.timestamp).toLocaleTimeString()}</span>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </div>
            ) : null}
            <DialogFooter>
              <Button onClick={() => setShowInferenceDialog(false)} className="bg-gray-700 hover:bg-gray-600">
                Close
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>

        <TabsContent value="models" className="space-y-4">
          {models.map(model => (
            <Card key={model.modelId} className="bg-gray-800 border-gray-700">
              <CardContent className="p-6">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-white mb-2">{model.name}</h3>
                    <div className="grid grid-cols-3 gap-4 text-sm">
                      <div>
                        <span className="text-gray-400">Version:</span>
                        <span className="text-white ml-2">{model.version}</span>
                      </div>
                      <div>
                        <span className="text-gray-400">Framework:</span>
                        <span className="text-white ml-2">{model.framework}</span>
                      </div>
                      <div>
                        <span className="text-gray-400">GPUs:</span>
                        <span className="text-white ml-2">{model.gpus}</span>
                      </div>
                      <div>
                        <span className="text-gray-400">Latency:</span>
                        <span className="text-white ml-2">{model.latency}</span>
                      </div>
                      <div>
                        <span className="text-gray-400">Accuracy:</span>
                        <span className="text-white ml-2">{(model.accuracy * 100).toFixed(1)}%</span>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge className={model.status === 'Deployed' ? 'bg-green-500' : model.status === 'Training' ? 'bg-blue-500' : 'bg-gray-600'}>
                      {model.status}
                    </Badge>
                    <Button size="sm" className="bg-purple-600 hover:bg-purple-700">
                      View
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </TabsContent>

        <TabsContent value="activity" className="space-y-4">
          {activities.map(activity => (
            <Card key={activity.activityId} className="bg-gray-800 border-gray-700">
              <CardContent className="p-4">
                <div className="flex items-start gap-4">
                  <div className="w-2 h-2 bg-blue-500 rounded-full mt-2"></div>
                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-medium text-white">{activity.activityType}</span>
                      <span className="text-sm text-gray-400">{new Date(activity.timestamp).toLocaleString()}</span>
                    </div>
                    <p className="text-sm text-gray-400">{activity.details}</p>
                    <p className="text-xs text-gray-500 mt-1">by {activity.user}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </TabsContent>
      </Tabs>
    </div>
  )
}

function ExportRequests() {
  const [requests, setRequests] = useState<ExportRequest[]>([])

  useEffect(() => {
    fetch(`${API_URL}/api/v1/exports/my-requests`)
      .then(res => res.json())
      .then(data => setRequests(data))
  }, [])

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold text-white mb-2">Export Requests</h2>
        <p className="text-gray-400">Track your data export requests</p>
      </div>

      <div className="space-y-4">
        {requests.map(request => (
          <Card key={request.requestId} className="bg-gray-800 border-gray-700">
            <CardContent className="p-6">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h3 className="text-lg font-semibold text-white mb-1">{request.requestNumber}</h3>
                  <p className="text-gray-400">{request.datasetName}</p>
                </div>
                <Badge className={
                  request.status === 'Approved' ? 'bg-green-500' :
                  request.status === 'Pending' ? 'bg-yellow-500' :
                  request.status === 'Rejected' ? 'bg-red-500' : 'bg-gray-500'
                }>
                  {request.status}
                </Badge>
              </div>
              
              <div className="space-y-2 text-sm">
                <div className="flex items-center gap-2">
                  <span className="text-gray-400">Rows:</span>
                  <span className="text-white">{request.rowCount?.toLocaleString() || 'Full dataset'}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-gray-400">Requested:</span>
                  <span className="text-white">{new Date(request.requestedAt).toLocaleString()}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-gray-400">Reviewer:</span>
                  <span className="text-white">{request.piReviewerEmail}</span>
                </div>
                <div>
                  <span className="text-gray-400">Justification:</span>
                  <p className="text-white mt-1">{request.justification}</p>
                </div>
                
                {request.reviewNotes && (
                  <Alert className="bg-gray-900 border-gray-700 mt-4">
                    <AlertDescription className="text-gray-300">
                      <strong>Review Notes:</strong> {request.reviewNotes}
                    </AlertDescription>
                  </Alert>
                )}
                
                {request.downloadUrl && (
                  <div className="mt-4">
                    <Button className="bg-green-600 hover:bg-green-700">
                      <Download className="w-4 h-4 mr-2" />
                      Download (Expires: {new Date(request.downloadExpiresAt!).toLocaleString()})
                    </Button>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}

function ExternalAccessRequest() {
  const navigate = useNavigate()
  const [formData, setFormData] = useState({
    fullName: '',
    email: '',
    institution: '',
    position: '',
    projectInterest: '',
    researchPurpose: '',
    dataNeeded: '',
    hipaaTraining: false,
    irbApproval: false,
    dataSecurityAgreement: false,
    noExternalSharing: false,
    institutionalAgreement: false
  })
  const [submitted, setSubmitted] = useState(false)

  const allRequirementsMet = formData.hipaaTraining && formData.irbApproval && 
    formData.dataSecurityAgreement && formData.noExternalSharing && formData.institutionalAgreement

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    const response = await fetch(`${API_URL}/api/v1/access-requests`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(formData)
    })
    
    if (response.ok) {
      setSubmitted(true)
    }
  }

  if (submitted) {
    return (
      <div className="max-w-3xl mx-auto space-y-6">
        <Card className="bg-gray-800 border-gray-700">
          <CardContent className="p-12 text-center">
            <CheckCircle2 className="w-16 h-16 text-green-500 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-white mb-4">Access Request Submitted</h2>
            <p className="text-gray-400 mb-6">
              Your request has been submitted for review. An AdventHealth PI will review your application and contact you within 3-5 business days.
            </p>
            <Alert className="bg-blue-900 border-blue-700 text-left">
              <Shield className="w-4 h-4" />
              <AlertDescription className="text-blue-200">
                <strong>Next Steps:</strong>
                <ul className="list-disc list-inside mt-2 space-y-1">
                  <li>PI will review your credentials and research purpose</li>
                  <li>If approved, you'll receive an Entra ID B2B invitation</li>
                  <li>Complete MFA setup (required)</li>
                  <li>Access expires after 180 days (renewable)</li>
                </ul>
              </AlertDescription>
            </Alert>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h2 className="text-3xl font-bold text-white mb-2">External Researcher Access Request</h2>
        <p className="text-gray-400">Request access to AdventHealth cardiovascular research data</p>
      </div>

      <Alert className="bg-yellow-900 border-yellow-700">
        <Shield className="w-4 h-4" />
        <AlertDescription className="text-yellow-200">
          <strong>Important:</strong> All data is PHI-protected and subject to HIPAA regulations. 
          Access is granted only to approved researchers with valid IRB approval and institutional agreements.
        </AlertDescription>
      </Alert>

      <form onSubmit={handleSubmit} className="space-y-6">
        <Card className="bg-gray-800 border-gray-700">
          <CardHeader>
            <CardTitle className="text-white">Researcher Information</CardTitle>
            <CardDescription className="text-gray-400">Provide your professional details</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="fullName" className="text-white">Full Name *</Label>
                <Input
                  id="fullName"
                  required
                  value={formData.fullName}
                  onChange={(e) => setFormData({...formData, fullName: e.target.value})}
                  className="bg-gray-900 border-gray-700 text-white"
                  placeholder="Dr. John Smith"
                />
              </div>
              <div>
                <Label htmlFor="email" className="text-white">Email Address *</Label>
                <Input
                  id="email"
                  type="email"
                  required
                  value={formData.email}
                  onChange={(e) => setFormData({...formData, email: e.target.value})}
                  className="bg-gray-900 border-gray-700 text-white"
                  placeholder="john.smith@university.edu"
                />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="institution" className="text-white">Institution *</Label>
                <Input
                  id="institution"
                  required
                  value={formData.institution}
                  onChange={(e) => setFormData({...formData, institution: e.target.value})}
                  className="bg-gray-900 border-gray-700 text-white"
                  placeholder="University of Florida"
                />
              </div>
              <div>
                <Label htmlFor="position" className="text-white">Position/Title *</Label>
                <Input
                  id="position"
                  required
                  value={formData.position}
                  onChange={(e) => setFormData({...formData, position: e.target.value})}
                  className="bg-gray-900 border-gray-700 text-white"
                  placeholder="Associate Professor"
                />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gray-800 border-gray-700">
          <CardHeader>
            <CardTitle className="text-white">Research Details</CardTitle>
            <CardDescription className="text-gray-400">Describe your research project</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label htmlFor="projectInterest" className="text-white">Project of Interest *</Label>
              <Select value={formData.projectInterest} onValueChange={(value) => setFormData({...formData, projectInterest: value})}>
                <SelectTrigger className="bg-gray-900 border-gray-700 text-white">
                  <SelectValue placeholder="Select a project" />
                </SelectTrigger>
                <SelectContent className="bg-gray-900 border-gray-700">
                  <SelectItem value="cardiac-arrhythmia">Cardiac Arrhythmia Prediction Study</SelectItem>
                  <SelectItem value="heart-failure">Heart Failure Readmission Analysis</SelectItem>
                  <SelectItem value="coronary-disease">Coronary Artery Disease Risk Modeling</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label htmlFor="researchPurpose" className="text-white">Research Purpose *</Label>
              <Textarea
                id="researchPurpose"
                required
                value={formData.researchPurpose}
                onChange={(e) => setFormData({...formData, researchPurpose: e.target.value})}
                className="bg-gray-900 border-gray-700 text-white"
                placeholder="Describe the purpose of your research and how you plan to use the data..."
                rows={4}
              />
            </div>
            <div>
              <Label htmlFor="dataNeeded" className="text-white">Data Requirements *</Label>
              <Textarea
                id="dataNeeded"
                required
                value={formData.dataNeeded}
                onChange={(e) => setFormData({...formData, dataNeeded: e.target.value})}
                className="bg-gray-900 border-gray-700 text-white"
                placeholder="Specify which datasets and variables you need access to..."
                rows={3}
              />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gray-800 border-gray-700">
          <CardHeader>
            <CardTitle className="text-white">Compliance Requirements</CardTitle>
            <CardDescription className="text-gray-400">All requirements must be met for approval</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-start space-x-3">
              <Checkbox
                id="hipaaTraining"
                checked={formData.hipaaTraining}
                onCheckedChange={(checked) => setFormData({...formData, hipaaTraining: checked as boolean})}
                className="mt-1"
              />
              <div className="flex-1">
                <Label htmlFor="hipaaTraining" className="text-white font-medium cursor-pointer">
                  HIPAA Training Completed
                </Label>
                <p className="text-sm text-gray-400">I have completed HIPAA training within the last 12 months</p>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <Checkbox
                id="irbApproval"
                checked={formData.irbApproval}
                onCheckedChange={(checked) => setFormData({...formData, irbApproval: checked as boolean})}
                className="mt-1"
              />
              <div className="flex-1">
                <Label htmlFor="irbApproval" className="text-white font-medium cursor-pointer">
                  IRB Approval Obtained
                </Label>
                <p className="text-sm text-gray-400">My institution's IRB has approved this research project</p>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <Checkbox
                id="dataSecurityAgreement"
                checked={formData.dataSecurityAgreement}
                onCheckedChange={(checked) => setFormData({...formData, dataSecurityAgreement: checked as boolean})}
                className="mt-1"
              />
              <div className="flex-1">
                <Label htmlFor="dataSecurityAgreement" className="text-white font-medium cursor-pointer">
                  Data Security Agreement
                </Label>
                <p className="text-sm text-gray-400">I agree to maintain data security and use encrypted storage</p>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <Checkbox
                id="noExternalSharing"
                checked={formData.noExternalSharing}
                onCheckedChange={(checked) => setFormData({...formData, noExternalSharing: checked as boolean})}
                className="mt-1"
              />
              <div className="flex-1">
                <Label htmlFor="noExternalSharing" className="text-white font-medium cursor-pointer">
                  No External Data Sharing
                </Label>
                <p className="text-sm text-gray-400">I will not share data with external parties without written approval</p>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <Checkbox
                id="institutionalAgreement"
                checked={formData.institutionalAgreement}
                onCheckedChange={(checked) => setFormData({...formData, institutionalAgreement: checked as boolean})}
                className="mt-1"
              />
              <div className="flex-1">
                <Label htmlFor="institutionalAgreement" className="text-white font-medium cursor-pointer">
                  Institutional Data Use Agreement
                </Label>
                <p className="text-sm text-gray-400">My institution has signed a Data Use Agreement with AdventHealth</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <div className="flex justify-end gap-4">
          <Button type="button" variant="outline" onClick={() => navigate('/')} className="border-gray-700">
            Cancel
          </Button>
          <Button 
            type="submit" 
            disabled={!allRequirementsMet}
            className="bg-green-600 hover:bg-green-700 disabled:bg-gray-600 disabled:cursor-not-allowed"
          >
            <UserPlus className="w-4 h-4 mr-2" />
            Submit Access Request
          </Button>
        </div>
      </form>
    </div>
  )
}

function Notifications() {
  const [notifications, setNotifications] = useState<Notification[]>([])

  useEffect(() => {
    fetch(`${API_URL}/api/v1/notifications`)
      .then(res => res.json())
      .then(data => setNotifications(data))
  }, [])

  const markAsRead = async (notificationId: string) => {
    await fetch(`${API_URL}/api/v1/notifications/${notificationId}/read`, {
      method: 'PATCH'
    })
    setNotifications(notifications.map(n => 
      n.notificationId === notificationId ? { ...n, isRead: true } : n
    ))
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold text-white mb-2">Notifications</h2>
        <p className="text-gray-400">Stay updated on your research activities</p>
      </div>

      <div className="space-y-4">
        {notifications.map(notification => (
          <Card 
            key={notification.notificationId} 
            className={`bg-gray-800 border-gray-700 ${!notification.isRead ? 'border-l-4 border-l-blue-500' : ''}`}
          >
            <CardContent className="p-6">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <Badge className={
                      notification.type === 'Success' ? 'bg-green-500' :
                      notification.type === 'Warning' ? 'bg-yellow-500' :
                      notification.type === 'Error' ? 'bg-red-500' : 'bg-blue-500'
                    }>
                      {notification.type}
                    </Badge>
                    <span className="text-sm text-gray-400">{new Date(notification.createdAt).toLocaleString()}</span>
                  </div>
                  <p className="text-white">{notification.message}</p>
                </div>
                {!notification.isRead && (
                  <Button 
                    size="sm" 
                    variant="outline" 
                    onClick={() => markAsRead(notification.notificationId)}
                    className="border-gray-700"
                  >
                    Mark as Read
                  </Button>
                )}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false)

  return (
    <Router>
      <div className="min-h-screen bg-gray-950">
        <div className="flex">
          <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
          
          <main className="flex-1 min-h-screen">
            <header className="bg-gray-900 border-b border-gray-800 px-6 py-4">
              <div className="flex items-center gap-4">
                <button 
                  onClick={() => setSidebarOpen(true)}
                  className="lg:hidden text-gray-400 hover:text-white"
                >
                  <Menu className="w-6 h-6" />
                </button>
                <div className="flex-1">
                  <h1 className="text-xl font-semibold text-white">Cardiovascular Research Platform</h1>
                </div>
              </div>
            </header>
            
            <div className="p-6">
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/project/:projectId" element={<ProjectDetails />} />
                <Route path="/exports" element={<ExportRequests />} />
                <Route path="/notifications" element={<Notifications />} />
                <Route path="/request-access" element={<ExternalAccessRequest />} />
              </Routes>
            </div>
          </main>
        </div>
      </div>
    </Router>
  )
}

export default App
