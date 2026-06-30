import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { GraduationCap, Loader2 } from 'lucide-react';
import { toast } from 'sonner';
import { useAuth } from '@/context/AuthContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';

export default function RegisterPage() {
  const navigate = useNavigate();
  const { register } = useAuth();
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState({ name: '', email: '', password: '', confirmPassword: '' });

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (form.password !== form.confirmPassword) {
      toast.error('Passwords do not match');
      return;
    }
    if (form.password.length < 8) {
      toast.error('Password must be at least 8 characters');
      return;
    }
    setLoading(true);
    try {
      const user = await register(form.name, form.email, form.password);
      toast.success(`Account created! Welcome, ${user.name}`);
      navigate('/apply', { replace: true });
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Registration failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-stone-100 flex items-center justify-center px-4 py-12">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <Link to="/" className="inline-flex items-center gap-2 text-blue-900 hover:text-blue-800">
            <GraduationCap className="w-8 h-8" />
            <span className="font-serif text-xl font-bold">EDU FLOW UNIVERSITY</span>
          </Link>
        </div>

        <Card className="border-stone-200 shadow-lg">
          <CardHeader className="text-center pb-4">
            <CardTitle className="font-serif text-2xl text-blue-900">Create Account</CardTitle>
            <CardDescription>Start your application journey</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-1">
                <Label htmlFor="name">Full Name</Label>
                <Input
                  id="name"
                  placeholder="John Smith"
                  value={form.name}
                  onChange={(e) => setForm(p => ({ ...p, name: e.target.value }))}
                  required
                  data-testid="register-name"
                />
              </div>
              <div className="space-y-1">
                <Label htmlFor="email">Email Address</Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="you@example.com"
                  value={form.email}
                  onChange={(e) => setForm(p => ({ ...p, email: e.target.value }))}
                  required
                  data-testid="register-email"
                />
              </div>
              <div className="space-y-1">
                <Label htmlFor="password">Password</Label>
                <Input
                  id="password"
                  type="password"
                  placeholder="Min. 8 characters"
                  value={form.password}
                  onChange={(e) => setForm(p => ({ ...p, password: e.target.value }))}
                  required
                  data-testid="register-password"
                />
              </div>
              <div className="space-y-1">
                <Label htmlFor="confirmPassword">Confirm Password</Label>
                <Input
                  id="confirmPassword"
                  type="password"
                  placeholder="Re-enter password"
                  value={form.confirmPassword}
                  onChange={(e) => setForm(p => ({ ...p, confirmPassword: e.target.value }))}
                  required
                  data-testid="register-confirm-password"
                />
              </div>
              <Button
                type="submit"
                className="w-full bg-blue-900 hover:bg-blue-800 text-white"
                disabled={loading}
                data-testid="register-submit"
              >
                {loading ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : null}
                {loading ? 'Creating account...' : 'Create Account'}
              </Button>
            </form>

            <p className="text-center text-sm text-stone-500 mt-6">
              Already have an account?{' '}
              <Link to="/login" className="text-blue-900 hover:underline font-medium">
                Sign in
              </Link>
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
