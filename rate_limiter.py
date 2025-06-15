

from collections import deque
from typing import Dict
from dataclasses import dataclass

# Note: Requires Python 12 for type hints. See: https://peps.python.org/pep-0695/
type TimeDeque = deque[float]
type RateMapper = Dict[str, TimeDeque]
type UnallocDict = Dict[str, float]

@dataclass
class InIsReqAllowed():
  # Allocated structures.
  rate_mapper: RateMapper
  unalloc_candidates: UnallocDict
  
  # Rate limiter config.
  max_requests: int
  unalloc_threshold: int
  window_duration_ms: int
  
  # Incoming request info.
  client_id: str 
  req_timestamp: float

def is_request_allowed( params : InIsReqAllowed ) -> bool:
  """Check if a request is allowed based on rate limiting rules"""
  rate_deque: TimeDeque | None = params.rate_mapper.get(params.client_id, None)
  client_id = params.client_id
  max_requests = params.max_requests
  req_time_ms = params.req_timestamp * 1000  # Convert to milliseconds.
  
  # Create a new deque for the client if it doesn't exist.
  if rate_deque is None:
    rate_deque = deque([], max_requests)
    params.rate_mapper[client_id] = rate_deque
  
  len_rate_deque = len(rate_deque)

  # If the deque is not full, add the request time.
  if( len_rate_deque < max_requests ):
    rate_deque.append(req_time_ms)
    sort_deque(rate_deque) # Requirement: Timestamp may not be in increasing order.
    if( len_rate_deque + 1 >= params.unalloc_threshold ): 
      params.unalloc_candidates[client_id] = req_time_ms
    return True
  # If the deque is full, check the oldest request time.
  else:
    in_window: float = req_time_ms - params.window_duration_ms
    if( rate_deque[0] < in_window ):
      rate_deque.append(req_time_ms)
      sort_deque(rate_deque) # Requirement: Timestamp may not be in increasing order.
      return True
    else:
      return False
    
def free_inactive_clients(
  rate_mapper: RateMapper, 
  unalloc_candidates: UnallocDict, 
  clear_beq_time_ms: float # Clear before/or equal to this timestamp.
) -> None:
  """Free inactive client's deque based on the unalloc_candidates"""
  for client_id in list(unalloc_candidates.keys()):
    if unalloc_candidates[client_id] <= clear_beq_time_ms:
      unalloc_candidates.pop(client_id, None)
      rate_mapper.pop(client_id, None)
      
def sort_deque( dq: deque ) -> deque:
  """We only need to sort the last element in the deque if it is smaller than the previous one"""
  idx = len(dq) - 1
  if idx < 1: 
    return dq
  
  last = dq[idx]
  while idx and last < dq[idx - 1]:
    dq[idx], dq[idx - 1] = dq[idx - 1], last
    idx -= 1
  return dq
  

######################################################################

### Ok, I know, maybe this is not the best place for an example usage, 
### But there are few arguments:
### 1. It can be moved and converted to a PyDoc.
### 2. It increase the example visibility.
### 3. If parameters are changed, there is a better probability the developer also updates the example. 

"""Example usage"""

# from datetime import datetime

# g_max_requests: int = 3
# g_window_duration: int = 20
# g_unalloc_threshold: int = min( 5, g_max_requests )
# g_rate_mapper: RateMapper = {}
# g_unalloc_candidates: UnallocDict = {}

# for i in range(g_max_requests + 2):
#   time_penalty = 2 # second(s)
#   interval_sec = (i * g_window_duration / g_max_requests) - (i * time_penalty)
#   allowed = is_request_allowed(
#     InIsReqAllowed(
#       rate_mapper = g_rate_mapper,
#       unalloc_candidates = g_unalloc_candidates,
#       max_requests = g_max_requests,
#       unalloc_threshold = g_unalloc_threshold,
#       window_duration_ms = g_window_duration * 1000, # Convert to milliseconds.
#       client_id = "client1",
#       req_timestamp = datetime.now().timestamp() + interval_sec
#     )
#   )
#   print(f"Request allowed: {allowed}")