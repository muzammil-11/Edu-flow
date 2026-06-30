import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { GraduationCap, FileCheck, Users, Calendar, CheckCircle, Mail, LogOut, LogIn } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';

export default function LandingPage() {
  const { user, logout, isAdmin } = useAuth();

  return (
    <div className="min-h-screen bg-stone-100">
      {/* Navigation */}
      <nav className="sticky top-0 z-50 backdrop-blur-xl bg-white/80 border-b border-stone-200/50">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <GraduationCap className="w-8 h-8 text-blue-900" />
              <span className="text-xl font-bold text-blue-900" style={{fontFamily: 'Merriweather, serif'}}>EduFlow</span>
            </div>
            <div className="flex items-center gap-4">
              {user ? (
                <>
                  <span className="text-sm text-stone-600 hidden sm:block">
                    {user.name}
                  </span>
                  {isAdmin && (
                    <Link to="/admin">
                      <Button
                        data-testid="admin-dashboard-nav-btn"
                        variant="ghost"
                        className="text-stone-600 hover:text-blue-900 hover:bg-stone-100 rounded-lg"
                      >
                        Admin
                      </Button>
                    </Link>
                  )}
                  <Link to="/apply">
                    <Button
                      data-testid="apply-now-nav-btn"
                      className="bg-blue-900 text-white hover:bg-blue-800 shadow-sm rounded-full px-6 py-2 font-medium transition-all hover:scale-105"
                    >
                      Apply Now
                    </Button>
                  </Link>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={logout}
                    className="text-stone-500 hover:text-red-600"
                    data-testid="logout-btn"
                  >
                    <LogOut className="w-4 h-4" />
                  </Button>
                </>
              ) : (
                <>
                  <Link to="/login">
                    <Button variant="ghost" className="text-stone-600 hover:text-blue-900">
                      <LogIn className="w-4 h-4 mr-1" /> Sign In
                    </Button>
                  </Link>
                  <Link to="/register">
                    <Button
                      data-testid="apply-now-nav-btn"
                      className="bg-blue-900 text-white hover:bg-blue-800 shadow-sm rounded-full px-6 font-medium transition-all hover:scale-105"
                    >
                      Apply Now
                    </Button>
                  </Link>
                </>
              )}
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative py-24 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div className="space-y-8">
              <h1 
                data-testid="hero-heading"
                className="text-5xl lg:text-6xl font-light text-slate-900 tracking-tight" 
                style={{fontFamily: 'Merriweather, serif'}}
              >
                AI-Powered University Admissions
              </h1>
              <p className="text-lg text-slate-600 leading-relaxed">
                Experience the future of university applications with our intelligent workflow system. 
                Automated processing, real-time tracking, and transparent decision-making.
              </p>
              <div className="flex gap-4">
                <Link to="/apply">
                  <Button 
                    data-testid="get-started-btn"
                    className="bg-blue-900 text-white hover:bg-blue-800 shadow-sm rounded-full px-8 py-6 text-lg font-medium transition-all hover:scale-105"
                  >
                    Get Started
                  </Button>
                </Link>
                <Button 
                  data-testid="learn-more-btn"
                  variant="outline"
                  className="bg-white text-blue-900 border border-stone-200 hover:bg-stone-50 rounded-full px-6 py-4"
                >
                  Learn More
                </Button>
              </div>
            </div>
            <div className="relative">
              <img 
                src="https://images.unsplash.com/photo-1680444873773-7c106c23ac52?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NjAzNTl8MHwxfHNlYXJjaHwxfHx1bml2ZXJzaXR5JTIwY2FtcHVzJTIwbW9kZXJuJTIwYXJjaGl0ZWN0dXJlfGVufDB8fHx8MTc3MjIzMTgzNnww&ixlib=rb-4.1.0&q=85"
                alt="Modern University Campus"
                className="rounded-lg shadow-xl"
              />
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 px-6 bg-white">
        <div className="max-w-7xl mx-auto">
          <h2 
            data-testid="features-heading"
            className="text-4xl font-light text-center text-slate-900 mb-12" 
            style={{fontFamily: 'Merriweather, serif'}}
          >
            Intelligent Workflow Process
          </h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            <Card className="bg-white border border-stone-100 shadow-sm hover:shadow-md transition-all duration-300">
              <CardContent className="p-8">
                <FileCheck className="w-12 h-12 text-amber-600 mb-4" />
                <h3 className="text-xl font-semibold mb-3">Application Intake</h3>
                <p className="text-slate-600">Automated data extraction and validation from submitted applications.</p>
              </CardContent>
            </Card>

            <Card className="bg-white border border-stone-100 shadow-sm hover:shadow-md transition-all duration-300">
              <CardContent className="p-8">
                <CheckCircle className="w-12 h-12 text-amber-600 mb-4" />
                <h3 className="text-xl font-semibold mb-3">Document Verification</h3>
                <p className="text-slate-600">AI-powered document analysis with OCR and completeness checking.</p>
              </CardContent>
            </Card>

            <Card className="bg-white border border-stone-100 shadow-sm hover:shadow-md transition-all duration-300">
              <CardContent className="p-8">
                <Users className="w-12 h-12 text-amber-600 mb-4" />
                <h3 className="text-xl font-semibold mb-3">Eligibility Screening</h3>
                <p className="text-slate-600">Smart evaluation based on GPA, test scores, and program requirements.</p>
              </CardContent>
            </Card>

            <Card className="bg-white border border-stone-100 shadow-sm hover:shadow-md transition-all duration-300">
              <CardContent className="p-8">
                <Calendar className="w-12 h-12 text-amber-600 mb-4" />
                <h3 className="text-xl font-semibold mb-3">Interview Scheduling</h3>
                <p className="text-slate-600">Automated calendar integration for seamless interview booking.</p>
              </CardContent>
            </Card>

            <Card className="bg-white border border-stone-100 shadow-sm hover:shadow-md transition-all duration-300">
              <CardContent className="p-8">
                <GraduationCap className="w-12 h-12 text-amber-600 mb-4" />
                <h3 className="text-xl font-semibold mb-3">Decision Agent</h3>
                <p className="text-slate-600">AI-assisted decision making with transparent reasoning.</p>
              </CardContent>
            </Card>

            <Card className="bg-white border border-stone-100 shadow-sm hover:shadow-md transition-all duration-300">
              <CardContent className="p-8">
                <Mail className="w-12 h-12 text-amber-600 mb-4" />
                <h3 className="text-xl font-semibold mb-3">Offer Dispatch</h3>
                <p className="text-slate-600">Automated offer letter generation and email distribution.</p>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-6">
        <div className="max-w-4xl mx-auto text-center">
          <h2 
            data-testid="cta-heading"
            className="text-4xl font-light text-slate-900 mb-6" 
            style={{fontFamily: 'Merriweather, serif'}}
          >
            Ready to Begin Your Journey?
          </h2>
          <p className="text-lg text-slate-600 mb-8">
            Start your application today and experience the most advanced admissions process.
          </p>
          <Link to="/apply">
            <Button 
              data-testid="start-application-btn"
              className="bg-amber-600 text-white hover:bg-amber-700 shadow-sm rounded-full px-10 py-6 text-lg font-medium transition-all hover:scale-105"
            >
              Start Your Application
            </Button>
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-slate-900 text-white py-12 px-6">
        <div className="max-w-7xl mx-auto text-center">
          <div className="flex items-center justify-center gap-2 mb-4">
            <GraduationCap className="w-6 h-6" />
            <span className="text-lg font-bold" style={{fontFamily: 'Merriweather, serif'}}>EduFlow</span>
          </div>
          <p className="text-slate-400">
            AI-Powered University Administration Workflow System
          </p>
          <p className="text-slate-500 text-sm mt-4">
            &copy; 2026 EduFlow. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  );
}