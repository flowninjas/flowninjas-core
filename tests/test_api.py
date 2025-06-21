"""Test API endpoints."""

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "flowninjas-core"


def test_api_root():
    """Test API root endpoint."""
    response = client.get("/api/v1/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "FlowNinjas Core API v1"
    assert data["version"] == "0.1.0"


def test_get_node_types():
    """Test get workflow node types endpoint."""
    response = client.get("/api/v1/workflows/node-types")
    assert response.status_code == 200
    data = response.json()
    assert "node_types" in data
    assert len(data["node_types"]) > 0
    
    # Check first node type structure
    node_type = data["node_types"][0]
    assert "type" in node_type
    assert "name" in node_type
    assert "description" in node_type


def test_get_workflow_templates():
    """Test get workflow templates endpoint."""
    response = client.get("/api/v1/workflows/templates")
    assert response.status_code == 200
    data = response.json()
    assert "templates" in data
    assert len(data["templates"]) > 0
    
    # Check first template structure
    template = data["templates"][0]
    assert "id" in template
    assert "name" in template
    assert "description" in template
    assert "template" in template


def test_validate_workflow_missing_nodes():
    """Test workflow validation with missing nodes."""
    workflow_data = {
        "id": "test-workflow",
        "metadata": {
            "name": "test-workflow",
            "description": "Test workflow"
        },
        "nodes": [],
        "connections": []
    }
    
    response = client.post("/api/v1/workflows/validate", json=workflow_data)
    assert response.status_code == 200
    data = response.json()
    assert data["is_valid"] is False
    assert len(data["issues"]) > 0


def test_preview_workflow_yaml():
    """Test workflow YAML preview."""
    workflow_data = {
        "id": "test-workflow",
        "metadata": {
            "name": "test-workflow",
            "description": "Test workflow"
        },
        "nodes": [
            {
                "id": "start-1",
                "type": "start",
                "position": {"x": 100, "y": 100},
                "config": {"name": "Start"},
                "inputs": [],
                "outputs": ["end-1"]
            },
            {
                "id": "end-1",
                "type": "end",
                "position": {"x": 300, "y": 100},
                "config": {"name": "End"},
                "inputs": ["start-1"],
                "outputs": []
            }
        ],
        "connections": [
            {
                "id": "conn-1",
                "source_node_id": "start-1",
                "target_node_id": "end-1"
            }
        ]
    }
    
    response = client.post("/api/v1/workflows/preview", json=workflow_data)
    assert response.status_code == 200
    data = response.json()
    assert data["workflow_id"] == "test-workflow"
    assert "yaml_content" in data
    assert len(data["validation_issues"]) == 0
