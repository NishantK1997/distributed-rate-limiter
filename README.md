# distributed-rate-limiter
A distributed rate limiting system built with FastAPI, AsyncIO, and custom algorithms for sliding window counters, priority scheduling, multi-tenant fairness, and concurrency control. Designed to simulate real-world infrastructure challenges.

# Distributed Rate Limiter

A distributed rate limiting system built using FastAPI, AsyncIO, and custom algorithms to simulate real-world traffic management challenges such as burst traffic handling, tenant isolation, priority scheduling, and distributed coordination.

The objective of this project is to build a scalable and testable rate limiting pipeline capable of handling multiple tenants while maintaining fairness and enforcing consistent limits across distributed nodes.

---

## Why This Project?

Modern systems receive traffic from multiple clients, services, and tenants at the same time. Simple rate limiting approaches often create problems such as burst traffic spikes, unfair request distribution, and inconsistent behavior across distributed systems.

This project was built to explore how different algorithms can work together to solve those problems while keeping the system modular and easy to test.

---

## Features

### Rate Limiting

* Sliding Window Counter implementation
* Weighted request calculation
* Retry-after support
* Boundary precision handling
* Burst traffic protection

### Distributed Coordination

* Shared distributed state simulation
* Multi-node request handling
* Global rate enforcement
* Node registration support

### Multi-Tenant Support

* Tenant isolation
* Independent quotas
* Fair resource allocation
* Burst capacity handling

### Scheduling Support

* Priority-based request processing
* FIFO ordering
* Priority aging
* Priority inversion validation

### Platform Features

* FastAPI integration
* Async request processing
* Benchmark support
* API validation
* Scenario-based testing

---

## Tech Stack

* Python 3.10+
* FastAPI
* AsyncIO
* Pytest
* Custom Algorithms
* Redis Simulator

---

## Project Structure

 
distributed-rate-limiter/

algorithms/
benchmarks/
config/
models/
services/
storage/
tests/

main.py
requirements.txt
README.md
  

---

## Algorithms Used

### Sliding Window Counter

Used for request throttling while reducing hard window boundary problems.

Why it was used:

* smoother traffic distribution
* weighted calculations
* more accurate throttling

### Token Bucket

Used for burst handling and fairness.

Supports:

* refill rates
* burst capacity
* isolated quotas

### Fairness Engine

Used for tenant isolation and quota separation.

Responsibilities:

* fairness enforcement
* tenant isolation
* independent allocation

### Priority Scheduler

Used for request prioritization.

Supports:

* priority handling
* FIFO behavior
* aging support

### Distributed Coordinator

Used to coordinate multiple nodes through shared state.

Responsibilities:

* node registration
* shared limits
* distributed consistency

---

## Installation

Clone repository:

  bash
git clone <repository-url>

cd distributed-rate-limiter
  

Create virtual environment:

  bash
python -m venv venv
  

Activate environment:

Linux / Mac:

  bash
source venv/bin/activate
  

Windows:

  bash
venv\Scripts\activate
  

Install dependencies:

  bash
pip install -r requirements.txt
  

---

## Running The API

Start server:

  bash
uvicorn main:app --reload
  

Open:

  
http://127.0.0.1:8000/docs
  

Available endpoints:

  
GET /health

POST /allow
  

---

## Running Tests

Run complete test suite:

  bash
python -m pytest tests/ -v
  

Current validation:

  
22 Tests Passed
  

---

## Running Benchmarks

Run burst traffic benchmark:

  bash
python benchmarks/burst_traffic.py
  

Observed benchmark:

  
10000 Requests

100 Allowed

9900 Blocked

~50K req/sec throughput
  

---

## Validation Scenarios Covered

### Scenario 1 — Burst Traffic

Validated request throttling under heavy load.

### Scenario 2 — Priority Inversion

Validated request prioritization behavior.

### Scenario 3 — Multi-Tenant Fairness

Validated tenant isolation and fairness.

### Scenario 4 — Sliding Window Precision

Validated weighted calculations across windows.

### Scenario 5 — Distributed Coordination

Validated multi-node consistency.

---

## Current Status

* Benchmark Validation Passed
* Distributed Validation Passed
* API Validation Passed
* Scenario Validation Passed
* 22 Tests Passing

---

## Future Improvements

* Real Redis integration
* Horizontal scaling
* Metrics and monitoring
* Containerization support
* Kubernetes deployment
* Persistent distributed storage
* Observability dashboards
