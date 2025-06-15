import unittest
import rate_limiter as rl

class TestRateLimiter(unittest.TestCase):
  def setUp(self):
      # Common parameters for tests.
      self.max_requests = 10
      self.window_duration_ms = 20_000  # 20 second window.
      self.unalloc_threshold = min(5, self.max_requests)
      self.base_time = 1_000.0  # Base timestamp for tests (in seconds).
      
      # Reset mappings for each test.
      self.rate_mapper = {}
      self.unalloc_candidates = {}
      
      # Test config.
      self.client_idx = 0
  
  def get_next_client_id(self): 
      self.client_idx += 1
      return f"client_{self.client_idx}"

  def create_request_params(self, client_id, req_timestamp):
      """Helper method to create request parameters"""
      
      return rl.InIsReqAllowed(
          rate_mapper=self.rate_mapper,
          unalloc_candidates=self.unalloc_candidates,
          max_requests=self.max_requests,
          unalloc_threshold=self.unalloc_threshold,
          window_duration_ms=self.window_duration_ms,
          client_id=client_id,
          req_timestamp=req_timestamp
      )
        
  def test_allowed_requests_simple(self):
    """Test that requests within the limit are allowed"""
    
    client_id = self.get_next_client_id()
    max_requests = self.max_requests
    
    # Make several requests up to the limit.
    for i in range(max_requests):
        params = self.create_request_params(client_id, self.base_time + i * 0.5)
        self.assertTrue(rl.is_request_allowed(params)) # Must be allowed.
        self.assertEqual(len(self.rate_mapper[client_id]), min(i + 1, max_requests)) # Check deque length.
    
  def test_allowed_requests_non_overlapping_bursts(self):
    """Test that requests in separate time windows are allowed"""
    
    client_id = self.get_next_client_id()
    max_requests = self.max_requests
    
    # First burst of requests - fill up the limit.
    for i in range(max_requests):
        params = self.create_request_params(client_id, self.base_time + i * 0.5)
        self.assertTrue(rl.is_request_allowed(params))
    
    # Wait for window to expire.
    next_window_time = self.base_time + (self.window_duration_ms / 1000) + 0.5
    
    # Second burst of requests after window expiration.
    for i in range(max_requests):
        params = self.create_request_params(client_id, next_window_time + i * 0.5)
        self.assertTrue(rl.is_request_allowed(params))
    
    # Check that client still has only 10 requests in the deque (oldest ones were removed).
    self.assertEqual(len(self.rate_mapper[client_id]), max_requests)
    
  def test_blocked_requests_simple(self):
    """Test that requests exceeding the limit are blocked"""
    
    client_id = self.get_next_client_id()
    max_requests = self.max_requests
    
    last_timestamp = self.base_time
    min_safe_duration_ms = self.window_duration_ms / max_requests
    
    # Fill up the limit.
    for i in range(max_requests):
        last_timestamp += min_safe_duration_ms / 1000 # [Note: order is important here].
        params = self.create_request_params(client_id, last_timestamp)
        self.assertTrue(rl.is_request_allowed(params))
    
    # Try one more request - Must be blocked.
    last_timestamp += min_safe_duration_ms / 1000 # Add a new request still under the threshold.
    params = self.create_request_params(client_id, last_timestamp )
    self.assertFalse(rl.is_request_allowed(params))
    
    # Check that client still has only 10 requests in the deque.
    self.assertEqual(len(self.rate_mapper[client_id]), max_requests)
    
  def test_blocked_requests_overlapping_bursts(self):
    """Test that requests in overlapping bursts are blocked appropriately"""
    
    client_id = self.get_next_client_id()
    max_requests = self.max_requests
    
    # First burst of requests
    for i in range(max_requests):
        params = self.create_request_params(client_id, self.base_time + i * 0.5)
        self.assertTrue(rl.is_request_allowed(params))
    
    # Wait for only part (1/4) of the window to expire.
    partial_wait = (self.window_duration_ms / 1000) / 4
    
    # Try another burst - these should be blocked as we're still in the window.
    for i in range(3):
        next_timestamp = self.base_time + partial_wait + i * 0.5
        params = self.create_request_params(client_id, next_timestamp)
        self.assertFalse(rl.is_request_allowed(params))
    
    # Wait for the first request to expire.
    first_expired = self.base_time + (self.window_duration_ms / 1000) + 0.1  # Just past window.
    
    # Now a new request should be allowed.
    params = self.create_request_params(client_id, first_expired)
    self.assertTrue(rl.is_request_allowed(params))
    
  def test_multiple_clients(self):
    """Test that different clients are tracked separately"""
    
    client_a = self.get_next_client_id()
    client_b = self.get_next_client_id()
    
    # Fill up client A's limit.
    for i in range(10):
        params = self.create_request_params(client_a, self.base_time + i * 0.5)
        self.assertTrue(rl.is_request_allowed(params))
    
    # Client A should now be blocked.
    params = self.create_request_params(client_a, self.base_time + 5.0)
    self.assertFalse(rl.is_request_allowed(params))
    
    # But client B should be allowed.
    for i in range(10):
        params = self.create_request_params(client_b, self.base_time + i * 0.5)
        self.assertTrue(rl.is_request_allowed(params))
        
  def test_unalloc_candidates_tracking(self):
    """Test tracking & clear of inactive clients"""

    client_x = self.get_next_client_id()
    client_a = self.get_next_client_id()
    client_b = self.get_next_client_id()
        
    # Fill up client X. (Should NOT be in, since request will fill bellow threshold).
    for i in range(self.unalloc_threshold - 1):
        params = self.create_request_params(client_x, self.base_time + i)
        self.assertTrue(rl.is_request_allowed(params))
    
    # Fill up client A.
    client_a_step = 0.2
    
    for i in range(self.unalloc_threshold):
        params = self.create_request_params(client_a, self.base_time + i * client_a_step)
        self.assertTrue(rl.is_request_allowed(params))
    
    # Fill up client B.
    client_b_step = client_a_step * 2  # Different step to ensure different timestamps.
    for i in range(self.unalloc_threshold):
        params = self.create_request_params(client_b, self.base_time + i * client_b_step)
        self.assertTrue(rl.is_request_allowed(params))
        
    uc = self.unalloc_candidates
        
    # Check that both clients are in unalloc_candidates.
    self.assertNotIn(client_x, uc)
    self.assertIn(client_a, uc)
    self.assertIn(client_b, uc)
    
    # Check that both clients have the correct timestamps.
    loop_n = self.unalloc_threshold - 1
    self.assertEqual(uc[client_a], 1000 * (self.base_time + loop_n * client_a_step))
    self.assertEqual(uc[client_b], 1000 * (self.base_time + loop_n * client_b_step))
        
    # Should free/clear A but not B.
    rl.free_inactive_clients(
      self.rate_mapper, 
      self.unalloc_candidates, 
      clear_beq_time_ms=1000 * (self.base_time + loop_n * client_a_step)
    )
    
    self.assertIn(client_b, uc)
    self.assertNotIn(client_a, uc)

### Run the tests ###
if __name__ == "__main__":
  unittest.main(verbosity=2)
