"""Workflow API endpoints."""

import uuid
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse

from app.core.logging import get_logger
from app.models.workflow import (
    Workflow,
    WorkflowGenerationRequest,
    WorkflowGenerationResponse,
    WorkflowNode,
    WorkflowNodeType,
)
from app.services.workflow_service import WorkflowService

router = APIRouter()
logger = get_logger(__name__)


@router.post("/generate", response_model=WorkflowGenerationResponse)
async def generate_workflow_code(request: WorkflowGenerationRequest):
    """Generate code and configurations for a workflow."""
    logger.info(
        "Received workflow generation request",
        workflow_id=request.workflow.id,
        workflow_name=request.workflow.metadata.name
    )
    
    try:
        workflow_service = WorkflowService()
        
        # Validate workflow
        validation_issues = workflow_service.validate_workflow(request.workflow)
        if validation_issues:
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "Workflow validation failed",
                    "issues": validation_issues
                }
            )
        
        # Generate workflow code
        response = await workflow_service.generate_workflow_code(request)
        
        logger.info(
            "Workflow code generated successfully",
            workflow_id=response.workflow_id,
            files_count=len(response.generated_files)
        )
        
        return response
        
    except Exception as e:
        logger.error(
            "Failed to generate workflow code",
            workflow_id=request.workflow.id,
            error=str(e)
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/save/{workflow_id}")
async def save_workflow_files(
    workflow_id: str,
    files: dict,
    output_path: Optional[str] = Query(None, description="Custom output path")
):
    """Save generated workflow files to local directory."""
    logger.info("Saving workflow files", workflow_id=workflow_id)
    
    try:
        workflow_service = WorkflowService()
        saved_path = await workflow_service.save_workflow_files(
            workflow_id=workflow_id,
            files=files,
            output_path=output_path
        )
        
        return {
            "message": "Workflow files saved successfully",
            "workflow_id": workflow_id,
            "output_path": saved_path,
            "files_count": len(files)
        }
        
    except Exception as e:
        logger.error(
            "Failed to save workflow files",
            workflow_id=workflow_id,
            error=str(e)
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/validate")
async def validate_workflow(workflow: Workflow):
    """Validate a workflow definition."""
    logger.info("Validating workflow", workflow_id=workflow.id)
    
    try:
        workflow_service = WorkflowService()
        issues = workflow_service.validate_workflow(workflow)
        
        is_valid = len(issues) == 0
        
        return {
            "workflow_id": workflow.id,
            "is_valid": is_valid,
            "issues": issues,
            "message": "Workflow is valid" if is_valid else "Workflow has validation issues"
        }
        
    except Exception as e:
        logger.error(
            "Failed to validate workflow",
            workflow_id=workflow.id,
            error=str(e)
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/node-types")
async def get_workflow_node_types():
    """Get available workflow node types."""
    return {
        "node_types": [
            {
                "type": node_type.value,
                "name": node_type.value.replace("_", " ").title(),
                "description": _get_node_type_description(node_type)
            }
            for node_type in WorkflowNodeType
        ]
    }


@router.post("/preview")
async def preview_workflow_yaml(workflow: Workflow):
    """Preview the generated workflow YAML without full code generation."""
    logger.info("Generating workflow YAML preview", workflow_id=workflow.id)
    
    try:
        workflow_service = WorkflowService()
        
        # Validate workflow first
        validation_issues = workflow_service.validate_workflow(workflow)
        if validation_issues:
            return {
                "workflow_id": workflow.id,
                "yaml_content": None,
                "validation_issues": validation_issues,
                "message": "Cannot generate preview due to validation issues"
            }
        
        # Generate basic YAML without AI enhancement
        yaml_content = workflow_service._generate_basic_workflow_yaml(workflow)
        
        return {
            "workflow_id": workflow.id,
            "yaml_content": yaml_content,
            "validation_issues": [],
            "message": "YAML preview generated successfully"
        }
        
    except Exception as e:
        logger.error(
            "Failed to generate workflow YAML preview",
            workflow_id=workflow.id,
            error=str(e)
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/templates")
async def get_workflow_templates():
    """Get predefined workflow templates."""
    templates = [
        {
            "id": "simple-http-workflow",
            "name": "Simple HTTP Workflow",
            "description": "A basic workflow that makes HTTP requests",
            "template": _create_simple_http_template()
        },
        {
            "id": "function-chain-workflow",
            "name": "Function Chain Workflow",
            "description": "Chain multiple Cloud Functions together",
            "template": _create_function_chain_template()
        },
        {
            "id": "pubsub-processing-workflow",
            "name": "Pub/Sub Processing Workflow",
            "description": "Process messages from Pub/Sub topics",
            "template": _create_pubsub_processing_template()
        }
    ]
    
    return {"templates": templates}


def _get_node_type_description(node_type: WorkflowNodeType) -> str:
    """Get description for a workflow node type."""
    descriptions = {
        WorkflowNodeType.START: "Starting point of the workflow",
        WorkflowNodeType.END: "End point of the workflow",
        WorkflowNodeType.CLOUD_FUNCTION: "Execute a Google Cloud Function",
        WorkflowNodeType.CLOUD_RUN: "Call a Google Cloud Run service",
        WorkflowNodeType.PUBSUB_PUBLISH: "Publish a message to Pub/Sub topic",
        WorkflowNodeType.PUBSUB_SUBSCRIBE: "Subscribe to Pub/Sub messages",
        WorkflowNodeType.HTTP_REQUEST: "Make an HTTP request to external service",
        WorkflowNodeType.CONDITION: "Conditional branching based on expression",
        WorkflowNodeType.PARALLEL: "Execute multiple steps in parallel",
        WorkflowNodeType.DELAY: "Add a delay/wait in the workflow",
        WorkflowNodeType.ASSIGN: "Assign values to variables",
        WorkflowNodeType.CALL: "Call another workflow or subworkflow",
        WorkflowNodeType.SWITCH: "Switch statement for multiple conditions",
        WorkflowNodeType.FOR_LOOP: "Loop through a collection of items",
        WorkflowNodeType.TRY_CATCH: "Error handling with try/catch blocks",
    }
    return descriptions.get(node_type, "No description available")


def _create_simple_http_template() -> dict:
    """Create a simple HTTP workflow template."""
    return {
        "id": str(uuid.uuid4()),
        "metadata": {
            "name": "simple-http-workflow",
            "description": "A simple workflow that makes HTTP requests",
            "version": "1.0.0",
            "tags": ["http", "simple"],
            "region": "us-central1"
        },
        "nodes": [
            {
                "id": "start-1",
                "type": "start",
                "position": {"x": 100, "y": 100},
                "config": {"name": "Start"},
                "inputs": [],
                "outputs": ["http-1"]
            },
            {
                "id": "http-1",
                "type": "http_request",
                "position": {"x": 300, "y": 100},
                "config": {
                    "name": "HTTP Request",
                    "description": "Make an HTTP request",
                    "url": "https://api.example.com/data",
                    "method": "GET"
                },
                "inputs": ["start-1"],
                "outputs": ["end-1"]
            },
            {
                "id": "end-1",
                "type": "end",
                "position": {"x": 500, "y": 100},
                "config": {"name": "End"},
                "inputs": ["http-1"],
                "outputs": []
            }
        ],
        "connections": [
            {
                "id": "conn-1",
                "source_node_id": "start-1",
                "target_node_id": "http-1"
            },
            {
                "id": "conn-2",
                "source_node_id": "http-1",
                "target_node_id": "end-1"
            }
        ]
    }


def _create_function_chain_template() -> dict:
    """Create a function chain workflow template."""
    return {
        "id": str(uuid.uuid4()),
        "metadata": {
            "name": "function-chain-workflow",
            "description": "Chain multiple Cloud Functions together",
            "version": "1.0.0",
            "tags": ["functions", "chain"],
            "region": "us-central1"
        },
        "nodes": [
            {
                "id": "start-1",
                "type": "start",
                "position": {"x": 100, "y": 100},
                "config": {"name": "Start"},
                "inputs": [],
                "outputs": ["func-1"]
            },
            {
                "id": "func-1",
                "type": "cloud_function",
                "position": {"x": 300, "y": 100},
                "config": {
                    "name": "Process Data",
                    "description": "Process incoming data",
                    "function_name": "process-data"
                },
                "inputs": ["start-1"],
                "outputs": ["func-2"]
            },
            {
                "id": "func-2",
                "type": "cloud_function",
                "position": {"x": 500, "y": 100},
                "config": {
                    "name": "Transform Data",
                    "description": "Transform processed data",
                    "function_name": "transform-data"
                },
                "inputs": ["func-1"],
                "outputs": ["end-1"]
            },
            {
                "id": "end-1",
                "type": "end",
                "position": {"x": 700, "y": 100},
                "config": {"name": "End"},
                "inputs": ["func-2"],
                "outputs": []
            }
        ],
        "connections": [
            {
                "id": "conn-1",
                "source_node_id": "start-1",
                "target_node_id": "func-1"
            },
            {
                "id": "conn-2",
                "source_node_id": "func-1",
                "target_node_id": "func-2"
            },
            {
                "id": "conn-3",
                "source_node_id": "func-2",
                "target_node_id": "end-1"
            }
        ]
    }


def _create_pubsub_processing_template() -> dict:
    """Create a Pub/Sub processing workflow template."""
    return {
        "id": str(uuid.uuid4()),
        "metadata": {
            "name": "pubsub-processing-workflow",
            "description": "Process messages from Pub/Sub topics",
            "version": "1.0.0",
            "tags": ["pubsub", "messaging"],
            "region": "us-central1"
        },
        "nodes": [
            {
                "id": "start-1",
                "type": "start",
                "position": {"x": 100, "y": 100},
                "config": {"name": "Start"},
                "inputs": [],
                "outputs": ["pubsub-1"]
            },
            {
                "id": "pubsub-1",
                "type": "pubsub_subscribe",
                "position": {"x": 300, "y": 100},
                "config": {
                    "name": "Subscribe to Messages",
                    "description": "Subscribe to incoming messages",
                    "subscription_name": "message-subscription"
                },
                "inputs": ["start-1"],
                "outputs": ["func-1"]
            },
            {
                "id": "func-1",
                "type": "cloud_function",
                "position": {"x": 500, "y": 100},
                "config": {
                    "name": "Process Message",
                    "description": "Process the received message",
                    "function_name": "process-message"
                },
                "inputs": ["pubsub-1"],
                "outputs": ["pubsub-2"]
            },
            {
                "id": "pubsub-2",
                "type": "pubsub_publish",
                "position": {"x": 700, "y": 100},
                "config": {
                    "name": "Publish Result",
                    "description": "Publish processing result",
                    "topic_name": "result-topic"
                },
                "inputs": ["func-1"],
                "outputs": ["end-1"]
            },
            {
                "id": "end-1",
                "type": "end",
                "position": {"x": 900, "y": 100},
                "config": {"name": "End"},
                "inputs": ["pubsub-2"],
                "outputs": []
            }
        ],
        "connections": [
            {
                "id": "conn-1",
                "source_node_id": "start-1",
                "target_node_id": "pubsub-1"
            },
            {
                "id": "conn-2",
                "source_node_id": "pubsub-1",
                "target_node_id": "func-1"
            },
            {
                "id": "conn-3",
                "source_node_id": "func-1",
                "target_node_id": "pubsub-2"
            },
            {
                "id": "conn-4",
                "source_node_id": "pubsub-2",
                "target_node_id": "end-1"
            }
        ]
    }
