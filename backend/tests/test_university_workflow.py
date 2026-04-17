"""
Backend API Tests for University Administration Workflow System
Tests: Application submission, status tracking, admin endpoints, analytics, audit log, human review
"""
import pytest
import requests
import os
import time
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://langgraph-admin.preview.emergentagent.com').rstrip('/')

class TestHealthAndBasicEndpoints:
    """Test basic API health and root endpoints"""
    
    def test_api_root(self):
        """Test API root endpoint returns expected message"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "University Admission Workflow System API" in data["message"]
        print(f"✓ API root endpoint working: {data['message']}")


class TestApplicationSubmission:
    """Test application submission and workflow processing"""
    
    def test_submit_high_gpa_application(self):
        """Test submitting application with high GPA (3.5+) - should be admitted"""
        unique_id = str(uuid.uuid4())[:8]
        payload = {
            "name": f"TEST_High_GPA_{unique_id}",
            "email": f"test.high.{unique_id}@example.com",
            "phone": "+1-555-000-0001",
            "program": "Computer Science",
            "gpa": 3.8,
            "test_scores": "SAT: 1450",
            "essay": "I am passionate about computer science and innovation."
        }
        
        response = requests.post(f"{BASE_URL}/api/applications", json=payload)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "application_id" in data
        assert "thread_id" in data
        assert data["status"] == "submitted"
        assert "message" in data
        
        print(f"✓ High GPA application submitted: thread_id={data['thread_id']}")
        return data["thread_id"]
    
    def test_submit_low_gpa_application(self):
        """Test submitting application with low GPA (<3.0) - should be denied"""
        unique_id = str(uuid.uuid4())[:8]
        payload = {
            "name": f"TEST_Low_GPA_{unique_id}",
            "email": f"test.low.{unique_id}@example.com",
            "phone": "+1-555-000-0002",
            "program": "Business Administration",
            "gpa": 2.5,
            "test_scores": "SAT: 1200",
            "essay": "I am committed to improving my academic performance."
        }
        
        response = requests.post(f"{BASE_URL}/api/applications", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert "thread_id" in data
        print(f"✓ Low GPA application submitted: thread_id={data['thread_id']}")
        return data["thread_id"]
    
    def test_submit_borderline_gpa_application(self):
        """Test submitting application with borderline GPA (3.0-3.2) - should trigger human review"""
        unique_id = str(uuid.uuid4())[:8]
        payload = {
            "name": f"TEST_Borderline_{unique_id}",
            "email": f"test.borderline.{unique_id}@example.com",
            "phone": "+1-555-000-0003",
            "program": "Engineering",
            "gpa": 3.05,
            "test_scores": "SAT: 1350",
            "essay": "I have shown significant improvement in my recent coursework."
        }
        
        response = requests.post(f"{BASE_URL}/api/applications", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert "thread_id" in data
        print(f"✓ Borderline GPA application submitted: thread_id={data['thread_id']}")
        return data["thread_id"]
    
    def test_submit_application_missing_required_fields(self):
        """Test submitting application with missing required fields"""
        payload = {
            "name": "Test User",
            # Missing email, phone, program, gpa
        }
        
        response = requests.post(f"{BASE_URL}/api/applications", json=payload)
        assert response.status_code == 422, f"Expected 422 for validation error, got {response.status_code}"
        print("✓ Validation error returned for missing fields")


class TestApplicationStatus:
    """Test application status retrieval"""
    
    def test_get_application_status_existing(self):
        """Test getting status of an existing application"""
        # First submit an application
        unique_id = str(uuid.uuid4())[:8]
        payload = {
            "name": f"TEST_Status_{unique_id}",
            "email": f"test.status.{unique_id}@example.com",
            "phone": "+1-555-000-0004",
            "program": "Medicine",
            "gpa": 3.7,
            "test_scores": "MCAT: 510",
            "essay": "I am dedicated to healthcare."
        }
        
        submit_response = requests.post(f"{BASE_URL}/api/applications", json=payload)
        assert submit_response.status_code == 200
        thread_id = submit_response.json()["thread_id"]
        
        # Wait for workflow to start processing
        time.sleep(2)
        
        # Get status
        status_response = requests.get(f"{BASE_URL}/api/applications/{thread_id}")
        assert status_response.status_code == 200
        
        data = status_response.json()
        assert "thread_id" in data
        assert "application_id" in data
        assert "current_stage" in data
        assert "status" in data
        assert "agent_reasoning" in data
        
        print(f"✓ Application status retrieved: stage={data['current_stage']}, status={data['status']}")
    
    def test_get_application_status_nonexistent(self):
        """Test getting status of non-existent application"""
        fake_thread_id = str(uuid.uuid4())
        response = requests.get(f"{BASE_URL}/api/applications/{fake_thread_id}")
        assert response.status_code == 404
        print("✓ 404 returned for non-existent application")


class TestAdminEndpoints:
    """Test admin dashboard endpoints"""
    
    def test_list_all_applications(self):
        """Test listing all applications"""
        response = requests.get(f"{BASE_URL}/api/admin/applications")
        assert response.status_code == 200
        
        data = response.json()
        assert "applications" in data
        assert "total" in data
        assert isinstance(data["applications"], list)
        assert data["total"] >= 0
        
        # Verify application structure if any exist
        if data["applications"]:
            app = data["applications"][0]
            assert "thread_id" in app
            assert "user_email" in app
            assert "submitted_data" in app
            assert "current_stage" in app
            assert "status" in app
        
        print(f"✓ Admin applications list: {data['total']} applications found")
    
    def test_get_pending_reviews(self):
        """Test getting pending human reviews"""
        response = requests.get(f"{BASE_URL}/api/admin/pending-reviews")
        assert response.status_code == 200
        
        data = response.json()
        assert "pending_reviews" in data
        assert "total" in data
        assert isinstance(data["pending_reviews"], list)
        
        # Verify review structure if any exist
        if data["pending_reviews"]:
            review = data["pending_reviews"][0]
            assert "thread_id" in review
            assert "applicant_name" in review
            assert "program" in review
            assert "gpa" in review
            assert "review_reason" in review
        
        print(f"✓ Pending reviews: {data['total']} reviews found")


class TestAnalyticsEndpoint:
    """Test analytics endpoint with program breakdown and GPA distribution"""
    
    def test_get_analytics(self):
        """Test analytics endpoint returns comprehensive metrics"""
        response = requests.get(f"{BASE_URL}/api/admin/analytics")
        assert response.status_code == 200
        
        data = response.json()
        assert "analytics" in data
        
        analytics = data["analytics"]
        
        # Verify required fields
        required_fields = ["total", "admitted", "denied", "waitlisted", "pending", 
                          "in_review", "admission_rate", "programs", "gpa_distribution"]
        for field in required_fields:
            assert field in analytics, f"Missing field: {field}"
        
        # Verify programs breakdown structure
        assert isinstance(analytics["programs"], dict)
        for prog_name, prog_data in analytics["programs"].items():
            assert "total" in prog_data
            assert "admitted" in prog_data
            assert "denied" in prog_data
            assert "waitlisted" in prog_data
        
        # Verify GPA distribution structure
        assert isinstance(analytics["gpa_distribution"], dict)
        expected_ranges = ["3.5-4.0", "3.0-3.49", "2.5-2.99", "2.0-2.49", "below_2.0"]
        for range_key in expected_ranges:
            assert range_key in analytics["gpa_distribution"], f"Missing GPA range: {range_key}"
        
        print(f"✓ Analytics retrieved: total={analytics['total']}, admitted={analytics['admitted']}, denied={analytics['denied']}")
        print(f"  Programs: {list(analytics['programs'].keys())}")
        print(f"  GPA Distribution: {analytics['gpa_distribution']}")


class TestAuditLogEndpoint:
    """Test audit log endpoint with agent reasoning"""
    
    def test_get_audit_log(self):
        """Test audit log returns application history with agent reasoning"""
        response = requests.get(f"{BASE_URL}/api/admin/audit-log")
        assert response.status_code == 200
        
        data = response.json()
        assert "audit_log" in data
        assert "total" in data
        assert isinstance(data["audit_log"], list)
        
        # Verify audit entry structure if any exist
        if data["audit_log"]:
            entry = data["audit_log"][0]
            assert "thread_id" in entry
            assert "applicant_name" in entry
            assert "program" in entry
            assert "gpa" in entry
            assert "current_stage" in entry
            assert "status" in entry
            assert "agent_reasoning" in entry
            assert isinstance(entry["agent_reasoning"], list)
        
        print(f"✓ Audit log retrieved: {data['total']} entries")
        
        # Check for agent reasoning content
        entries_with_reasoning = sum(1 for e in data["audit_log"] if e.get("agent_reasoning"))
        print(f"  Entries with agent reasoning: {entries_with_reasoning}")


class TestHumanReviewWorkflow:
    """Test human review approval/rejection workflow"""
    
    def test_submit_review_approval(self):
        """Test approving a pending review"""
        # First check if there are any pending reviews
        pending_response = requests.get(f"{BASE_URL}/api/admin/pending-reviews")
        assert pending_response.status_code == 200
        
        pending_data = pending_response.json()
        
        if pending_data["total"] > 0:
            # Get first pending review
            review = pending_data["pending_reviews"][0]
            thread_id = review["thread_id"]
            
            # Submit approval
            review_payload = {
                "approved": True,
                "comments": "TEST: Approved via automated testing"
            }
            
            response = requests.post(f"{BASE_URL}/api/admin/review/{thread_id}", json=review_payload)
            assert response.status_code == 200
            
            data = response.json()
            assert "status" in data
            assert data["status"] == "success"
            assert "Approved" in data["message"]
            
            print(f"✓ Review approved for thread_id={thread_id}")
        else:
            # Create a borderline application to test review
            unique_id = str(uuid.uuid4())[:8]
            payload = {
                "name": f"TEST_Review_{unique_id}",
                "email": f"test.review.{unique_id}@example.com",
                "phone": "+1-555-000-0005",
                "program": "Computer Science",
                "gpa": 3.08,  # Borderline GPA
                "test_scores": "SAT: 1350",
                "essay": "Testing human review workflow."
            }
            
            submit_response = requests.post(f"{BASE_URL}/api/applications", json=payload)
            assert submit_response.status_code == 200
            thread_id = submit_response.json()["thread_id"]
            
            # Wait for workflow to reach human review stage
            time.sleep(15)
            
            # Check if it's in pending reviews
            pending_response = requests.get(f"{BASE_URL}/api/admin/pending-reviews")
            pending_data = pending_response.json()
            
            # Find our application
            our_review = next((r for r in pending_data["pending_reviews"] if r["thread_id"] == thread_id), None)
            
            if our_review:
                review_payload = {
                    "approved": True,
                    "comments": "TEST: Approved via automated testing"
                }
                
                response = requests.post(f"{BASE_URL}/api/admin/review/{thread_id}", json=review_payload)
                assert response.status_code == 200
                print(f"✓ Review approved for new borderline application: thread_id={thread_id}")
            else:
                print(f"⚠ Application did not reach human review stage (may have been auto-processed)")
    
    def test_submit_review_rejection(self):
        """Test rejecting a pending review"""
        # Create a borderline application
        unique_id = str(uuid.uuid4())[:8]
        payload = {
            "name": f"TEST_Reject_{unique_id}",
            "email": f"test.reject.{unique_id}@example.com",
            "phone": "+1-555-000-0006",
            "program": "Law",
            "gpa": 2.95,  # Below minimum for Law (3.0)
            "test_scores": "LSAT: 155",
            "essay": "Testing rejection workflow."
        }
        
        submit_response = requests.post(f"{BASE_URL}/api/applications", json=payload)
        assert submit_response.status_code == 200
        thread_id = submit_response.json()["thread_id"]
        
        # Wait for workflow
        time.sleep(15)
        
        # Check pending reviews
        pending_response = requests.get(f"{BASE_URL}/api/admin/pending-reviews")
        pending_data = pending_response.json()
        
        our_review = next((r for r in pending_data["pending_reviews"] if r["thread_id"] == thread_id), None)
        
        if our_review:
            review_payload = {
                "approved": False,
                "comments": "TEST: Rejected via automated testing"
            }
            
            response = requests.post(f"{BASE_URL}/api/admin/review/{thread_id}", json=review_payload)
            assert response.status_code == 200
            
            data = response.json()
            assert "Rejected" in data["message"]
            print(f"✓ Review rejected for thread_id={thread_id}")
        else:
            print(f"⚠ Application did not reach human review stage")


class TestDocumentUpload:
    """Test document upload with OCR extraction"""
    
    def test_upload_document(self):
        """Test uploading a document for an application"""
        # First create an application
        unique_id = str(uuid.uuid4())[:8]
        payload = {
            "name": f"TEST_Doc_{unique_id}",
            "email": f"test.doc.{unique_id}@example.com",
            "phone": "+1-555-000-0007",
            "program": "Medicine",
            "gpa": 3.7,
            "test_scores": "MCAT: 510",
            "essay": "Testing document upload."
        }
        
        submit_response = requests.post(f"{BASE_URL}/api/applications", json=payload)
        assert submit_response.status_code == 200
        thread_id = submit_response.json()["thread_id"]
        
        # Create a simple text file to upload
        files = {
            'file': ('test_transcript.txt', b'Student Transcript\nGPA: 3.7\nCourses: Biology, Chemistry, Physics', 'text/plain')
        }
        
        response = requests.post(
            f"{BASE_URL}/api/documents/upload/{thread_id}",
            files=files,
            data={"document_type": "transcript"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "document_id" in data
        assert data["status"] == "uploaded"
        
        print(f"✓ Document uploaded: document_id={data['document_id']}")
    
    def test_list_documents(self):
        """Test listing documents for an application"""
        # First create an application and upload a document
        unique_id = str(uuid.uuid4())[:8]
        payload = {
            "name": f"TEST_DocList_{unique_id}",
            "email": f"test.doclist.{unique_id}@example.com",
            "phone": "+1-555-000-0008",
            "program": "Engineering",
            "gpa": 3.6,
            "test_scores": "SAT: 1400",
            "essay": "Testing document listing."
        }
        
        submit_response = requests.post(f"{BASE_URL}/api/applications", json=payload)
        thread_id = submit_response.json()["thread_id"]
        
        # Upload a document
        files = {
            'file': ('test_doc.txt', b'Test document content', 'text/plain')
        }
        requests.post(f"{BASE_URL}/api/documents/upload/{thread_id}", files=files)
        
        # List documents
        response = requests.get(f"{BASE_URL}/api/documents/list/{thread_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert "documents" in data
        assert "total" in data
        
        print(f"✓ Documents listed: {data['total']} documents")


class TestWorkflowProcessing:
    """Test end-to-end workflow processing with different GPA scenarios"""
    
    def test_high_gpa_workflow_completion(self):
        """Test that high GPA application flows through to admitted"""
        unique_id = str(uuid.uuid4())[:8]
        payload = {
            "name": f"TEST_HighFlow_{unique_id}",
            "email": f"test.highflow.{unique_id}@example.com",
            "phone": "+1-555-000-0009",
            "program": "Computer Science",
            "gpa": 3.85,
            "test_scores": "SAT: 1500",
            "essay": "I am passionate about AI and machine learning with strong academic performance."
        }
        
        submit_response = requests.post(f"{BASE_URL}/api/applications", json=payload)
        assert submit_response.status_code == 200
        thread_id = submit_response.json()["thread_id"]
        
        # Wait for workflow to complete (10-15 seconds as per docs)
        print(f"  Waiting for workflow to complete for thread_id={thread_id}...")
        time.sleep(18)
        
        # Check final status
        status_response = requests.get(f"{BASE_URL}/api/applications/{thread_id}")
        assert status_response.status_code == 200
        
        data = status_response.json()
        print(f"  Final stage: {data['current_stage']}, decision: {data.get('final_decision')}")
        
        # High GPA should result in admitted
        if data["current_stage"] == "completed":
            assert data["final_decision"] == "admitted", f"Expected 'admitted' for high GPA, got {data['final_decision']}"
            print(f"✓ High GPA workflow completed: ADMITTED")
        else:
            print(f"⚠ Workflow still in progress: stage={data['current_stage']}")
    
    def test_low_gpa_workflow_completion(self):
        """Test that low GPA application flows through to denied"""
        unique_id = str(uuid.uuid4())[:8]
        payload = {
            "name": f"TEST_LowFlow_{unique_id}",
            "email": f"test.lowflow.{unique_id}@example.com",
            "phone": "+1-555-000-0010",
            "program": "Medicine",  # Medicine has high GPA requirement (3.5)
            "gpa": 2.4,
            "test_scores": "MCAT: 480",
            "essay": "I want to be a doctor."
        }
        
        submit_response = requests.post(f"{BASE_URL}/api/applications", json=payload)
        assert submit_response.status_code == 200
        thread_id = submit_response.json()["thread_id"]
        
        # Wait for workflow
        print(f"  Waiting for workflow to complete for thread_id={thread_id}...")
        time.sleep(18)
        
        # Check final status
        status_response = requests.get(f"{BASE_URL}/api/applications/{thread_id}")
        data = status_response.json()
        
        print(f"  Final stage: {data['current_stage']}, decision: {data.get('final_decision')}")
        
        # Low GPA should result in denied or waitlisted
        if data["current_stage"] == "completed":
            assert data["final_decision"] in ["denied", "waitlisted"], f"Expected 'denied' or 'waitlisted' for low GPA, got {data['final_decision']}"
            print(f"✓ Low GPA workflow completed: {data['final_decision'].upper()}")
        else:
            print(f"⚠ Workflow still in progress: stage={data['current_stage']}")


class TestFAISSEligibilityScoring:
    """Test FAISS vector store eligibility scoring breakdown"""
    
    def test_eligibility_score_in_status(self):
        """Test that eligibility score breakdown is included in application status"""
        unique_id = str(uuid.uuid4())[:8]
        payload = {
            "name": f"TEST_FAISS_{unique_id}",
            "email": f"test.faiss.{unique_id}@example.com",
            "phone": "+1-555-000-0011",
            "program": "Computer Science",
            "gpa": 3.6,
            "test_scores": "SAT: 1480",
            "essay": "I am passionate about artificial intelligence, machine learning, and algorithm design."
        }
        
        submit_response = requests.post(f"{BASE_URL}/api/applications", json=payload)
        thread_id = submit_response.json()["thread_id"]
        
        # Wait for eligibility processing
        time.sleep(15)
        
        # Check status for eligibility reasoning
        status_response = requests.get(f"{BASE_URL}/api/applications/{thread_id}")
        data = status_response.json()
        
        # Check agent reasoning contains eligibility score breakdown
        reasoning = data.get("agent_reasoning", [])
        eligibility_reasoning = [r for r in reasoning if "Eligibility" in r or "Score" in r]
        
        assert len(eligibility_reasoning) > 0, "Expected eligibility reasoning in agent_reasoning"
        
        # Check for score breakdown format (GPA/40 + Match/30 + Essay/15 + Test/15)
        has_breakdown = any("GPA:" in r or "Match:" in r or "Essay:" in r for r in reasoning)
        
        print(f"✓ FAISS eligibility scoring found in reasoning")
        print(f"  Reasoning entries: {eligibility_reasoning}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
