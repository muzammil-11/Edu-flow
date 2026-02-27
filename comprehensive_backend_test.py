import requests
import sys
import json
import time
import io
from datetime import datetime

class ComprehensiveAPITester:
    def __init__(self, base_url="https://eduflow-orchestr.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.application_data = []

    def run_test(self, name, method, endpoint, expected_status, data=None, files=None, timeout=30):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}" if not endpoint.startswith('http') else endpoint
        headers = {'Content-Type': 'application/json'} if not files else {}

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

    def test_complete_workflow_high_gpa(self):
        """Test Case 1: Complete Workflow Test (High GPA)"""
        print("\n" + "="*60)
        print("TEST CASE 1: Complete Workflow Test (High GPA)")
        print("="*60)
        
        test_data = {
            "name": "High GPA Student",
            "email": "highgpa@test.com",
            "phone": "+1-555-111-1111",
            "program": "Computer Science",
            "gpa": 3.8,
            "test_scores": "SAT: 1500",
            "essay": "I am passionate about technology and innovation."
        }
        
        success, response = self.run_test(
            "Submit Application (High GPA)",
            "POST",
            "applications",
            200,
            data=test_data
        )
        
        if success and 'thread_id' in response:
            thread_id = response['thread_id']
            self.application_data.append({
                'thread_id': thread_id,
                'application_id': response['application_id'],
                'gpa': test_data['gpa'],
                'type': 'high_gpa_workflow'
            })
            
            # Wait for workflow to complete
            print("⏳ Waiting 15 seconds for workflow to complete...")
            time.sleep(15)
            
            # Check final status
            success, status_response = self.run_test(
                "Check Final Status (High GPA)",
                "GET",
                f"applications/{thread_id}",
                200
            )
            
            if success:
                current_stage = status_response.get('current_stage')
                final_decision = status_response.get('final_decision')
                agent_reasoning = status_response.get('agent_reasoning', [])
                
                print(f"\n📊 Workflow Analysis:")
                print(f"Final Stage: {current_stage}")
                print(f"Final Decision: {final_decision}")
                print(f"Workflow Steps: {len(agent_reasoning)}")
                
                # Verify expected workflow progression
                expected_stages = ['intake', 'verification', 'eligibility', 'interview', 'decision', 'dispatch']
                workflow_valid = True
                
                if final_decision != 'admitted':
                    print(f"❌ Expected 'admitted', got '{final_decision}'")
                    workflow_valid = False
                
                if current_stage != 'completed':
                    print(f"❌ Expected 'completed', got '{current_stage}'")
                    workflow_valid = False
                
                if len(agent_reasoning) < 5:  # Should have multiple steps
                    print(f"❌ Expected multiple workflow steps, got {len(agent_reasoning)}")
                    workflow_valid = False
                
                if workflow_valid:
                    print("✅ High GPA workflow completed successfully")
                    self.tests_passed += 1
                else:
                    print("❌ High GPA workflow validation failed")
                
                self.tests_run += 1
                return workflow_valid
        
        return False

    def test_workflow_low_gpa(self):
        """Test Case 2: Workflow Test (Low GPA)"""
        print("\n" + "="*60)
        print("TEST CASE 2: Workflow Test (Low GPA)")
        print("="*60)
        
        test_data = {
            "name": "Low GPA Student",
            "email": "lowgpa@test.com",
            "phone": "+1-555-222-2222",
            "program": "Business Administration",
            "gpa": 2.5,
            "test_scores": "SAT: 1100",
            "essay": "I am committed to academic improvement."
        }
        
        success, response = self.run_test(
            "Submit Application (Low GPA)",
            "POST",
            "applications",
            200,
            data=test_data
        )
        
        if success and 'thread_id' in response:
            thread_id = response['thread_id']
            
            # Wait for workflow to complete
            print("⏳ Waiting 15 seconds for workflow to complete...")
            time.sleep(15)
            
            # Check final status
            success, status_response = self.run_test(
                "Check Final Status (Low GPA)",
                "GET",
                f"applications/{thread_id}",
                200
            )
            
            if success:
                current_stage = status_response.get('current_stage')
                final_decision = status_response.get('final_decision')
                agent_reasoning = status_response.get('agent_reasoning', [])
                
                print(f"\n📊 Workflow Analysis:")
                print(f"Final Stage: {current_stage}")
                print(f"Final Decision: {final_decision}")
                print(f"Workflow Steps: {len(agent_reasoning)}")
                
                # Verify expected workflow (should skip interview)
                workflow_valid = True
                
                if final_decision != 'denied':
                    print(f"❌ Expected 'denied', got '{final_decision}'")
                    workflow_valid = False
                
                # Check that interview was skipped (should go eligibility → decision)
                reasoning_text = ' '.join(agent_reasoning)
                if 'Interview:' in reasoning_text:
                    print(f"❌ Interview stage should be skipped for low GPA")
                    workflow_valid = False
                else:
                    print("✅ Interview stage correctly skipped for low GPA")
                
                if workflow_valid:
                    print("✅ Low GPA workflow completed successfully")
                    self.tests_passed += 1
                else:
                    print("❌ Low GPA workflow validation failed")
                
                self.tests_run += 1
                return workflow_valid
        
        return False

    def test_borderline_gpa_human_review(self):
        """Test Case 3: Borderline GPA Test (Human Review)"""
        print("\n" + "="*60)
        print("TEST CASE 3: Borderline GPA Test (Human Review)")
        print("="*60)
        
        test_data = {
            "name": "Borderline GPA Student",
            "email": "borderline@test.com",
            "phone": "+1-555-333-3333",
            "program": "Engineering",
            "gpa": 3.05,
            "test_scores": "SAT: 1350",
            "essay": "I have shown significant improvement in my recent coursework."
        }
        
        success, response = self.run_test(
            "Submit Application (Borderline GPA)",
            "POST",
            "applications",
            200,
            data=test_data
        )
        
        if success and 'thread_id' in response:
            thread_id = response['thread_id']
            
            # Wait for workflow to process
            print("⏳ Waiting 15 seconds for workflow to process...")
            time.sleep(15)
            
            # Check if requires human review
            success, status_response = self.run_test(
                "Check Status (Borderline GPA)",
                "GET",
                f"applications/{thread_id}",
                200
            )
            
            # Check pending reviews endpoint
            success_reviews, reviews_response = self.run_test(
                "Check Pending Reviews",
                "GET",
                "admin/pending-reviews",
                200
            )
            
            if success and success_reviews:
                # Look for our application in pending reviews
                pending_reviews = reviews_response.get('pending_reviews', [])
                found_review = False
                
                for review in pending_reviews:
                    if review.get('thread_id') == thread_id:
                        found_review = True
                        print(f"✅ Found application in pending reviews")
                        print(f"Review Reason: {review.get('review_reason')}")
                        break
                
                if found_review:
                    print("✅ Borderline GPA correctly flagged for human review")
                    self.tests_passed += 1
                else:
                    print("❌ Borderline GPA application not found in pending reviews")
                
                self.tests_run += 1
                return found_review
        
        return False

    def test_document_upload(self):
        """Test Case 4: Document Upload Test"""
        print("\n" + "="*60)
        print("TEST CASE 4: Document Upload Test")
        print("="*60)
        
        # First submit an application
        test_data = {
            "name": "Document Test Student",
            "email": "doctest@test.com",
            "phone": "+1-555-444-4444",
            "program": "Medicine",
            "gpa": 3.7,
            "test_scores": "MCAT: 510",
            "essay": "I am dedicated to healthcare."
        }
        
        success, response = self.run_test(
            "Submit Application for Document Test",
            "POST",
            "applications",
            200,
            data=test_data
        )
        
        if success and 'thread_id' in response:
            thread_id = response['thread_id']
            
            # Create a mock PDF file
            pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n>>\nendobj\nxref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n0000000074 00000 n \n0000000120 00000 n \ntrailer\n<<\n/Size 4\n/Root 1 0 R\n>>\nstartxref\n179\n%%EOF"
            
            # Upload document
            files = {
                'file': ('transcript.pdf', io.BytesIO(pdf_content), 'application/pdf')
            }
            data = {'document_type': 'transcript'}
            
            success, upload_response = self.run_test(
                "Upload Document",
                "POST",
                f"documents/upload/{thread_id}",
                200,
                data=data,
                files=files
            )
            
            if success:
                document_id = upload_response.get('document_id')
                print(f"Document ID: {document_id}")
                
                # List documents
                success, list_response = self.run_test(
                    "List Documents",
                    "GET",
                    f"documents/list/{thread_id}",
                    200
                )
                
                if success:
                    documents = list_response.get('documents', [])
                    found_document = False
                    
                    for doc in documents:
                        if doc.get('filename') == 'transcript.pdf':
                            found_document = True
                            print(f"✅ Document found in list: {doc.get('filename')}")
                            break
                    
                    if found_document:
                        print("✅ Document upload and listing successful")
                        self.tests_passed += 1
                    else:
                        print("❌ Uploaded document not found in list")
                    
                    self.tests_run += 1
                    return found_document
        
        return False

    def test_admin_endpoints(self):
        """Test admin dashboard endpoints"""
        print("\n" + "="*60)
        print("TEST CASE 5: Admin Dashboard Endpoints")
        print("="*60)
        
        # Test admin applications endpoint
        success1, _ = self.run_test(
            "Admin - List All Applications",
            "GET",
            "admin/applications",
            200
        )
        
        # Test pending reviews endpoint
        success2, _ = self.run_test(
            "Admin - Pending Reviews",
            "GET",
            "admin/pending-reviews",
            200
        )
        
        return success1 and success2

    def check_backend_logs(self):
        """Check for expected log messages"""
        print("\n" + "="*60)
        print("BACKEND LOGS CHECK")
        print("="*60)
        
        print("📧 Checking for email and calendar mock logs...")
        print("Note: This requires manual verification of backend logs")
        print("Expected log patterns:")
        print("- '📧 EMAIL SENT (MOCK)' messages")
        print("- '📅 CALENDAR EVENT CREATED (MOCK)' messages") 
        print("- 'Workflow completed' messages")
        
        # This would require access to backend logs which we can't directly test via API
        return True

def main():
    print("🎓 University Admission Workflow System - Comprehensive Testing")
    print("=" * 80)
    
    tester = ComprehensiveAPITester()
    
    # Test basic connectivity
    print("\n📡 Testing Basic Connectivity...")
    success, _ = tester.run_test("Root API Endpoint", "GET", "", 200)
    if not success:
        print("❌ Cannot connect to API. Stopping tests.")
        return 1
    
    # Run comprehensive test cases
    test_results = []
    
    # Test Case 1: High GPA Workflow
    result1 = tester.test_complete_workflow_high_gpa()
    test_results.append(("High GPA Workflow", result1))
    
    # Test Case 2: Low GPA Workflow  
    result2 = tester.test_workflow_low_gpa()
    test_results.append(("Low GPA Workflow", result2))
    
    # Test Case 3: Borderline GPA Human Review
    result3 = tester.test_borderline_gpa_human_review()
    test_results.append(("Borderline GPA Human Review", result3))
    
    # Test Case 4: Document Upload
    result4 = tester.test_document_upload()
    test_results.append(("Document Upload", result4))
    
    # Test Case 5: Admin Endpoints
    result5 = tester.test_admin_endpoints()
    test_results.append(("Admin Endpoints", result5))
    
    # Backend logs check
    tester.check_backend_logs()
    
    # Print comprehensive results
    print("\n" + "=" * 80)
    print("📊 COMPREHENSIVE TEST RESULTS")
    print("=" * 80)
    
    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nAPI Tests: {tester.tests_passed}/{tester.tests_run} passed")
    
    passed_comprehensive = sum(1 for _, result in test_results if result)
    total_comprehensive = len(test_results)
    
    print(f"Comprehensive Tests: {passed_comprehensive}/{total_comprehensive} passed")
    
    if passed_comprehensive == total_comprehensive and tester.tests_passed == tester.tests_run:
        print("\n🎉 All comprehensive tests passed!")
        return 0
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())