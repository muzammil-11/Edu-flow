import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { AlertCircle, CheckCircle, XCircle } from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

export default function ReviewQueue() {
  const [pendingReviews, setPendingReviews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedReview, setSelectedReview] = useState(null);
  const [comments, setComments] = useState('');
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    fetchPendingReviews();
    const interval = setInterval(fetchPendingReviews, 10000);
    return () => clearInterval(interval);
  }, []);

  const fetchPendingReviews = async () => {
    try {
      const response = await axios.get(`${BACKEND_URL}/api/admin/pending-reviews`);
      setPendingReviews(response.data.pending_reviews || []);
    } catch (error) {
      console.error('Failed to fetch pending reviews:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitReview = async (threadId, approved) => {
    setSubmitting(true);
    try {
      await axios.post(`${BACKEND_URL}/api/admin/review/${threadId}`, {
        approved,
        comments
      });

      toast.success(approved ? 'Application approved!' : 'Application rejected');
      setSelectedReview(null);
      setComments('');
      fetchPendingReviews();
    } catch (error) {
      console.error('Failed to submit review:', error);
      toast.error('Failed to submit review decision');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return <div className="text-center py-8">Loading reviews...</div>;
  }

  return (
    <div className="space-y-6">
      <Card className="bg-white border border-stone-100 shadow-lg">
        <CardHeader className="p-6 border-b border-stone-100">
          <div className="flex items-center justify-between">
            <CardTitle className="text-2xl font-semibold">Applications Requiring Review</CardTitle>
            <Badge className="bg-amber-600 text-white">
              {pendingReviews.length} Pending
            </Badge>
          </div>
        </CardHeader>
        <CardContent className="p-6">
          {pendingReviews.length === 0 ? (
            <div className="text-center py-12">
              <CheckCircle className="w-16 h-16 mx-auto text-green-600 mb-4" />
              <p className="text-lg font-medium text-slate-900">All caught up!</p>
              <p className="text-slate-600 mt-2">No applications require review at this time.</p>
            </div>
          ) : (
            <div className="space-y-4">
              {pendingReviews.map((review) => (
                <div
                  key={review.thread_id}
                  className="border border-stone-200 rounded-lg p-6 hover:shadow-md transition-shadow"
                  data-testid={`review-item-${review.thread_id}`}
                >
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <h3 className="text-lg font-semibold text-slate-900">
                        {review.applicant_name}
                      </h3>
                      <p className="text-sm text-slate-600">{review.applicant_email}</p>
                    </div>
                    <AlertCircle className="w-6 h-6 text-amber-600" />
                  </div>

                  <div className="grid grid-cols-2 gap-4 mb-4">
                    <div>
                      <p className="text-xs text-slate-500 uppercase tracking-wide">Program</p>
                      <p className="text-sm font-medium text-slate-900">{review.program}</p>
                    </div>
                    <div>
                      <p className="text-xs text-slate-500 uppercase tracking-wide">GPA</p>
                      <p className="text-sm font-medium text-slate-900">{review.gpa}</p>
                    </div>
                    <div>
                      <p className="text-xs text-slate-500 uppercase tracking-wide">Eligibility Score</p>
                      <p className="text-sm font-medium text-slate-900">
                        {review.eligibility_score?.toFixed(1)}/100
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-slate-500 uppercase tracking-wide">Current Stage</p>
                      <Badge className="bg-blue-100 text-blue-800 capitalize">
                        {review.current_stage}
                      </Badge>
                    </div>
                  </div>

                  <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 mb-4">
                    <p className="text-sm font-medium text-amber-900 mb-1">Review Reason:</p>
                    <p className="text-sm text-amber-800">{review.review_reason}</p>
                  </div>

                  {selectedReview === review.thread_id ? (
                    <div className="space-y-4">
                      <div>
                        <label className="text-sm font-medium text-slate-700 mb-2 block">
                          Review Comments (Optional)
                        </label>
                        <Textarea
                          value={comments}
                          onChange={(e) => setComments(e.target.value)}
                          placeholder="Add any additional comments or notes..."
                          rows={3}
                          data-testid="review-comments"
                          className="bg-stone-50"
                        />
                      </div>
                      <div className="flex gap-3">
                        <Button
                          onClick={() => handleSubmitReview(review.thread_id, true)}
                          disabled={submitting}
                          data-testid="approve-button"
                          className="flex-1 bg-green-600 text-white hover:bg-green-700"
                        >
                          <CheckCircle className="mr-2 h-4 w-4" />
                          Approve Application
                        </Button>
                        <Button
                          onClick={() => handleSubmitReview(review.thread_id, false)}
                          disabled={submitting}
                          data-testid="reject-button"
                          className="flex-1 bg-red-600 text-white hover:bg-red-700"
                        >
                          <XCircle className="mr-2 h-4 w-4" />
                          Reject Application
                        </Button>
                        <Button
                          onClick={() => {
                            setSelectedReview(null);
                            setComments('');
                          }}
                          variant="outline"
                          disabled={submitting}
                        >
                          Cancel
                        </Button>
                      </div>
                    </div>
                  ) : (
                    <Button
                      onClick={() => setSelectedReview(review.thread_id)}
                      data-testid="review-button"
                      className="w-full bg-blue-900 text-white hover:bg-blue-800"
                    >
                      Review Application
                    </Button>
                  )}
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
