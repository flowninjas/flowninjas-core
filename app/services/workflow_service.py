"""Workflow management service."""

import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from app.core.config import get_settings
from app.core.logging import LoggerMixin
from app.models.workflow import (
    Workflow,
    WorkflowGenerationRequest,
    WorkflowGenerationResponse,
    WorkflowNode,
    WorkflowNodeType,
)
from app.services.ai_service import AIService


class WorkflowService(LoggerMixin):
    """Service for workflow management and code generation."""
    
    def __init__(self):
        """Initialize the workflow service."""
        self.settings = get_settings()
        self.ai_service = AIService()
    
    async def generate_workflow_code(
        self, request: WorkflowGenerationRequest
    ) -> WorkflowGenerationResponse:
        """Generate code and configurations for a workflow."""
        start_time = datetime.utcnow()
        workflow = request.workflow
        
        self.logger.info(
            "Starting workflow code generation",
            workflow_id=workflow.id,
            workflow_name=workflow.metadata.name
        )
        
        try:
            generated_files = {}
            deployment_configs = {}
            ai_suggestions = []
            
            # Generate main workflow YAML
            if request.ai_enhance:
                workflow_yaml = await self.ai_service.generate_workflow_yaml(workflow)
            else:
                workflow_yaml = self._generate_basic_workflow_yaml(workflow)
            
            generated_files["workflow.yaml"] = workflow_yaml
            
            # Generate code for each node
            for node in workflow.nodes:
                if node.type == WorkflowNodeType.CLOUD_FUNCTION:
                    function_code = await self._generate_function_files(node, request.ai_enhance)
                    generated_files.update(function_code)
                
                elif node.type == WorkflowNodeType.CLOUD_RUN:
                    service_files = await self._generate_service_files(node, request.ai_enhance)
                    generated_files.update(service_files)
            
            # Generate deployment configurations
            if request.include_deployment:
                deployment_configs = self._generate_deployment_configs(workflow)
            
            # Generate AI suggestions if enabled
            if request.ai_enhance:
                ai_suggestions = await self._generate_ai_suggestions(workflow)
            
            # Calculate generation time
            generation_time = (datetime.utcnow() - start_time).total_seconds()
            
            response = WorkflowGenerationResponse(
                workflow_id=workflow.id,
                generated_files=generated_files,
                deployment_configs=deployment_configs,
                ai_suggestions=ai_suggestions,
                generation_time=generation_time,
            )
            
            self.logger.info(
                "Workflow code generation completed",
                workflow_id=workflow.id,
                files_count=len(generated_files),
                generation_time=generation_time
            )
            
            return response
            
        except Exception as e:
            self.logger.error(
                "Failed to generate workflow code",
                workflow_id=workflow.id,
                error=str(e)
            )
            raise
    
    async def save_workflow_files(
        self, workflow_id: str, files: Dict[str, str], output_path: Optional[str] = None
    ) -> str:
        """Save generated workflow files to local directory."""
        if output_path is None:
            output_path = os.path.join(self.settings.WORKFLOWS_STORAGE_PATH, workflow_id)
        
        # Create output directory
        Path(output_path).mkdir(parents=True, exist_ok=True)
        
        self.logger.info(
            "Saving workflow files",
            workflow_id=workflow_id,
            output_path=output_path,
            files_count=len(files)
        )
        
        try:
            for filename, content in files.items():
                file_path = os.path.join(output_path, filename)
                
                # Create subdirectories if needed
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                self.logger.debug("File saved", file_path=file_path)
            
            self.logger.info(
                "All workflow files saved successfully",
                workflow_id=workflow_id,
                output_path=output_path
            )
            
            return output_path
            
        except Exception as e:
            self.logger.error(
                "Failed to save workflow files",
                workflow_id=workflow_id,
                error=str(e)
            )
            raise
    
    def validate_workflow(self, workflow: Workflow) -> List[str]:
        """Validate workflow definition and return list of issues."""
        issues = []
        
        # Check for required nodes
        start_nodes = [n for n in workflow.nodes if n.type == WorkflowNodeType.START]
        end_nodes = [n for n in workflow.nodes if n.type == WorkflowNodeType.END]
        
        if len(start_nodes) != 1:
            issues.append("Workflow must have exactly one START node")
        
        if len(end_nodes) == 0:
            issues.append("Workflow must have at least one END node")
        
        # Check node connections
        node_ids = {node.id for node in workflow.nodes}
        connection_sources = {conn.source_node_id for conn in workflow.connections}
        connection_targets = {conn.target_node_id for conn in workflow.connections}
        
        # Check for orphaned nodes (except START and END)
        for node in workflow.nodes:
            if node.type not in [WorkflowNodeType.START, WorkflowNodeType.END]:
                if node.id not in connection_targets and node.id not in connection_sources:
                    issues.append(f"Node '{node.config.name}' is not connected")
        
        # Validate node configurations
        for node in workflow.nodes:
            node_issues = self._validate_node_config(node)
            issues.extend(node_issues)
        
        return issues
    
    def _validate_node_config(self, node: WorkflowNode) -> List[str]:
        """Validate individual node configuration."""
        issues = []
        
        if node.type == WorkflowNodeType.CLOUD_FUNCTION:
            if not node.config.function_name:
                issues.append(f"Cloud Function node '{node.config.name}' missing function_name")
        
        elif node.type == WorkflowNodeType.CLOUD_RUN:
            if not node.config.service_name:
                issues.append(f"Cloud Run node '{node.config.name}' missing service_name")
        
        elif node.type == WorkflowNodeType.PUBSUB_PUBLISH:
            if not node.config.topic_name:
                issues.append(f"Pub/Sub Publish node '{node.config.name}' missing topic_name")
        
        elif node.type == WorkflowNodeType.PUBSUB_SUBSCRIBE:
            if not node.config.subscription_name:
                issues.append(f"Pub/Sub Subscribe node '{node.config.name}' missing subscription_name")
        
        elif node.type == WorkflowNodeType.HTTP_REQUEST:
            if not node.config.url:
                issues.append(f"HTTP Request node '{node.config.name}' missing url")
        
        elif node.type == WorkflowNodeType.CONDITION:
            if not node.config.condition:
                issues.append(f"Condition node '{node.config.name}' missing condition")
        
        return issues
    
    def _generate_basic_workflow_yaml(self, workflow: Workflow) -> str:
        """Generate basic workflow YAML without AI enhancement."""
        workflow_def = {
            "main": {
                "steps": []
            }
        }
        
        # Convert nodes to workflow steps
        for i, node in enumerate(workflow.nodes):
            if node.type == WorkflowNodeType.START:
                continue
            elif node.type == WorkflowNodeType.END:
                workflow_def["main"]["steps"].append({
                    f"end_step_{i}": {
                        "return": "${result}"
                    }
                })
            else:
                step = self._node_to_workflow_step(node)
                workflow_def["main"]["steps"].append({f"step_{i}": step})
        
        return yaml.dump(workflow_def, default_flow_style=False, sort_keys=False)
    
    def _node_to_workflow_step(self, node: WorkflowNode) -> Dict[str, Any]:
        """Convert a workflow node to a workflow step definition."""
        if node.type == WorkflowNodeType.CLOUD_FUNCTION:
            return {
                "call": "googleapis.cloudfunctions.v1.projects.locations.functions.call",
                "args": {
                    "name": f"projects/{self.settings.GOOGLE_CLOUD_PROJECT}/locations/{node.config.function_name}",
                    "data": "${input}"
                },
                "result": "function_result"
            }
        
        elif node.type == WorkflowNodeType.HTTP_REQUEST:
            return {
                "call": "http.request",
                "args": {
                    "url": node.config.url,
                    "method": node.config.method or "GET",
                    "headers": node.config.headers or {},
                    "body": node.config.body or {}
                },
                "result": "http_result"
            }
        
        elif node.type == WorkflowNodeType.CONDITION:
            return {
                "switch": [
                    {
                        "condition": node.config.condition,
                        "next": "continue"
                    }
                ],
                "next": "end"
            }
        
        elif node.type == WorkflowNodeType.DELAY:
            return {
                "call": "sys.sleep",
                "args": {
                    "seconds": node.config.delay_seconds or 1
                }
            }
        
        else:
            return {
                "assign": [
                    {"result": f"Processed {node.config.name}"}
                ]
            }
    
    async def _generate_function_files(
        self, node: WorkflowNode, ai_enhance: bool
    ) -> Dict[str, str]:
        """Generate Cloud Function files for a node."""
        files = {}
        
        function_name = node.config.function_name or node.config.name.lower().replace(' ', '_')
        
        if ai_enhance:
            # Use AI to generate function code
            main_py = await self.ai_service.generate_cloud_function_code(node)
        else:
            # Generate basic function template
            main_py = self._generate_basic_function_code(node)
        
        files[f"functions/{function_name}/main.py"] = main_py
        files[f"functions/{function_name}/requirements.txt"] = self._generate_function_requirements()
        
        return files
    
    async def _generate_service_files(
        self, node: WorkflowNode, ai_enhance: bool
    ) -> Dict[str, str]:
        """Generate Cloud Run service files for a node."""
        files = {}
        
        service_name = node.config.service_name or node.config.name.lower().replace(' ', '_')
        
        if ai_enhance:
            # Use AI to generate Dockerfile
            dockerfile = await self.ai_service.generate_cloud_run_dockerfile(node)
        else:
            # Generate basic Dockerfile template
            dockerfile = self._generate_basic_dockerfile(node)
        
        files[f"services/{service_name}/Dockerfile"] = dockerfile
        files[f"services/{service_name}/main.py"] = self._generate_basic_service_code(node)
        files[f"services/{service_name}/requirements.txt"] = self._generate_service_requirements()
        
        return files
    
    def _generate_basic_function_code(self, node: WorkflowNode) -> str:
        """Generate basic Cloud Function code template."""
        function_name = node.config.function_name or node.config.name.lower().replace(' ', '_')
        
        return f'''"""
Cloud Function: {node.config.name}
Description: {node.config.description or 'Generated Cloud Function'}
"""

import json
import logging
from typing import Any, Dict

import functions_framework


@functions_framework.http
def {function_name}(request):
    """HTTP Cloud Function entry point."""
    logging.info(f"Function {function_name} triggered")
    
    try:
        # Parse request data
        if request.method == 'POST':
            request_json = request.get_json(silent=True)
            if request_json is None:
                return {{"error": "Invalid JSON in request"}}, 400
        else:
            request_json = {{}}
        
        # Process the request
        result = process_request(request_json)
        
        logging.info(f"Function {function_name} completed successfully")
        return {{"result": result, "status": "success"}}
        
    except Exception as e:
        logging.error(f"Function {function_name} failed: {{str(e)}}")
        return {{"error": str(e), "status": "error"}}, 500


def process_request(data: Dict[str, Any]) -> Dict[str, Any]:
    """Process the function request."""
    # TODO: Implement your business logic here
    return {{
        "message": "Function executed successfully",
        "input_data": data,
        "timestamp": "{{}}".format(__import__('datetime').datetime.utcnow().isoformat())
    }}
'''
    
    def _generate_basic_service_code(self, node: WorkflowNode) -> str:
        """Generate basic Cloud Run service code template."""
        service_name = node.config.service_name or node.config.name.lower().replace(' ', '_')
        
        return f'''"""
Cloud Run Service: {node.config.name}
Description: {node.config.description or 'Generated Cloud Run Service'}
"""

import json
import logging
import os
from typing import Any, Dict

from flask import Flask, request, jsonify

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({{"status": "healthy", "service": "{service_name}"}})


@app.route('/', methods=['POST'])
def process_request():
    """Main request processing endpoint."""
    logger.info(f"Service {service_name} received request")
    
    try:
        # Parse request data
        data = request.get_json() or {{}}
        
        # Process the request
        result = handle_request(data)
        
        logger.info(f"Service {service_name} completed successfully")
        return jsonify({{"result": result, "status": "success"}})
        
    except Exception as e:
        logger.error(f"Service {service_name} failed: {{str(e)}}")
        return jsonify({{"error": str(e), "status": "error"}}), 500


def handle_request(data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle the service request."""
    # TODO: Implement your business logic here
    return {{
        "message": "Service executed successfully",
        "input_data": data,
        "timestamp": "{{}}".format(__import__('datetime').datetime.utcnow().isoformat())
    }}


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
'''
    
    def _generate_basic_dockerfile(self, node: WorkflowNode) -> str:
        """Generate basic Dockerfile template."""
        return '''# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8080

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Run the application
CMD ["python", "main.py"]
'''
    
    def _generate_function_requirements(self) -> str:
        """Generate requirements.txt for Cloud Functions."""
        return '''functions-framework>=3.4.0
google-cloud-logging>=3.8.0
'''
    
    def _generate_service_requirements(self) -> str:
        """Generate requirements.txt for Cloud Run services."""
        return '''Flask>=2.3.0
gunicorn>=21.2.0
google-cloud-logging>=3.8.0
'''
    
    def _generate_deployment_configs(self, workflow: Workflow) -> Dict[str, str]:
        """Generate deployment configuration files."""
        configs = {}
        
        # Generate Cloud Build configuration
        configs["cloudbuild.yaml"] = self._generate_cloudbuild_config(workflow)
        
        # Generate Terraform configuration
        configs["terraform/main.tf"] = self._generate_terraform_config(workflow)
        
        # Generate deployment script
        configs["deploy.sh"] = self._generate_deployment_script(workflow)
        
        return configs
    
    def _generate_cloudbuild_config(self, workflow: Workflow) -> str:
        """Generate Cloud Build configuration."""
        return f'''steps:
  # Deploy Cloud Functions
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: 'bash'
    args:
      - '-c'
      - |
        for func_dir in functions/*/; do
          func_name=$(basename "$func_dir")
          gcloud functions deploy "$func_name" \\
            --source="$func_dir" \\
            --runtime=python311 \\
            --trigger=http \\
            --allow-unauthenticated \\
            --region={workflow.metadata.region}
        done

  # Build and deploy Cloud Run services
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/workflow-service', './services/']
  
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/workflow-service']
  
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: 'gcloud'
    args:
      - 'run'
      - 'deploy'
      - 'workflow-service'
      - '--image=gcr.io/$PROJECT_ID/workflow-service'
      - '--region={workflow.metadata.region}'
      - '--allow-unauthenticated'

  # Deploy workflow
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: 'gcloud'
    args:
      - 'workflows'
      - 'deploy'
      - '{workflow.metadata.name}'
      - '--source=workflow.yaml'
      - '--location={workflow.metadata.region}'

options:
  logging: CLOUD_LOGGING_ONLY
'''
    
    def _generate_terraform_config(self, workflow: Workflow) -> str:
        """Generate Terraform configuration."""
        return f'''terraform {{
  required_providers {{
    google = {{
      source  = "hashicorp/google"
      version = "~> 4.0"
    }}
  }}
}}

provider "google" {{
  project = var.project_id
  region  = "{workflow.metadata.region}"
}}

variable "project_id" {{
  description = "Google Cloud Project ID"
  type        = string
}}

# Deploy the workflow
resource "google_workflows_workflow" "{workflow.metadata.name.lower().replace('-', '_')}" {{
  name            = "{workflow.metadata.name}"
  region          = "{workflow.metadata.region}"
  description     = "{workflow.metadata.description or 'Generated workflow'}"
  source_contents = file("../workflow.yaml")
}}
'''
    
    def _generate_deployment_script(self, workflow: Workflow) -> str:
        """Generate deployment script."""
        return f'''#!/bin/bash

# Deployment script for {workflow.metadata.name}
set -e

PROJECT_ID="${{1:-{workflow.metadata.project_id or 'your-project-id'}}}"
REGION="{workflow.metadata.region}"

echo "Deploying workflow: {workflow.metadata.name}"
echo "Project ID: $PROJECT_ID"
echo "Region: $REGION"

# Set the project
gcloud config set project "$PROJECT_ID"

# Deploy Cloud Functions
echo "Deploying Cloud Functions..."
for func_dir in functions/*/; do
  if [ -d "$func_dir" ]; then
    func_name=$(basename "$func_dir")
    echo "Deploying function: $func_name"
    gcloud functions deploy "$func_name" \\
      --source="$func_dir" \\
      --runtime=python311 \\
      --trigger=http \\
      --allow-unauthenticated \\
      --region="$REGION"
  fi
done

# Deploy Cloud Run services
echo "Deploying Cloud Run services..."
for service_dir in services/*/; do
  if [ -d "$service_dir" ]; then
    service_name=$(basename "$service_dir")
    echo "Deploying service: $service_name"
    gcloud run deploy "$service_name" \\
      --source="$service_dir" \\
      --region="$REGION" \\
      --allow-unauthenticated
  fi
done

# Deploy the workflow
echo "Deploying workflow..."
gcloud workflows deploy "{workflow.metadata.name}" \\
  --source=workflow.yaml \\
  --location="$REGION"

echo "Deployment completed successfully!"
'''
    
    async def _generate_ai_suggestions(self, workflow: Workflow) -> List[str]:
        """Generate AI suggestions for workflow improvement."""
        suggestions = []
        
        try:
            # Analyze workflow for potential improvements
            for node in workflow.nodes:
                if node.config.ai_prompt:
                    enhanced_config = await self.ai_service.enhance_node_configuration(node)
                    if "suggestions" in enhanced_config:
                        suggestions.extend(enhanced_config["suggestions"])
            
            # Add general suggestions
            suggestions.extend([
                "Consider adding error handling and retry logic",
                "Implement proper logging and monitoring",
                "Add input validation for all endpoints",
                "Consider using Cloud Monitoring for observability",
                "Implement proper authentication and authorization",
            ])
            
        except Exception as e:
            self.logger.warning("Failed to generate AI suggestions", error=str(e))
        
        return suggestions[:10]  # Limit to top 10 suggestions
