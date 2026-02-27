import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { GraduationCap, TrendingUp, Users, FileCheck, Clock, AlertCircle } from 'lucide-react';
import ReviewQueue from '@/components/ReviewQueue';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

export default function AdminDashboard() {
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    total: 0,
    pending: 0,
    admitted: 0,
    denied: 0
  });

  useEffect(() => {
    fetchApplications();
    const interval = setInterval(fetchApplications, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchApplications = async () => {
    try {
      const response = await axios.get(`${BACKEND_URL}/api/admin/applications`);
      const apps = response.data.applications;
      setApplications(apps);
      
      // Calculate stats
      setStats({
        total: apps.length,
        pending: apps.filter(a => a.status === 'pending' || a.status === 'in_progress').length,
        admitted: apps.filter(a => a.current_stage === 'completed').length,
        denied: apps.filter(a => a.status === 'rejected').length
      });
    } catch (error) {
      console.error('Failed to fetch applications:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStageBadge = (stage) => {
    const stageColors = {
      intake: 'bg-blue-100 text-blue-800',
      verification: 'bg-purple-100 text-purple-800',
      eligibility: 'bg-amber-100 text-amber-800',
      interview: 'bg-indigo-100 text-indigo-800',
      decision: 'bg-orange-100 text-orange-800',
      dispatch: 'bg-green-100 text-green-800',
      completed: 'bg-green-600 text-white'
    };
    
    return (
      <Badge className={stageColors[stage] || 'bg-gray-100 text-gray-800'}>
        {stage}
      </Badge>
    );
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
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-green-500" />
              <span className="text-sm text-slate-600">System Active</span>
            </div>
          </div>
        </div>
      </nav>

      <div className="w-full px-6 py-8">
        {/* Tabs for different views */}
        <Tabs defaultValue="pipeline" className="space-y-6">
          <TabsList className="grid w-full max-w-md grid-cols-2">
            <TabsTrigger value="pipeline" data-testid="pipeline-tab">Pipeline</TabsTrigger>
            <TabsTrigger value="reviews" data-testid="reviews-tab">
              Reviews {stats.pending > 0 && <Badge className="ml-2 bg-amber-600">{stats.pending}</Badge>}
            </TabsTrigger>
          </TabsList>

          <TabsContent value="pipeline" className="space-y-6">
            {/* Stats Overview */}
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
                      <p className="text-3xl font-bold text-green-600 mt-2">{stats.admitted}</p>
                    </div>
                    <FileCheck className="w-10 h-10 text-green-600" />
                  </div>
                </CardContent>
              </Card>

              <Card data-testid="stat-conversion-rate" className="bg-white border border-stone-100 shadow-sm">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-slate-600">Success Rate</p>
                      <p className="text-3xl font-bold text-blue-900 mt-2">
                        {stats.total > 0 ? Math.round((stats.admitted / stats.total) * 100) : 0}%
                      </p>
                    </div>
                    <TrendingUp className="w-10 h-10 text-blue-900" />
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Applications Table */}
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
                    <Link to="/apply" className="text-blue-900 hover:underline mt-2 inline-block">
                      Submit the first application
                    </Link>
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
                          <TableHead>Current Stage</TableHead>
                          <TableHead>Status</TableHead>
                          <TableHead>Submitted</TableHead>
                          <TableHead>Actions</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {applications.map((app) => (
                          <TableRow key={app.thread_id} data-testid={`application-row-${app.thread_id}`}>
                            <TableCell className="font-medium">
                              {app.submitted_data?.name || 'N/A'}
                            </TableCell>
                            <TableCell>{app.user_email}</TableCell>
                            <TableCell>{app.submitted_data?.program || 'N/A'}</TableCell>
                            <TableCell>{app.submitted_data?.gpa || 'N/A'}</TableCell>
                            <TableCell>{getStageBadge(app.current_stage)}</TableCell>
                            <TableCell>
                              <Badge className={
                                app.status === 'completed' ? 'bg-green-600 text-white' :
                                app.status === 'in_progress' ? 'bg-blue-600 text-white' :
                                'bg-stone-300 text-stone-800'
                              }>
                                {app.status}
                              </Badge>
                            </TableCell>
                            <TableCell>
                              {new Date(app.created_at).toLocaleDateString()}
                            </TableCell>
                            <TableCell>
                              <Link 
                                to={`/status/${app.thread_id}`}
                                className="text-blue-900 hover:underline text-sm"
                                data-testid={`view-details-${app.thread_id}`}
                              >
                                View Details
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

          <TabsContent value="reviews">
            <ReviewQueue />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
