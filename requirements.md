# Take-Home Assessment: Command-Line Rate Limiter Service

## 1. Introduction

Welcome to the Tephra Labs backend engineering take-home assessment! This exercise is designed to give you an opportunity to showcase your practical backend development skills in a scenario relevant to the challenges we tackle. We value your time and have designed this task accordingly.

**Time Expectation & AI Tools:** This assessment is calibrated with modern development practices in mind. We estimate that building a robust solution without AI coding assistance (like GitHub Copilot, ChatGPT, etc.) might take approximately 2-3 hours of focused effort. However, if you effectively leverage AI tools for generating boilerplate code and initial scaffolding, you should aim to complete a functional solution in significantly less time, around 1 hour. The evaluation focuses on the quality, correctness, and design of your final submission, not strictly the time taken, but this calibration is intended to guide your effort. The goal is to assess your ability to integrate tools effectively while applying critical thinking to nuanced implementation, testing, and design.

## 2. Problem Statement

Implement a command-line application that simulates an in-memory rate limiter for client requests. The application must read a stream of client request events from standard input (`stdin`), apply a specified rate limiting rule based on unique client identifiers, and output decisions (`ALLOW` or `DENY`) for each request to standard output (`stdout`). Any processing errors or diagnostic information should be reported to standard error (`stderr`).

The specific rate limiting requirement is: **Limit each unique client ID to a maximum of 10 requests per 60 seconds.** You should implement an algorithm suitable for this requirement.

## 3. Input Specification (stdin)

* **Format:** Input will be provided via `stdin` as a stream of JSON objects, one per line (JSON lines format).
* **Structure:** Each line will conform to the following structure:
  ```json
  {"timestamp": "YYYY-MM-DDTHH:mm:ssZ", "clientId": "string"}
  ```
* **Fields:**
  * `timestamp`: An ISO 8601 formatted string representing the time of the request (UTC).
  * `clientId`: A non-empty string identifying the client making the request.
* **Constraints:** Timestamps can be assumed to be generally increasing but may occasionally arrive slightly out of order. The input stream can be of arbitrary length and will be terminated by an End-Of-File (EOF) signal.
* **Error Handling:** The application must gracefully handle malformed JSON lines or lines not conforming to the expected structure. Such errors should be reported to `stderr`, and the application should continue processing subsequent valid lines.

## 4. Output Specification (stdout/stderr)

* **Success Output (`stdout`):** For each valid input request processed, the application must write a single JSON line to `stdout` indicating the rate limiter's decision. The output order must correspond to the order in which valid input requests were processed.
  * Example ALLOW output: `{"timestamp": "2023-10-27T10:00:01Z", "clientId": "user123", "decision": "ALLOW"}`
  * Example DENY output: `{"timestamp": "2023-10-27T10:00:01Z", "clientId": "user123", "decision": "DENY"}`
* **Error Output (`stderr`):** All diagnostic messages, including parsing errors, internal application errors, or warnings, must be written to `stderr`. `stdout` should only contain the valid decision JSON lines.

## 5. Core Logic Requirements

* **Algorithm:** Implement a suitable rate limiting algorithm (e.g., Sliding Window Counter, Token Bucket) to enforce the "10 requests per 60 seconds per client ID" rule. The choice of algorithm should be justifiable in your README.
* **State Management:** Maintain the necessary state (e.g., request timestamps, counts, token levels) for each unique `clientId` entirely *in memory*. No persistent storage (files, databases) should be used for rate limiting state.
* **Time Handling:** Correctly manage time based on the `timestamp` field in the input requests. The implementation must accurately track requests within the defined 60-second window for each client. Consider how to handle state for clients over time (e.g., cleaning up state for inactive clients is *not* required for this exercise, but efficient window management is).
* **Stream Processing:** Process the `stdin` stream line by line until EOF is reached.

## 6. Constraints and Environment

* **Execution:** The solution must be runnable as a standalone command-line application.
* **Languages:** Preferred languages are Go, TypeScript (runnable via `ts-node` or compiled to JavaScript runnable with Node.js), Rust, or Python. If you wish to use another language, please check with us first.
* **Dependencies:** Use of the standard library is strongly preferred. Minimal external libraries are permissible only if essential for core functionality (e.g., high-precision time handling if the standard library is insufficient) and must be explicitly justified in the README. Web frameworks, databases, ORMs, message queues, or other significant external dependencies are strictly forbidden.
* **Installation:** Any required non-standard dependencies must be easily installable using standard package managers (`go mod`, `npm`/`yarn`, `cargo`, `pip`) and documented clearly.

## 7. Submission Guidelines

* **Submission:** Please use the GitHub repository that is provided to you as we will use it to get your submission. 
* **Contents:** The repository must contain all source code, any necessary build/configuration files, and the mandatory `README.md` file.
* **README Contents:** Your `README.md` must include:
  * Clear instructions on how to build and run the application.
  * Instructions on how to execute the tests.
  * A brief explanation of your chosen rate limiting algorithm and any significant design decisions made.
  * List and justification for any external libraries used.
* **Commit History:** Maintain a clear commit history showing your development process.

Thank you for your time and effort. We look forward to reviewing your submission!
