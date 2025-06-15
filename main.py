import os
import sys
import json
from datetime import datetime
from typing import Literal
import rate_limiter as rl

def log_error(*args):
  """Log error messages to stderr."""
  print(*args, file=sys.stderr)
  
def log_ok(*args):
  """Log successful messages to stdout."""
  print(*args, file=sys.stdout)
  
def validate_timestamp(data: dict) -> tuple[float, str] | Literal[False]:
  """Validate timestamp to be in ISO 8601 format."""
  raw_timestamp = data.get("timestamp", None)
  if not raw_timestamp:
    log_error("[missing_timestamp]:", data)
    return False
  try:
    ts = datetime.fromisoformat(raw_timestamp)
    return (ts.timestamp(), raw_timestamp)
  except (ValueError, TypeError):
    log_error("[invalid_timestamp]:", data)
    return False
  
def validate_client_id(data: dict) -> tuple[str, str] | Literal[False]:
  """
    Validate clientId to be a non-empty (at least one non-blank char) string.
    We're stripping whitespace from the clientId, if this behavior is not desired,
    we can either use T[0] for the stripped value or T[1] for the original value.
  """
  raw_client_id = data.get("clientId", None)
  if not raw_client_id or type(raw_client_id) is not str:
    log_error("[missing_clientId]:", data)
    return False
  client_id = raw_client_id.strip()
  if not client_id:
    log_error("[empty_clientId]:", data)
    return False
  return (client_id, raw_client_id)

def main( debug_clients: set[str] = set([]) ):
  g_window_duration_ms: int = 60 * 1000  # 60 seconds window interval.
  g_max_requests: int = 10 # 10 Reqs per <g_window_duration> seconds.
  g_unalloc_threshold: int = min( int(g_max_requests / 2), g_max_requests )
  g_rate_mapper: rl.RateMapper = {}
  g_unalloc_candidates: rl.UnallocDict = {}
  g_debug_clients: set[str] = debug_clients # Optional whitelist of clients to process (empty to disable).

  for line in sys.stdin:
    line = line.strip()

    try:
      data = json.loads(line)  # Validate JSON format
      t_timestamp = validate_timestamp(data)
      t_client_id = validate_client_id(data)
      
      # Skip this line if any validation failed.
      if t_client_id is False or t_timestamp is False:
        continue
      
      # A debug line that can be removed, the purpose is to quickly narrow client selection to the specified whitelist.
      # If the whitelist is empty, all clients will be processed.
      if( len(g_debug_clients) and t_client_id[0] not in g_debug_clients ): 
        continue
      
      # Check if the request is allowed based on the rate limiting logic.
      is_valid = rl.is_request_allowed(
        rl.InIsReqAllowed(
          rate_mapper=g_rate_mapper,
          unalloc_candidates=g_unalloc_candidates,
          max_requests=g_max_requests,
          unalloc_threshold=g_unalloc_threshold,
          window_duration_ms= g_window_duration_ms,
          client_id=t_client_id[1],
          req_timestamp=t_timestamp[0]
        )
      )
      
      # Optionally, we may determine a logic to call `free_inactive_clients`.
      # Since it is somewhat out of the scope of this task, we'll skip it.
      
      # Print output.
      decision = "DENY" if not is_valid else "ALLOW"
      raw_output = f'"timestamp": "{t_timestamp[1]}", "clientId": "{t_client_id[1]}", "decision": "{decision}"'
      log_ok( '{' + raw_output + '}' )

    except json.JSONDecodeError:
      log_error("[invalid_json]:", line)
      continue

    except Exception as e:
      e_class = e.__class__.__name__
      log_error("[err_processing_line]:", line,f"[{e_class}] -> {str(e)}")
      continue
    

def debug_redirect_logs():
  """Redirect stdout and stderr to log files."""
  if not os.path.exists("logs"):
    os.makedirs("logs")
  sys.stdout = open("logs/stdout.log", "w")
  sys.stderr = open("logs/stderr.log", "w")
  
if __name__ == "__main__":
  # Note: Uncomment the next line to redirect logs to files.
  # debug_redirect_logs()
  main()
