import requests
import sys
import json
import time
from datetime import datetime

class UniversityAdmissionAPITester:
    def __init__(self, base_url="https://eduflow-orchestr.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.application_data = []

    def run_test(self, name, method, endpoint, expected_status, data=None, timeout=30):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}" if not endpoint.startswith('http') else endpoint
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=timeout)
            elif method == 'POST':
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

    def test_root_endpoint(self):
        """Test the root API endpoint"""
        return self.run_test("Root API Endpoint", "GET", "", 200)

    def test_submit_application_high_gpa(self):
        """Test submitting application with high GPA (>= 3.0)"""
        test_data = {
            "name": "Test Student High GPA",
            "email": "test.high@example.com",
            "phone": "+1-555-000-0001",
            "program": "Computer Science",
            "gpa": 3.8,
            "test_scores": "SAT: 1450",
            "essay": "I am passionate about computer science and innovation."
        }
        
        success, response = self.run_test(
            "Submit Application (High GPA)",
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
                'type': 'high_gpa'
            })
            return True, response
        return False, {}

    def test_submit_application_low_gpa(self):
        """Test submitting application with low GPA (< 3.0)"""
        test_data = {
            "name": "Test Student Low GPA",
            "email": "test.low@example.com", 
            "phone": "+1-555-000-0002",
            "program": "Business Administration",
            "gpa": 2.5,
            "test_scores": "SAT: 1200",
            "essay": "I am committed to improving my academic performance."
        }
        
        success, response = self.run_test(
            "Submit Application (Low GPA)",
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
                'type': 'low_gpa'
            })
            return True, response
        return False, {}

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

    def test_workflow_execution(self):
        """Test workflow execution by checking application progress"""
        print("\n🔄 Testing Workflow Execution...")
        
        if not self.application_data:
            print("❌ No applications to test workflow execution")
            return False
        
        # Wait for workflow to process
        print("⏳ Waiting 10 seconds for workflow processing...")
        time.sleep(10)
        
        workflow_success = True
        
        for app in self.application_data:
            print(f"\n📊 Checking workflow progress for {app['type']} application...")
            success, response = self.test_get_application_status(app['thread_id'], app['type'])
            
            if success:
                current_stage = response.get('current_stage', 'unknown')
                status = response.get('status', 'unknown')
                agent_reasoning = response.get('agent_reasoning', [])
                
                print(f"Current Stage: {current_stage}")
                print(f"Status: {status}")
                print(f"Agent Reasoning Steps: {len(agent_reasoning)}")
                
                # Check if workflow progressed beyond intake
                if current_stage == 'intake' and len(agent_reasoning) == 0:
                    print(f"⚠️  Workflow may not be executing properly for {app['type']}")
                    workflow_success = False
                else:
                    print(f"✅ Workflow is progressing for {app['type']}")
            else:
                workflow_success = False
        
        return workflow_success

def main():
    print("🎓 University Admission Workflow System - API Testing")
    print("=" * 60)
    
    tester = UniversityAdmissionAPITester()
    
    # Test basic connectivity
    print("\n📡 Testing Basic Connectivity...")
    success, _ = tester.test_root_endpoint()
    if not success:
        print("❌ Cannot connect to API. Stopping tests.")
        return 1
    
    # Test application submissions
    print("\n📝 Testing Application Submissions...")
    tester.test_submit_application_high_gpa()
    tester.test_submit_application_low_gpa()
    
    # Test workflow execution
    tester.test_workflow_execution()
    
    # Test admin endpoint
    print("\n👨‍💼 Testing Admin Endpoints...")
    tester.test_admin_applications()
    
    # Print final results
    print("\n" + "=" * 60)
    print(f"📊 Final Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())