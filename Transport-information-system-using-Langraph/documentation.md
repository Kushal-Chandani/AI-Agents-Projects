# Transport Query Agent

## 1. Project Overview

The project implements a multi-tool agent capable of answering user queries about Singapore's public transport system. The agent is built using LangGraph, powered by Google's gemini-2.5-flash model, and deployed as a REST API using FastAPI.

### Key Features:

-   **Multi-Tool Capability**: The agent can dynamically choose between three tools to answer a wide range of queries:
    -   `get_bus_arrival_times`: Fetches real-time bus arrival information for a given bus stop.
    -   `get_taxi_availability`: Retrieves the current locations of all available taxis.
    -   `get_traffic_incidents`: Provides information on real-time traffic incidents like accidents and road work.
-   **Orchestration**: LangGraph is used to create a resilient and flexible workflow, allowing the agent to make one or more tool calls to satisfy a user's request.
-   **Production-Ready Deployment**: The agent is wrapped in a FastAPI server, a standard practice for deploying machine learning and AI models in production environments.

## 2. Workflow Design Decisions

The agent's workflow is designed as a cyclical graph using LangGraph, which provides a clear and maintainable structure.

### Graph Components:

1.  **`agent` Node**: This is the brain of the operation. It receives the user's query (and any previous tool outputs) and uses the gemini-2.5-flash model to decide the next step. It can either generate a final answer or decide to call one or more tools.
2.  **`tools` Node**: If the `agent` node decides to use a tool, this node is responsible for executing it. It takes the tool calls from the agent's message, runs the corresponding Python functions, and returns the results.
3.  **Conditional Edge (`should_continue`)**: This is the logic that directs the flow of the graph.
    -   If the agent's last message contains tool calls, the graph transitions to the `tools` node.
    -   If the agent's last message does not contain tool calls, it means the agent has formulated a final answer, and the graph execution ends.

This cyclical design (`agent` -> `tools` -> `agent`) is powerful because it allows the agent to chain tool calls or even call multiple tools in parallel if needed, although for this specific implementation, it typically resolves queries in a single loop.

## 3. Assumptions Made

-   **User Input**: The agent expects user queries to be in natural language. It assumes that bus stop codes, when provided, are in the correct format. It does not currently support fuzzy matching or location-based searches for bus stops.
-   **Network Connectivity**: The system requires a stable internet connection to communicate with the Google and LTA DataMall APIs.
-   **Environment**: The code is expected to be run in a Python environment with all the dependencies.

## 4. How to Deploy in a Real-World Production Environment

Deploying this agent in a production environment requires additional considerations for scalability, security, and reliability.

1.  **Containerization**:
    -   Package the FastAPI application into a Docker container. This creates a portable, self-contained environment that can be deployed consistently across different systems. A `Dockerfile` would be created to manage this process.

2.  **Cloud Deployment**:
    -   Deploy the Docker container to a cloud platform like Google Cloud Platform (GCP).
    -   **Serverless**: For applications with variable traffic, a serverless platform like AWS Lambda or Google Cloud Run is an excellent choice. It automatically scales the number of instances based on demand and is highly cost-effective.
    -   **Kubernetes**: For more complex, large-scale deployments, a container orchestration platform like Kubernetes would be used to manage scaling, load balancing, and resilience.

3.  **State Management and Concurrency**:
    -   The current implementation is stateless for each request. For more complex conversational agents that need to remember past interactions, a persistent checkpointer (e.g., using Redis) would be integrated with LangGraph to manage each user's state independently.

4.  **Security**:
    -   **API Key Management**: I also think in a production environment, API keys and other secrets should be stored in a dedicated secrets management service like AWS Secrets Manager or HashiCorp Vault, not in `.env` files.
    -   **Authentication**: The API endpoint should be protected with an authentication mechanism (e.g., API keys) to ensure that only authorized users or services can access it.

5.  **Monitoring and Logging**:
    -   Integrate a logging framework to capture detailed information about requests, responses, tool calls, and any errors.
    -   Use monitoring and observability tools like Prometheus to track the application's performance, latency, and error rates. This is crucial for identifying and resolving issues proactively.

## 5. How to Run This Project

1.  **Set Up API Keys**:
    -   Create a file named `.env` in the root of the project.
    -   Add your API keys to this file:
        ```
        GOOGLE_API_KEY="your_google_api_key"
        LTA_DATAMALL_API_KEY="your_lta_datamall_api_key"
        ```

2.  **Run the FastAPI Server**:
    -   Run all the cells in `Hyptos_assignment_Part_1.ipynb`:
    -   The server will start and be accessible at `http://127.0.0.1:8000`.

3.  **Run the Simulation**:
    -   Then in a seperate window, run the `Hyptos_assignment_Part_2.ipynb`:
    -   This will send 10 different queries to the running server and print the agent's responses.