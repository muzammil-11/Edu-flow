import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { GraduationCap, TrendingUp, Users, FileCheck, Clock, AlertCircle, BarChart3, ScrollText, CheckCircle, XCircle, Timer, LogOut } from 'lucide-react';
import ReviewQueue from '@/components/ReviewQueue';
import { useAuth } from '@/context/AuthContext';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

export default function AdminDashboard() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [applications, setApplications] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [auditLog, setAuditLog] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('pipeline');

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  useEffect(() => {
    fetchApplications();
    fetchAnalytics();
    const interval = setInterval(() => {
      fetchApplications();
      if (activeTab === 'analytics') fetchAnalytics();
    }, 5000);
    return () => clearInterval(interval);
  }, [activeTab]);

  const fetchApplications = async () => {
    try {
      const response = await axios.get(`${BACKEND_URL}/api/admin/applications`);
      setApplications(response.data.applications);
    } catch (error) {
      console.error('Failed to fetch applications:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchAnalytics = async () => {
    try {
      const response = await axios.get(`${BACKEND_URL}/api/admin/analytics`);
      setAnalytics(response.data.analytics);
    } catch (error) {
      console.error('Failed to fetch analytics:', error);
    }
  };

  const fetchAuditLog = async () => {
    try {
      const response = await axios.get(`${BACKEND_URL}/api/admin/audit-log`);
      setAuditLog(response.data.audit_log);
    } catch (error) {
      console.error('Failed to fetch audit log:', error);
    }
  };

  const getStageBadge = (stage) => {
    const stageColors = {
      intake: 'bg-blue-100 text-blue-800',
      verification: 'bg-purple-100 text-purple-800',
      eligibility: 'bg-amber-100 text-amber-800',
      interview: 'bg-indigo-100 text-indigo-800',
      human_review: 'bg-orange-100 text-orange-800',
      decision: 'bg-cyan-100 text-cyan-800',
      dispatch: 'bg-green-100 text-green-800',
      completed: 'bg-green-600 text-white'
    };
    return (
      <Badge className={stageColors[stage] || 'bg-gray-100 text-gray-800'}>
        {stage?.replace('_', ' ')}
      </Badge>
    );
  };

  const getDecisionBadge = (decision) => {
    if (!decision) return <Badge className="bg-stone-200 text-stone-600">Pending</Badge>;
    const colors = {
      admitted: 'bg-green-600 text-white',
      denied: 'bg-red-600 text-white',
      waitlisted: 'bg-amber-600 text-white',
    };
    return <Badge className={colors[decision] || 'bg-stone-200 text-stone-600'}>{decision}</Badge>;
  };

  const formatProcessingTime = (seconds) => {
    if (!seconds || seconds === 0) return 'N/A';
    if (seconds < 60) return `${Math.round(seconds)}s`;
    if (seconds < 3600) return `${Math.round(seconds / 60)}m`;
    return `${(seconds / 3600).toFixed(1)}h`;
  };

  const stats = analytics || {
    total: applications.length,
    pending: applications.filter(a => a.status === 'pending' || a.status === 'in_progress').length,
    admitted: applications.filter(a => a.final_decision === 'admitted').length,
    denied: applications.filter(a => a.final_decision === 'denied').length,
    completed: applications.filter(a => a.status === 'completed').length,
  };

  return (
    <div className="min-h-screen bg-stone-100">
      {/* Header */}
      <nav className="sticky top-0 z-50 backdrop-blur-xl bg-white/80 border-b border-stone-200/50">
        <div className="w-full px-6 py-4">
          <div className="flex items-center justify-between">
            <Link to="/" className="flex items-center gap-2">
              <GraduationCap className="w-8 h-8 text-blue-900" />
              <span className="text-xl font-bold text-blue-900" style={{fontFamily: 'Merriweather, serif'}}>
                EduFlow Admin
              </span>
            </Link>
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-green-500" />
                <span className="text-sm text-slate-600">System Active</span>
              </div>
              {user && (
                <span className="text-sm text-stone-500 hidden sm:block">{user.name} · {user.role}</span>
              )}
              <Button
                variant="ghost"
                size="sm"
                onClick={handleLogout}
                className="text-stone-500 hover:text-red-600"
                data-testid="admin-logout-btn"
              >
                <LogOut className="w-4 h-4 mr-1" /> Sign Out
              </Button>
            </div>
          </div>
        </div>
      </nav>

      <div className="w-full px-6 py-8">
        <Tabs defaultValue="pipeline" className="space-y-6" onValueChange={(val) => {
          setActiveTab(val);
          if (val === 'audit') fetchAuditLog();
          if (val === 'analytics') fetchAnalytics();
        }}>
          <TabsList className="grid w-full max-w-2xl grid-cols-4">
            <TabsTrigger value="pipeline" data-testid="pipeline-tab">Pipeline</TabsTrigger>
            <TabsTrigger value="reviews" data-testid="reviews-tab">Reviews</TabsTrigger>
            <TabsTrigger value="analytics" data-testid="analytics-tab">Analytics</TabsTrigger>
            <TabsTrigger value="audit" data-testid="audit-tab">Audit Log</TabsTrigger>
          </TabsList>

          {/* Pipeline Tab */}
          <TabsContent value="pipeline" className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <Card data-testid="stat-total-applications" className="bg-white border border-stone-100 shadow-sm">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-slate-600">Total Applications</p>
                      <p className="text-3xl font-bold text-slate-900 mt-2">{stats.total}</p>
                    </div>
                    <Users className="w-10 h-10 text-blue-600" />
                  </div>
                </CardContent>
              </Card>
              <Card data-testid="stat-pending" className="bg-white border border-stone-100 shadow-sm">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-slate-600">In Progress</p>
                      <p className="text-3xl font-bold text-amber-600 mt-2">{stats.pending}</p>
                    </div>
                    <Clock className="w-10 h-10 text-amber-600" />
                  </div>
                </CardContent>
              </Card>
              <Card data-testid="stat-admitted" className="bg-white border border-stone-100 shadow-sm">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-slate-600">Completed</p>
                      <p className="text-3xl font-bold text-green-600 mt-2">{stats.completed || 0}</p>
                    </div>
                    <FileCheck className="w-10 h-10 text-green-600" />
                  </div>
                </CardContent>
              </Card>
              <Card data-testid="stat-conversion-rate" className="bg-white border border-stone-100 shadow-sm">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-slate-600">Admission Rate</p>
                      <p className="text-3xl font-bold text-blue-900 mt-2">
                        {stats.admission_rate || (stats.total > 0 ? Math.round((stats.admitted / stats.total) * 100) : 0)}%
                      </p>
                    </div>
                    <TrendingUp className="w-10 h-10 text-blue-900" />
                  </div>
                </CardContent>
              </Card>
            </div>

            <Card className="bg-white border border-stone-100 shadow-lg">
              <CardHeader className="p-6 border-b border-stone-100">
                <CardTitle className="text-2xl font-semibold">Application Pipeline</CardTitle>
              </CardHeader>
              <CardContent className="p-0">
                {loading ? (
                  <div className="p-12 text-center text-slate-600">
                    <Clock className="w-8 h-8 animate-spin mx-auto mb-4" />
                    Loading applications...
                  </div>
                ) : applications.length === 0 ? (
                  <div className="p-12 text-center text-slate-600">
                    <FileCheck className="w-12 h-12 mx-auto mb-4 text-slate-400" />
                    <p>No applications yet</p>
                  </div>
                ) : (
                  <div className="overflow-x-auto">
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Applicant</TableHead>
                          <TableHead>Email</TableHead>
                          <TableHead>Program</TableHead>
                          <TableHead>GPA</TableHead>
                          <TableHead>Stage</TableHead>
                          <TableHead>Decision</TableHead>
                          <TableHead>Submitted</TableHead>
                          <TableHead>Actions</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {applications.map((app) => (
                          <TableRow key={app.thread_id} data-testid={`application-row-${app.thread_id}`}>
                            <TableCell className="font-medium">{app.submitted_data?.name || 'N/A'}</TableCell>
                            <TableCell>{app.user_email}</TableCell>
                            <TableCell>{app.submitted_data?.program || 'N/A'}</TableCell>
                            <TableCell>{app.submitted_data?.gpa || 'N/A'}</TableCell>
                            <TableCell>{getStageBadge(app.current_stage)}</TableCell>
                            <TableCell>{getDecisionBadge(app.final_decision)}</TableCell>
                            <TableCell>{new Date(app.created_at).toLocaleDateString()}</TableCell>
                            <TableCell>
                              <Link to={`/status/${app.thread_id}`} className="text-blue-900 hover:underline text-sm" data-testid={`view-details-${app.thread_id}`}>
                                View
                              </Link>
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Reviews Tab */}
          <TabsContent value="reviews">
            <ReviewQueue />
          </TabsContent>

          {/* Analytics Tab */}
          <TabsContent value="analytics" className="space-y-6">
            {analytics ? (
              <>
                {/* Key Metrics */}
                <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                  <Card data-testid="analytics-admitted" className="bg-white border-l-4 border-l-green-500">
                    <CardContent className="p-5">
                      <div className="flex items-center gap-3">
                        <CheckCircle className="w-8 h-8 text-green-600" />
                        <div>
                          <p className="text-xs text-slate-500 uppercase tracking-wide">Admitted</p>
                          <p className="text-2xl font-bold text-green-700">{analytics.admitted}</p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                  <Card data-testid="analytics-denied" className="bg-white border-l-4 border-l-red-500">
                    <CardContent className="p-5">
                      <div className="flex items-center gap-3">
                        <XCircle className="w-8 h-8 text-red-600" />
                        <div>
                          <p className="text-xs text-slate-500 uppercase tracking-wide">Denied</p>
                          <p className="text-2xl font-bold text-red-700">{analytics.denied}</p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                  <Card data-testid="analytics-waitlisted" className="bg-white border-l-4 border-l-amber-500">
                    <CardContent className="p-5">
                      <div className="flex items-center gap-3">
                        <AlertCircle className="w-8 h-8 text-amber-600" />
                        <div>
                          <p className="text-xs text-slate-500 uppercase tracking-wide">Waitlisted</p>
                          <p className="text-2xl font-bold text-amber-700">{analytics.waitlisted}</p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                  <Card data-testid="analytics-in-review" className="bg-white border-l-4 border-l-blue-500">
                    <CardContent className="p-5">
                      <div className="flex items-center gap-3">
                        <ScrollText className="w-8 h-8 text-blue-600" />
                        <div>
                          <p className="text-xs text-slate-500 uppercase tracking-wide">In Review</p>
                          <p className="text-2xl font-bold text-blue-700">{analytics.in_review}</p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                  <Card data-testid="analytics-avg-time" className="bg-white border-l-4 border-l-indigo-500">
                    <CardContent className="p-5">
                      <div className="flex items-center gap-3">
                        <Timer className="w-8 h-8 text-indigo-600" />
                        <div>
                          <p className="text-xs text-slate-500 uppercase tracking-wide">Avg Time</p>
                          <p className="text-2xl font-bold text-indigo-700">{formatProcessingTime(analytics.avg_processing_time_seconds)}</p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </div>

                {/* Program Breakdown */}
                <Card className="bg-white border border-stone-100 shadow-lg">
                  <CardHeader className="p-6 border-b border-stone-100">
                    <CardTitle className="text-xl font-semibold flex items-center gap-2">
                      <BarChart3 className="w-5 h-5" /> Program Breakdown
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="p-0">
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Program</TableHead>
                          <TableHead className="text-center">Total</TableHead>
                          <TableHead className="text-center">Admitted</TableHead>
                          <TableHead className="text-center">Denied</TableHead>
                          <TableHead className="text-center">Waitlisted</TableHead>
                          <TableHead className="text-center">Rate</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {Object.entries(analytics.programs || {}).map(([prog, data]) => (
                          <TableRow key={prog} data-testid={`program-row-${prog.replace(/\s+/g, '-').toLowerCase()}`}>
                            <TableCell className="font-medium">{prog}</TableCell>
                            <TableCell className="text-center">{data.total}</TableCell>
                            <TableCell className="text-center text-green-700 font-semibold">{data.admitted}</TableCell>
                            <TableCell className="text-center text-red-700 font-semibold">{data.denied}</TableCell>
                            <TableCell className="text-center text-amber-700 font-semibold">{data.waitlisted}</TableCell>
                            <TableCell className="text-center">
                              <Badge className={data.admitted > 0 ? 'bg-green-100 text-green-800' : 'bg-stone-100 text-stone-600'}>
                                {data.total > 0 ? Math.round((data.admitted / data.total) * 100) : 0}%
                              </Badge>
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </CardContent>
                </Card>

                {/* GPA Distribution */}
                <Card className="bg-white border border-stone-100 shadow-lg">
                  <CardHeader className="p-6 border-b border-stone-100">
                    <CardTitle className="text-xl font-semibold">GPA Distribution</CardTitle>
                  </CardHeader>
                  <CardContent className="p-6">
                    <div className="grid grid-cols-5 gap-4">
                      {Object.entries(analytics.gpa_distribution || {}).map(([range, count]) => (
                        <div key={range} className="text-center p-4 rounded-lg bg-stone-50 border border-stone-200" data-testid={`gpa-range-${range}`}>
                          <p className="text-2xl font-bold text-slate-900">{count}</p>
                          <p className="text-xs text-slate-500 mt-1">{range.replace('_', ' ')}</p>
                          <div className="mt-2 h-2 bg-stone-200 rounded-full overflow-hidden">
                            <div
                              className="h-full bg-blue-600 rounded-full transition-all"
                              style={{ width: `${analytics.total > 0 ? (count / analytics.total) * 100 : 0}%` }}
                            />
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </>
            ) : (
              <div className="p-12 text-center text-slate-600">
                <Clock className="w-8 h-8 animate-spin mx-auto mb-4" />
                Loading analytics...
              </div>
            )}
          </TabsContent>

          {/* Audit Log Tab */}
          <TabsContent value="audit" className="space-y-6">
            <Card className="bg-white border border-stone-100 shadow-lg">
              <CardHeader className="p-6 border-b border-stone-100">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-xl font-semibold flex items-center gap-2">
                    <ScrollText className="w-5 h-5" /> Audit Trail
                  </CardTitle>
                  <Badge className="bg-stone-200 text-stone-700">{auditLog.length} entries</Badge>
                </div>
              </CardHeader>
              <CardContent className="p-0">
                {auditLog.length === 0 ? (
                  <div className="p-12 text-center text-slate-500">
                    <ScrollText className="w-10 h-10 mx-auto mb-3 text-slate-400" />
                    <p>Click the Audit Log tab to load entries</p>
                  </div>
                ) : (
                  <div className="divide-y divide-stone-100">
                    {auditLog.map((entry, idx) => (
                      <div key={idx} className="p-5 hover:bg-stone-50 transition-colors" data-testid={`audit-entry-${idx}`}>
                        <div className="flex items-start justify-between mb-2">
                          <div className="flex items-center gap-3">
                            <span className="font-semibold text-slate-900">{entry.applicant_name}</span>
                            <Badge className="bg-stone-100 text-stone-600 text-xs">{entry.program}</Badge>
                            {entry.human_review && (
                              <Badge className="bg-blue-100 text-blue-700 text-xs">Human Reviewed</Badge>
                            )}
                          </div>
                          <div className="flex items-center gap-2">
                            {getStageBadge(entry.current_stage)}
                            {getDecisionBadge(entry.final_decision)}
                          </div>
                        </div>
                        <div className="text-sm text-slate-500 mb-2">
                          GPA: {entry.gpa} | Submitted: {new Date(entry.created_at).toLocaleString()}
                          {entry.updated_at && entry.updated_at !== entry.created_at && (
                            <span> | Updated: {new Date(entry.updated_at).toLocaleString()}</span>
                          )}
                        </div>
                        {entry.agent_reasoning && entry.agent_reasoning.length > 0 && (
                          <div className="mt-2 space-y-1">
                            {entry.agent_reasoning.map((reason, rIdx) => (
                              <div key={rIdx} className="flex items-start gap-2 text-xs text-slate-600 bg-stone-50 p-2 rounded">
                                <CheckCircle className="w-3 h-3 text-green-500 mt-0.5 flex-shrink-0" />
                                <span>{reason}</span>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
