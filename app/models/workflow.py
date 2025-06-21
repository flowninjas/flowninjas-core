"""Workflow data models and schemas."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, validator


class WorkflowNodeType(str, Enum):
    """Types of workflow nodes."""
    START = "start"
    END = "end"
    CLOUD_FUNCTION = "cloud_function"
    CLOUD_RUN = "cloud_run"
    PUBSUB_PUBLISH = "pubsub_publish"
    PUBSUB_SUBSCRIBE = "pubsub_subscribe"
    HTTP_REQUEST = "http_request"
    CONDITION = "condition"
    PARALLEL = "parallel"
    DELAY = "delay"
    ASSIGN = "assign"
    CALL = "call"
    SWITCH = "switch"
    FOR_LOOP = "for_loop"
    TRY_CATCH = "try_catch"


class WorkflowNodePosition(BaseModel):
    """Position of a node in the workflow canvas."""
    x: float = Field(..., description="X coordinate")
    y: float = Field(..., description="Y coordinate")


class WorkflowNodeConfig(BaseModel):
    """Configuration for a workflow node."""
    # Common properties
    name: str = Field(..., description="Node name")
    description: Optional[str] = Field(None, description="Node description")
    
    # Node-specific configuration
    function_name: Optional[str] = Field(None, description="Cloud Function name")
    service_name: Optional[str] = Field(None, description="Cloud Run service name")
    topic_name: Optional[str] = Field(None, description="Pub/Sub topic name")
    subscription_name: Optional[str] = Field(None, description="Pub/Sub subscription name")
    url: Optional[str] = Field(None, description="HTTP request URL")
    method: Optional[str] = Field("GET", description="HTTP method")
    headers: Optional[Dict[str, str]] = Field(None, description="HTTP headers")
    body: Optional[Dict[str, Any]] = Field(None, description="Request body")
    condition: Optional[str] = Field(None, description="Condition expression")
    delay_seconds: Optional[int] = Field(None, description="Delay in seconds")
    variables: Optional[Dict[str, Any]] = Field(None, description="Variables to assign")
    call_target: Optional[str] = Field(None, description="Target to call")
    call_args: Optional[Dict[str, Any]] = Field(None, description="Call arguments")
    switch_variable: Optional[str] = Field(None, description="Switch variable")
    switch_cases: Optional[List[Dict[str, Any]]] = Field(None, description="Switch cases")
    loop_variable: Optional[str] = Field(None, description="Loop variable")
    loop_range: Optional[Dict[str, Any]] = Field(None, description="Loop range")
    try_steps: Optional[List[str]] = Field(None, description="Try block steps")
    catch_steps: Optional[List[str]] = Field(None, description="Catch block steps")
    
    # AI prompt for code generation
    ai_prompt: Optional[str] = Field(None, description="AI prompt for code generation")
    
    # Environment variables
    env_vars: Optional[Dict[str, str]] = Field(None, description="Environment variables")
    
    # Resource configuration
    memory: Optional[str] = Field(None, description="Memory allocation")
    cpu: Optional[str] = Field(None, description="CPU allocation")
    timeout: Optional[str] = Field(None, description="Timeout")


class WorkflowNode(BaseModel):
    """A node in the workflow."""
    id: str = Field(..., description="Unique node ID")
    type: WorkflowNodeType = Field(..., description="Node type")
    position: WorkflowNodePosition = Field(..., description="Node position")
    config: WorkflowNodeConfig = Field(..., description="Node configuration")
    
    # Connections
    inputs: List[str] = Field(default_factory=list, description="Input node IDs")
    outputs: List[str] = Field(default_factory=list, description="Output node IDs")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class WorkflowConnection(BaseModel):
    """Connection between workflow nodes."""
    id: str = Field(..., description="Unique connection ID")
    source_node_id: str = Field(..., description="Source node ID")
    target_node_id: str = Field(..., description="Target node ID")
    source_handle: Optional[str] = Field(None, description="Source handle")
    target_handle: Optional[str] = Field(None, description="Target handle")
    condition: Optional[str] = Field(None, description="Connection condition")


class WorkflowMetadata(BaseModel):
    """Workflow metadata."""
    name: str = Field(..., description="Workflow name")
    description: Optional[str] = Field(None, description="Workflow description")
    version: str = Field(default="1.0.0", description="Workflow version")
    tags: List[str] = Field(default_factory=list, description="Workflow tags")
    author: Optional[str] = Field(None, description="Workflow author")
    
    # Google Cloud settings
    project_id: Optional[str] = Field(None, description="Google Cloud project ID")
    region: str = Field(default="us-central1", description="Google Cloud region")
    
    # Execution settings
    timeout: Optional[str] = Field(None, description="Workflow timeout")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Workflow(BaseModel):
    """Complete workflow definition."""
    id: str = Field(..., description="Unique workflow ID")
    metadata: WorkflowMetadata = Field(..., description="Workflow metadata")
    nodes: List[WorkflowNode] = Field(..., description="Workflow nodes")
    connections: List[WorkflowConnection] = Field(..., description="Node connections")
    
    @validator('nodes')
    def validate_nodes(cls, v):
        """Validate workflow nodes."""
        if not v:
            raise ValueError("Workflow must have at least one node")
        
        # Check for start and end nodes
        start_nodes = [node for node in v if node.type == WorkflowNodeType.START]
        end_nodes = [node for node in v if node.type == WorkflowNodeType.END]
        
        if len(start_nodes) != 1:
            raise ValueError("Workflow must have exactly one start node")
        
        if len(end_nodes) < 1:
            raise ValueError("Workflow must have at least one end node")
        
        return v


class WorkflowGenerationRequest(BaseModel):
    """Request to generate workflow code."""
    workflow: Workflow = Field(..., description="Workflow definition")
    target_format: str = Field(default="yaml", description="Target format (yaml, json)")
    include_deployment: bool = Field(default=True, description="Include deployment configs")
    ai_enhance: bool = Field(default=True, description="Use AI to enhance code generation")


class WorkflowGenerationResponse(BaseModel):
    """Response from workflow code generation."""
    workflow_id: str = Field(..., description="Workflow ID")
    generated_files: Dict[str, str] = Field(..., description="Generated files content")
    deployment_configs: Optional[Dict[str, str]] = Field(None, description="Deployment configurations")
    ai_suggestions: Optional[List[str]] = Field(None, description="AI suggestions")
    generation_time: float = Field(..., description="Generation time in seconds")
    
    
class WorkflowExecutionStatus(str, Enum):
    """Workflow execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class WorkflowExecution(BaseModel):
    """Workflow execution record."""
    id: str = Field(..., description="Execution ID")
    workflow_id: str = Field(..., description="Workflow ID")
    status: WorkflowExecutionStatus = Field(..., description="Execution status")
    input_data: Optional[Dict[str, Any]] = Field(None, description="Input data")
    output_data: Optional[Dict[str, Any]] = Field(None, description="Output data")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = Field(None, description="Completion time")
    duration_seconds: Optional[float] = Field(None, description="Execution duration")
