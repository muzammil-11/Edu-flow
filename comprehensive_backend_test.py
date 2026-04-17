import requests
import sys
import json
import time
import io
from datetime import datetime

class ComprehensiveUniversityAdmissionTester:
    def __init__(self, base_url="https://langgraph-admin.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.application_data = []
        self.borderline_thread_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None, files=None, timeout=30):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}" if not endpoint.startswith('http') else endpoint
        headers = {}
        if not files:
            headers['Content-Type'] = 'application/json'

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=timeout)
            elif method == 'POST':
                if files:
                    response = requests.post(url, files=files, data=data, timeout=timeout)
                else:
                    response = requests.post(url, json=data, headers=headers, timeout=timeout)

            print(f"Response Status: {response.status_code}")
            
            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"Response: {json.dumps(response_data, indent=2)}")
                    return True, response_data
                except:
                    return True, response.text
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"Error Response: {json.dumps(error_data, indent=2)}")
                except:
                    print(f"Error Response: {response.text}")
                return False, {}

        except requests.exceptions.Timeout:
            print(f"❌ Failed - Request timeout after {timeout} seconds")
            return False, {}
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_submit_borderline_application(self):
        """Test submitting application with borderline GPA (3.08) for human review"""
        test_data = {
            "name": "Borderline Test Student",
            "email": "borderline.test@example.com",
            "phone": "+1-555-000-0003",
            "program": "Computer Science",
            "gpa": 3.08,
            "test_scores": "SAT: 1350",
            "essay": "I have shown significant improvement in my recent coursework and am passionate about computer science."
        }
        
        success, response = self.run_test(
            "Submit Borderline Application (GPA 3.08)",
            "POST",
            "applications",
            200,
            data=test_data
        )
        
        if success and 'thread_id' in response:
            self.borderline_thread_id = response['thread_id']
            self.application_data.append({
                'thread_id': response['thread_id'],
                'application_id': response['application_id'],
                'gpa': test_data['gpa'],
                'type': 'borderline_gpa'
            })
            return True, response
        return False, {}

    def test_submit_high_gpa_application(self):
        """Test submitting application with high GPA (3.75) for complete workflow"""
        test_data = {
            "name": "High GPA Test Student",
            "email": "highgpa.test@example.com",
            "phone": "+1-555-000-0004",
            "program": "Engineering",
            "gpa": 3.75,
            "test_scores": "SAT: 1500",
            "essay": "I am passionate about engineering and innovation with strong academic performance."
        }
        
        success, response = self.run_test(
            "Submit High GPA Application (GPA 3.75)",
            "POST",
            "applications",
            200,
            data=test_data
        )
        
        if success and 'thread_id' in response:
            self.application_data.append({
                'thread_id': response['thread_id'],
                'application_id': response['application_id'],
                'gpa': test_data['gpa'],
                'type': 'high_gpa_complete'
            })
            return True, response
        return False, {}

    def test_document_upload(self, thread_id):
        """Test document upload functionality"""
        # Create a mock PDF content
        pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n>>\nendobj\nxref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n0000000074 00000 n \n0000000120 00000 n \ntrailer\n<<\n/Size 4\n/Root 1 0 R\n>>\nstartxref\n179\n%%EOF"
        
        files = {
            'file': ('transcript.pdf', io.BytesIO(pdf_content), 'application/pdf')
        }
        data = {
            'document_type': 'transcript'
        }
        
        success, response = self.run_test(
            f"Upload Document for {thread_id}",
            "POST",
            f"documents/upload/{thread_id}",
            200,
            data=data,
            files=files
        )
        return success, response

    def test_list_documents(self, thread_id):
        """Test listing documents for an application"""
        success, response = self.run_test(
            f"List Documents for {thread_id}",
            "GET",
            f"documents/list/{thread_id}",
            200
        )
        return success, response

    def test_pending_reviews(self):
        """Test getting pending reviews"""
        success, response = self.run_test(
            "Get Pending Reviews",
            "GET",
            "admin/pending-reviews",
            200
        )
        return success, response

    def test_submit_review_decision(self, thread_id, approved=True, comments="Test approval"):
        """Test submitting review decision"""
        decision_data = {
            "approved": approved,
            "comments": comments
        }
        
        success, response = self.run_test(
            f"Submit Review Decision for {thread_id}",
            "POST",
            f"admin/review/{thread_id}",
            200,
            data=decision_data
        )
        return success, response

    def test_get_application_status(self, thread_id, app_type):
        """Test getting application status"""
        success, response = self.run_test(
            f"Get Application Status ({app_type})",
            "GET",
            f"applications/{thread_id}",
            200
        )
        return success, response

    def test_admin_applications(self):
        """Test admin endpoint to list all applications"""
        return self.run_test(
            "Admin - List All Applications",
            "GET",
            "admin/applications",
            200
        )

    def wait_for_human_review_stage(self, thread_id, max_wait=30):
        """Wait for application to reach human review stage"""
        print(f"⏳ Waiting for application {thread_id} to reach human review stage...")
        
        for i in range(max_wait):
            success, response = self.test_get_application_status(thread_id, "borderline")
            if success:
                current_stage = response.get('current_stage', '')
                status = response.get('status', '')
                
                if current_stage == 'human_review' or status == 'pending_review':
                    print(f"✅ Application reached human review stage after {i+1} seconds")
                    return True
                
                print(f"Current stage: {current_stage}, Status: {status}")
            
            time.sleep(1)
        
        print(f"❌ Application did not reach human review stage within {max_wait} seconds")
        return False

    def wait_for_workflow_completion(self, thread_id, max_wait=30):
        """Wait for workflow to complete"""
        print(f"⏳ Waiting for workflow completion for {thread_id}...")
        
        for i in range(max_wait):
            success, response = self.test_get_application_status(thread_id, "workflow")
            if success:
                current_stage = response.get('current_stage', '')
                status = response.get('status', '')
                final_decision = response.get('final_decision')
                
                if current_stage == 'completed' or status == 'completed' or final_decision:
                    print(f"✅ Workflow completed after {i+1} seconds")
                    print(f"Final Decision: {final_decision}")
                    return True, final_decision
                
                print(f"Current stage: {current_stage}, Status: {status}")
            
            time.sleep(1)
        
        print(f"❌ Workflow did not complete within {max_wait} seconds")
        return False, None

def main():
    print("🎓 Comprehensive University Admission Workflow System Testing")
    print("=" * 70)
    
    tester = ComprehensiveUniversityAdmissionTester()
    
    # Test 1: Document Upload Flow
    print("\n📄 Testing Document Upload Flow...")
    
    # First submit an application to get a thread_id
    success, response = tester.test_submit_high_gpa_application()
    if success:
        thread_id = response['thread_id']
        
        # Test document upload
        tester.test_document_upload(thread_id)
        
        # Test document listing
        tester.test_list_documents(thread_id)
    
    # Test 2: Human Review Workflow
    print("\n👨‍💼 Testing Human Review Workflow...")
    
    # Submit borderline application
    success, response = tester.test_submit_borderline_application()
    if success and tester.borderline_thread_id:
        # Wait for workflow to pause at human review
        if tester.wait_for_human_review_stage(tester.borderline_thread_id):
            # Check pending reviews
            tester.test_pending_reviews()
            
            # Submit approval decision
            tester.test_submit_review_decision(tester.borderline_thread_id, approved=True, comments="Approved after review")
            
            # Wait for workflow to resume and complete
            tester.wait_for_workflow_completion(tester.borderline_thread_id)
    
    # Test 3: Complete End-to-End Workflow
    print("\n🔄 Testing Complete End-to-End Workflow...")
    
    # Submit high GPA application
    success, response = tester.test_submit_high_gpa_application()
    if success:
        thread_id = response['thread_id']
        
        # Wait for completion and check final decision
        completed, final_decision = tester.wait_for_workflow_completion(thread_id)
        if completed:
            print(f"Expected 'admitted' decision, got: {final_decision}")
    
    # Test 4: Admin Dashboard
    print("\n📊 Testing Admin Dashboard...")
    tester.test_admin_applications()
    tester.test_pending_reviews()
    
    # Print final results
    print("\n" + "=" * 70)
    print(f"📊 Final Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All comprehensive tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())