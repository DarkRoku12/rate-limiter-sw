
### Quick checklist

[✅] Constraints: Timestamps can be assumed to be generally increasing but may occasionally arrive slightly out of order. The input stream can be of arbitrary length and will be terminated by an End-Of-File (EOF) signal.

-> `rate_limiter.py` Implemented by ordering the queue (deque) within each client allowed request pool.

[✅] Success Output (stdout): For each valid input request processed, the application must write a single JSON line to stdout indicating the rate limiter's decision. The output order must correspond to the order in which valid input requests were processed (ALLOW, DENY).

-> `main.py` Implemented in main processing.

[✅] Error Handling: The application must gracefully handle malformed JSON lines or lines not conforming to the expected structure. Such errors should be reported to stderr, and the application should continue processing subsequent valid lines.

-> `main.py` Implemented in main processing.

[✅] Error Output (stderr): All diagnostic messages, including parsing errors, internal application errors, or warnings, must be written to stderr. stdout should only contain the valid decision JSON lines.

-> `main.py` Implemented in main processing.

[✅] Algorithm: Implement a suitable rate limiting algorithm (e.g., Sliding Window Counter, Token Bucket) to enforce the "10 requests per 60 seconds per client ID" rule. The choice of algorithm should be justifiable in your README.

-> `rate_limiter.py` Implemented within the rate limiter, the core algorithm used is sliding window using bounded deque for each client.

[✅] State Management: Maintain the necessary state (e.g., request timestamps, counts, token levels) for each unique clientId entirely in memory. No persistent storage (files, databases) should be used for rate limiting state.

-> `rate_limiter.py` Implemented within the rate limiter, the main structure is a in-memory bounded deque.

[✅] Time Handling: Correctly manage time based on the timestamp field in the input requests. The implementation must accurately track requests within the defined 60-second window for each client. Consider how to handle state for clients over time (e.g., cleaning up state for inactive clients is not required for this exercise, but efficient window management is).

-> `rate_limiter.py` Implemented within the rate limiter, we'll discard DENY any request under the last window (60s) frame,
as long as it is over the ALLOWED request's limit (10) under the given window, which will depend and move based on the provided request timestamp history. 

[✅] Stream Processing: Process the stdin stream line by line until EOF is reached.

-> `main.py` It will process each request as it arrives from stdin, it will treat is as a stream and process it line by line until EOF.

[✅] Execution: The solution must be runnable as a standalone command-line application.

-> `main.py` 
`python main.py` -> Interactive console stdin until EOF (`ctrl+d` / `ctrl+z`, os dependant)
`python main.py < input.txt` -> Buffers the sample file `input.txt` to the program.

[✅] Dependencies

-> No third party packages, just standard library.

[✅] Installation

-> Only requires Python 12+. 