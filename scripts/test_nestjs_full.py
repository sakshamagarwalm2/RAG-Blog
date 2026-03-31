import requests
import time
import sys
import json
from typing import Optional

BASE_URL = "http://localhost:8000"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}{Colors.ENDC}")

def print_success(text: str):
    print(f"{Colors.GREEN}[PASS] {text}{Colors.ENDC}")

def print_error(text: str):
    print(f"{Colors.RED}[FAIL] {text}{Colors.ENDC}")

def print_warning(text: str):
    print(f"{Colors.YELLOW}[WARN] {text}{Colors.ENDC}")

def print_info(text: str):
    print(f"{Colors.BLUE}[INFO] {text}{Colors.ENDC}")

class BackendTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.created_blog_id: Optional[str] = None
        self.created_video_id: Optional[str] = None
        self.results = {
            "passed": 0,
            "failed": 0,
            "total": 0
        }
    
    def run_test(self, name: str, test_func):
        self.results["total"] += 1
        print_info(f"Testing: {name}")
        try:
            test_func()
            print_success(f"{name} - PASSED")
            self.results["passed"] += 1
            return True
        except AssertionError as e:
            print_error(f"{name} - FAILED: {e}")
            self.results["failed"] += 1
            return False
        except requests.exceptions.ConnectionError:
            print_error(f"{name} - FAILED: Cannot connect to server at {self.base_url}")
            self.results["failed"] += 1
            return False
        except Exception as e:
            print_error(f"{name} - FAILED: {type(e).__name__}: {e}")
            self.results["failed"] += 1
            return False
    
    def test_health(self):
        """Test GET /health"""
        resp = self.session.get(f"{self.base_url}/health")
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        data = resp.json()
        assert data.get("status") == "ok", f"Expected status 'ok', got {data.get('status')}"
        assert "message" in data, "Response missing 'message' field"
    
    def test_get_blogs(self):
        """Test GET /blogs"""
        resp = self.session.get(f"{self.base_url}/blogs")
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        data = resp.json()
        assert isinstance(data, list), f"Expected list, got {type(data)}"
        print_info(f"  Found {len(data)} blogs")
    
    def test_create_blog(self):
        """Test POST /blogs"""
        payload = {
            "title": "Automated Test Blog",
            "content": "This is a test blog created by the automated test suite. It contains sample content for testing the blog creation API endpoint.",
            "url": "https://example.com/test-blog-" + str(int(time.time())),
            "tags": ["test", "automated"]
        }
        resp = self.session.post(f"{self.base_url}/blogs", json=payload)
        assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"
        data = resp.json()
        assert "id" in data or "_id" in data, "Response missing 'id' field"
        self.created_blog_id = data.get("id") or data.get("_id")
        assert data.get("title") == payload["title"], f"Title mismatch"
        print_info(f"  Created blog with ID: {self.created_blog_id}")
    
    def test_delete_blog(self):
        """Test DELETE /blogs/:id"""
        if not self.created_blog_id:
            print_warning("  Skipping - no blog ID from create test")
            return
        
        resp = self.session.delete(f"{self.base_url}/blogs/{self.created_blog_id}")
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        data = resp.json()
        assert data.get("deleted") == True, f"Expected deleted=true, got {data}"
        print_info(f"  Deleted blog with ID: {self.created_blog_id}")
        self.created_blog_id = None
    
    def test_get_videos(self):
        """Test GET /videos"""
        resp = self.session.get(f"{self.base_url}/videos")
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        data = resp.json()
        assert isinstance(data, list), f"Expected list, got {type(data)}"
        print_info(f"  Found {len(data)} videos")
    
    def test_create_video_manual(self):
        """Test POST /videos/manual"""
        payload = {
            "youtube_url": "https://www.youtube.com/watch?v=test" + str(int(time.time())),
            "transcript_raw": "This is a test transcript for automated testing purposes.",
            "tags": ["test", "automated"]
        }
        resp = self.session.post(f"{self.base_url}/videos/manual", json=payload)
        assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"
        data = resp.json()
        assert "id" in data or "_id" in data, "Response missing 'id' field"
        self.created_video_id = data.get("id") or data.get("_id")
        print_info(f"  Created video with ID: {self.created_video_id}")
    
    def test_delete_video(self):
        """Test DELETE /videos/:id"""
        if not self.created_video_id:
            print_warning("  Skipping - no video ID from create test")
            return
        
        resp = self.session.delete(f"{self.base_url}/videos/{self.created_video_id}")
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        data = resp.json()
        assert data.get("deleted") == True, f"Expected deleted=true, got {data}"
        print_info(f"  Deleted video with ID: {self.created_video_id}")
        self.created_video_id = None
    
    def test_ingest_rebuild(self):
        """Test POST /ingest/rebuild"""
        print_warning("  This may take a while as it rebuilds the vector index...")
        resp = self.session.post(f"{self.base_url}/ingest/rebuild", timeout=120)
        assert resp.status_code in [200, 201], f"Expected 200/201, got {resp.status_code}: {resp.text}"
        print_info(f"  Ingest rebuild response: {resp.json()}")
    
    def test_chat(self):
        """Test POST /chat"""
        payload = {
            "query": "What is the test blog about?",
            "chat_history": []
        }
        resp = self.session.post(f"{self.base_url}/chat", json=payload, timeout=60)
        assert resp.status_code in [200, 201], f"Expected 200/201, got {resp.status_code}: {resp.text}"
        data = resp.json()
        assert "answer" in data, f"Response missing 'answer' field"
        assert len(data["answer"]) > 0, "Answer is empty"
        print_info(f"  Chat answer: {data['answer'][:100]}...")
    
    def test_nonexistent_endpoint(self):
        """Test GET /nonexistent - should return 404"""
        resp = self.session.get(f"{self.base_url}/nonexistent")
        assert resp.status_code == 404, f"Expected 404, got {resp.status_code}"
    
    def test_invalid_blog_delete(self):
        """Test DELETE /blogs/invalid-id - should return 404"""
        resp = self.session.delete(f"{self.base_url}/blogs/invalid-id-12345")
        assert resp.status_code == 404, f"Expected 404, got {resp.status_code}"
    
    def test_invalid_video_delete(self):
        """Test DELETE /videos/invalid-id - should return 404"""
        resp = self.session.delete(f"{self.base_url}/videos/invalid-id-12345")
        assert resp.status_code == 404, f"Expected 404, got {resp.status_code}"
    
    def run_all_tests(self):
        print_header("NestJS Backend API Test Suite")
        print_info(f"Target: {self.base_url}")
        print_info(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Health check first
        print_header("Health Check")
        self.run_test("GET /health", self.test_health)
        
        # Blog tests
        print_header("Blog Endpoints")
        self.run_test("GET /blogs", self.test_get_blogs)
        self.run_test("POST /blogs", self.test_create_blog)
        self.run_test("DELETE /blogs/:id", self.test_delete_blog)
        self.run_test("DELETE /blogs/invalid-id (404)", self.test_invalid_blog_delete)
        
        # Video tests
        print_header("Video Endpoints")
        self.run_test("GET /videos", self.test_get_videos)
        self.run_test("POST /videos/manual", self.test_create_video_manual)
        self.run_test("DELETE /videos/:id", self.test_delete_video)
        self.run_test("DELETE /videos/invalid-id (404)", self.test_invalid_video_delete)
        
        # Ingest test
        print_header("Ingest Endpoints")
        self.run_test("POST /ingest/rebuild", self.test_ingest_rebuild)
        
        # Chat test (requires ingest to run first)
        print_header("Chat Endpoints")
        self.run_test("POST /chat", self.test_chat)
        
        # 404 test
        print_header("Error Handling")
        self.run_test("GET /nonexistent (404)", self.test_nonexistent_endpoint)
        
        # Summary
        print_header("Test Summary")
        print(f"Total Tests: {self.results['total']}")
        print_success(f"Passed: {self.results['passed']}")
        if self.results['failed'] > 0:
            print_error(f"Failed: {self.results['failed']}")
        else:
            print_info(f"Failed: {self.results['failed']}")
        
        success_rate = (self.results['passed'] / self.results['total']) * 100 if self.results['total'] > 0 else 0
        if success_rate == 100:
            print_success(f"\nAll tests passed! ({success_rate:.0f}%)")
        elif success_rate >= 80:
            print_warning(f"\nMost tests passed ({success_rate:.0f}%)")
        else:
            print_error(f"\nMultiple test failures ({success_rate:.0f}%)")
        
        return self.results['failed'] == 0

if __name__ == "__main__":
    tester = BackendTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)