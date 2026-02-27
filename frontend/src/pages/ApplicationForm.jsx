import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { GraduationCap, Loader2 } from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

export default function ApplicationForm() {
  const navigate = useNavigate();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    program: '',
    gpa: '',
    test_scores: '',
    essay: ''
  });

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      const response = await axios.post(
        `${BACKEND_URL}/api/applications`,
        {
          ...formData,
          gpa: parseFloat(formData.gpa)
        }
      );

      toast.success('Application submitted successfully!');
      navigate(`/status/${response.data.thread_id}`);
    } catch (error) {
      console.error('Failed to submit application:', error);
      toast.error('Failed to submit application. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-stone-100 py-12 px-6">
      {/* Header */}
      <div className="max-w-4xl mx-auto mb-8">
        <Link to="/" className="inline-flex items-center gap-2 text-blue-900 hover:text-blue-800 mb-6">
          <GraduationCap className="w-6 h-6" />
          <span className="font-bold" style={{fontFamily: 'Merriweather, serif'}}>EduFlow</span>
        </Link>
      </div>

      <div className="max-w-4xl mx-auto">
        <Card className="bg-white border border-stone-100 shadow-lg">
          <CardHeader className="p-8 border-b border-stone-100">
            <CardTitle 
              data-testid="application-form-title"
              className="text-3xl font-light" 
              style={{fontFamily: 'Merriweather, serif'}}
            >
              University Application
            </CardTitle>
            <CardDescription className="text-base text-slate-600 mt-2">
              Complete the form below to begin your admission process. Our AI system will guide your application through each stage.
            </CardDescription>
          </CardHeader>
          <CardContent className="p-8">
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Personal Information */}
              <div className="space-y-4">
                <h3 className="text-xl font-semibold text-slate-900">Personal Information</h3>
                
                <div>
                  <Label htmlFor="name" className="text-sm font-medium text-slate-700">Full Name *</Label>
                  <Input
                    id="name"
                    name="name"
                    data-testid="name-input"
                    value={formData.name}
                    onChange={handleInputChange}
                    required
                    className="mt-1 bg-stone-50 border-stone-200 focus:border-blue-900 focus:ring-1 focus:ring-blue-900 rounded-md h-12 px-4"
                    placeholder="John Doe"
                  />
                </div>

                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="email" className="text-sm font-medium text-slate-700">Email Address *</Label>
                    <Input
                      id="email"
                      name="email"
                      type="email"
                      data-testid="email-input"
                      value={formData.email}
                      onChange={handleInputChange}
                      required
                      className="mt-1 bg-stone-50 border-stone-200 focus:border-blue-900 focus:ring-1 focus:ring-blue-900 rounded-md h-12 px-4"
                      placeholder="john@example.com"
                    />
                  </div>
                  <div>
                    <Label htmlFor="phone" className="text-sm font-medium text-slate-700">Phone Number *</Label>
                    <Input
                      id="phone"
                      name="phone"
                      data-testid="phone-input"
                      value={formData.phone}
                      onChange={handleInputChange}
                      required
                      className="mt-1 bg-stone-50 border-stone-200 focus:border-blue-900 focus:ring-1 focus:ring-blue-900 rounded-md h-12 px-4"
                      placeholder="+1 (555) 123-4567"
                    />
                  </div>
                </div>
              </div>

              {/* Academic Information */}
              <div className="space-y-4 pt-6 border-t border-stone-100">
                <h3 className="text-xl font-semibold text-slate-900">Academic Information</h3>
                
                <div>
                  <Label htmlFor="program" className="text-sm font-medium text-slate-700">Program *</Label>
                  <Select 
                    name="program" 
                    value={formData.program} 
                    onValueChange={(value) => setFormData(prev => ({...prev, program: value}))}
                  >
                    <SelectTrigger 
                      data-testid="program-select"
                      className="mt-1 bg-stone-50 border-stone-200 focus:border-blue-900 focus:ring-1 focus:ring-blue-900 rounded-md h-12"
                    >
                      <SelectValue placeholder="Select a program" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="Computer Science">Computer Science</SelectItem>
                      <SelectItem value="Engineering">Engineering</SelectItem>
                      <SelectItem value="Business Administration">Business Administration</SelectItem>
                      <SelectItem value="Medicine">Medicine</SelectItem>
                      <SelectItem value="Law">Law</SelectItem>
                      <SelectItem value="Arts & Humanities">Arts & Humanities</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="gpa" className="text-sm font-medium text-slate-700">GPA (4.0 scale) *</Label>
                    <Input
                      id="gpa"
                      name="gpa"
                      type="number"
                      step="0.01"
                      min="0"
                      max="4.0"
                      data-testid="gpa-input"
                      value={formData.gpa}
                      onChange={handleInputChange}
                      required
                      className="mt-1 bg-stone-50 border-stone-200 focus:border-blue-900 focus:ring-1 focus:ring-blue-900 rounded-md h-12 px-4"
                      placeholder="3.75"
                    />
                  </div>
                  <div>
                    <Label htmlFor="test_scores" className="text-sm font-medium text-slate-700">Test Scores (SAT/ACT)</Label>
                    <Input
                      id="test_scores"
                      name="test_scores"
                      data-testid="test-scores-input"
                      value={formData.test_scores}
                      onChange={handleInputChange}
                      className="mt-1 bg-stone-50 border-stone-200 focus:border-blue-900 focus:ring-1 focus:ring-blue-900 rounded-md h-12 px-4"
                      placeholder="SAT: 1450"
                    />
                  </div>
                </div>
              </div>

              {/* Personal Statement */}
              <div className="space-y-4 pt-6 border-t border-stone-100">
                <h3 className="text-xl font-semibold text-slate-900">Personal Statement</h3>
                
                <div>
                  <Label htmlFor="essay" className="text-sm font-medium text-slate-700">Why do you want to join this program?</Label>
                  <Textarea
                    id="essay"
                    name="essay"
                    data-testid="essay-textarea"
                    value={formData.essay}
                    onChange={handleInputChange}
                    rows={6}
                    className="mt-1 bg-stone-50 border-stone-200 focus:border-blue-900 focus:ring-1 focus:ring-blue-900 rounded-md p-4"
                    placeholder="Share your motivations, goals, and what makes you a great fit for this program..."
                  />
                </div>
              </div>

              {/* Submit Button */}
              <div className="pt-6">
                <Button
                  type="submit"
                  data-testid="submit-application-btn"
                  disabled={isSubmitting || !formData.name || !formData.email || !formData.phone || !formData.program || !formData.gpa}
                  className="w-full bg-blue-900 text-white hover:bg-blue-800 shadow-sm rounded-full px-8 py-6 text-lg font-medium transition-all hover:scale-[1.02] disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isSubmitting ? (
                    <>
                      <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                      Processing Application...
                    </>
                  ) : (
                    'Submit Application'
                  )}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}