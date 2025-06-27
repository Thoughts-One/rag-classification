# System Patterns

This file describes common system patterns and architectural decisions.

## Coding Doctrine

## Core Doctrine: **Incremental Development with Continuous Validation**

### Primary Principles:

**1. Minimum Viable Implementation (MVI)**
- Implement the smallest possible code change that delivers a complete, testable feature increment
- Each change should be independently verifiable and deployable

**2. Red-Green-Refactor Cycles (TDD-inspired)**
- Write failing test → Write minimal code to pass → Refactor → Repeat
- Even without strict TDD, maintain this rhythm of test-implement-verify

**3. Vertical Slicing**
- Cut features into thin vertical slices that touch all necessary layers (UI → business logic → data)
- Each slice delivers end-to-end functionality, however minimal

### Supporting Practices:

**Atomic Commits & Feature Branches**
- Each commit represents a complete, working unit
- Commits should compile, pass tests, and not break existing functionality

**Walking Skeleton Approach**
- Start with the thinnest possible end-to-end implementation
- Gradually flesh out functionality while maintaining working state

**Fail-Fast Feedback Loops**
- Integrate and test frequently (ideally after each small change)
- Catch issues early when context is fresh and fixes are simple

**YAGNI Principle (You Aren't Gonna Need It)**
- Implement only what's immediately needed for the current increment
- Avoid anticipatory complexity

### Practical Implementation:

- **Feature decomposition**: Break large features into independently deliverable micro-features
- **Time-boxing**: Set short development cycles (30min-2hrs) before testing
- **Integration checkpoints**: Verify the system works after each increment
- **Evolutionary design**: Let architecture emerge through small, validated changes

This doctrine is often called **"Baby Steps Development"** or **"Micro-Increment Development"** in agile contexts.
[2025-06-26 19:15:30] - Deployment Pattern: Render.com Managed Dependencies
- All Python dependencies are installed during Render.com build phase
- Local development should use same requirements.txt but not require local installs
- Production environment is fully containerized with dependencies baked in
[2025-06-26 19:24:16] - Production Deployment Pattern
- Service URL: https://rag-classification.onrender.com
- Health check endpoint follows standard /api/v1/health pattern
- Fully containerized deployment on Render.com