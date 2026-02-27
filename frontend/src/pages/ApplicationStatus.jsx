import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { GraduationCap, CheckCircle, Clock, XCircle, AlertCircle } from 'lucide-react';
import DocumentUpload from '@/components/DocumentUpload';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const stages = [
  { key: 'intake', label: 'Application Intake', icon: Clock },
  { key: 'verification', label: 'Document Verification', icon: CheckCircle },
  { key: 'eligibility', label: 'Eligibility Screening', icon: AlertCircle },
  { key: 'interview', label: 'Interview Scheduling', icon: Clock },
  { key: 'decision', label: 'Decision Making', icon: CheckCircle },
  { key: 'dispatch', label: 'Offer Dispatch', icon: CheckCircle },
  { key: 'completed', label: 'Completed', icon: CheckCircle }
];

export default function ApplicationStatus() {
  const { threadId } = useParams();
  const [applicationData, setApplicationData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [wsConnected, setWsConnected] = useState(false);

  useEffect(() => {
    fetchApplicationStatus();
    
    // Setup WebSocket connection
    const wsUrl = BACKEND_URL.replace('https://', 'wss://').replace('http://', 'ws://');
    const ws = new WebSocket(`${wsUrl}/ws/${threadId}`);

    ws.onopen = () => {
      setWsConnected(true);
    };

    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      if (message.type === 'state_update' || message.type === 'workflow_complete') {
        setApplicationData(prev => ({
          ...prev,
          ...message.data
        }));
      }
    };

    ws.onerror = () => {
      setWsConnected(false);
    };

    ws.onclose = () => {
      setWsConnected(false);
    };

    return () => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.close();
      }
    };
  }, [threadId]);

  const fetchApplicationStatus = async () => {
    try {
      const response = await axios.get(`${BACKEND_URL}/api/applications/${threadId}`);
      setApplicationData(response.data);
    } catch (error) {
      console.error('Failed to fetch application status:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-stone-100 flex items-center justify-center">
        <div className="text-center">
          <Clock className="w-12 h-12 text-blue-900 animate-spin mx-auto mb-4" />
          <p className="text-slate-600">Loading application status...</p>
        </div>
      </div>
    );
  }

  if (!applicationData) {
    return (
      <div className="min-h-screen bg-stone-100 flex items-center justify-center">
        <div className="text-center">
          <XCircle className="w-12 h-12 text-red-600 mx-auto mb-4" />
          <p className="text-slate-600">Application not found</p>
        </div>
      </div>
    );
  }

  const currentStageIndex = stages.findIndex(s => s.key === applicationData.current_stage);
  const progress = ((currentStageIndex + 1) / stages.length) * 100;

  const getDecisionBadge = (decision) => {
    if (decision === 'admitted') return <Badge className="bg-green-600 text-white">Admitted</Badge>;
    if (decision === 'waitlisted') return <Badge className="bg-amber-600 text-white">Waitlisted</Badge>;
    if (decision === 'denied') return <Badge className="bg-red-600 text-white">Denied</Badge>;
    return null;
  };

  return (
    <div className="min-h-screen bg-stone-100 py-12 px-6">
      {/* Header */}
      <div className="max-w-5xl mx-auto mb-8">
        <Link to="/" className="inline-flex items-center gap-2 text-blue-900 hover:text-blue-800 mb-6">
          <GraduationCap className="w-6 h-6" />
          <span className="font-bold" style={{fontFamily: 'Merriweather, serif'}}>EduFlow</span>
        </Link>
      </div>

      <div className="max-w-5xl mx-auto space-y-6">
        {/* Status Overview */}
        <Card className="bg-white border border-stone-100 shadow-lg">
          <CardHeader className="p-8">
            <div className="flex items-center justify-between">
              <div>
                <CardTitle 
                  data-testid="status-title"
                  className="text-3xl font-light" 
                  style={{fontFamily: 'Merriweather, serif'}}
                >
                  Application Status
                </CardTitle>
                <p className="text-slate-600 mt-2" style={{fontFamily: 'JetBrains Mono, monospace'}}>
                  ID: {applicationData.application_id}
                </p>
              </div>
              {applicationData.final_decision && getDecisionBadge(applicationData.final_decision)}
            </div>
          </CardHeader>
          <CardContent className="p-8 pt-0">
            <div className="space-y-6">
              {/* Progress Bar */}
              <div>
                <div className="flex justify-between items-center mb-3">
                  <span className="text-sm font-medium text-slate-700">Overall Progress</span>
                  <span className="text-sm text-slate-600">{Math.round(progress)}%</span>
                </div>
                <Progress value={progress} className="h-3" data-testid="progress-bar" />
              </div>

              {/* WebSocket Status */}
              <div className="flex items-center gap-2 text-sm">
                <div className={`w-2 h-2 rounded-full ${wsConnected ? 'bg-green-500' : 'bg-red-500'}`} />
                <span className="text-slate-600">
                  {wsConnected ? 'Real-time updates active' : 'Reconnecting...'}
                </span>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Stage Progress */}
        <Card className="bg-white border border-stone-100 shadow-lg">
          <CardHeader className="p-8 border-b border-stone-100">
            <CardTitle className="text-2xl font-semibold">Workflow Stages</CardTitle>
          </CardHeader>
          <CardContent className="p-8">
            <div className="space-y-4">
              {stages.map((stage, index) => {
                const isActive = stage.key === applicationData.current_stage;
                const isCompleted = index < currentStageIndex;
                const Icon = stage.icon;

                return (
                  <div
                    key={stage.key}
                    data-testid={`stage-${stage.key}`}
                    className={`p-4 rounded-lg border transition-all ${
                      isActive
                        ? 'border-blue-500 bg-blue-50'
                        : isCompleted
                        ? 'border-green-500 bg-green-50'
                        : 'border-stone-200 bg-white'
                    }`}
                  >
                    <div className="flex items-center gap-4">
                      <div
                        className={`w-10 h-10 rounded-full flex items-center justify-center font-bold text-white ${
                          isCompleted
                            ? 'bg-green-500'
                            : isActive
                            ? 'bg-blue-500'
                            : 'bg-stone-300'
                        }`}
                      >
                        {isCompleted ? (
                          <CheckCircle className="w-6 h-6" />
                        ) : (
                          <Icon className="w-6 h-6" />
                        )}
                      </div>
                      <div className="flex-1">
                        <h3 className="font-semibold text-slate-900">{stage.label}</h3>
                        {isActive && (
                          <p className="text-sm text-blue-600 mt-1">In progress...</p>
                        )}
                        {isCompleted && (
                          <p className="text-sm text-green-600 mt-1">Completed</p>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>

        {/* Document Upload Section */}
        <DocumentUpload threadId={threadId} />

        {/* Agent Activity Log */}
        {applicationData.agent_reasoning && applicationData.agent_reasoning.length > 0 && (
          <Card className="bg-white border border-stone-100 shadow-lg">
            <CardHeader className="p-8 border-b border-stone-100">
              <CardTitle className="text-2xl font-semibold">Activity Log</CardTitle>
            </CardHeader>
            <CardContent className="p-8">
              <div className="space-y-3">
                {applicationData.agent_reasoning.map((activity, index) => (
                  <div key={index} className="flex items-start gap-3">
                    <CheckCircle className="w-5 h-5 text-green-600 mt-0.5 flex-shrink-0" />
                    <p className="text-slate-700">{activity}</p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}