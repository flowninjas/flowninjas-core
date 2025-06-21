"""AI service for code generation using Google Gemini."""

import json
import time
from typing import Any, Dict, List, Optional

import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

from app.core.config import get_settings
from app.core.logging import LoggerMixin
from app.models.workflow import Workflow, WorkflowNode, WorkflowNodeType


class AIService(LoggerMixin):
    """Service for AI-powered code generation."""
    
    def __init__(self):
        """Initialize the AI service."""
        self.settings = get_settings()
        self._configure_gemini()
    
    def _configure_gemini(self) -> None:
        """Configure Google Gemini API."""
        if not self.settings.GEMINI_API_KEY:
            self.logger.warning("GEMINI_API_KEY not configured")
            return
        
        genai.configure(api_key=self.settings.GEMINI_API_KEY)
        
        # Configure safety settings
        self.safety_settings = {
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        }
        
        # Initialize the model
        self.model = genai.GenerativeModel(
            model_name=self.settings.GEMINI_MODEL,
            safety_settings=self.safety_settings,
        )
    
    async def generate_workflow_yaml(self, workflow: Workflow) -> str:
        """Generate Google Cloud Workflow YAML from workflow definition."""
        start_time = time.time()
        
        try:
            prompt = self._build_workflow_prompt(workflow)
            
            self.logger.info("Generating workflow YAML", workflow_id=workflow.id)
            
            response = await self._generate_content(prompt)
            
            # Extract YAML from response
            yaml_content = self._extract_yaml_from_response(response)
            
            generation_time = time.time() - start_time
            self.logger.info(
                "Workflow YAML generated successfully",
                workflow_id=workflow.id,
                generation_time=generation_time
            )
            
            return yaml_content
            
        except Exception as e:
            self.logger.error(
                "Failed to generate workflow YAML",
                workflow_id=workflow.id,
                error=str(e)
            )
            raise
    
    async def generate_cloud_function_code(self, node: WorkflowNode) -> str:
        """Generate Cloud Function code for a workflow node."""
        if node.type != WorkflowNodeType.CLOUD_FUNCTION:
            raise ValueError("Node must be of type CLOUD_FUNCTION")
        
        try:
            prompt = self._build_function_prompt(node)
            
            self.logger.info("Generating Cloud Function code", node_id=node.id)
            
            response = await self._generate_content(prompt)
            
            # Extract Python code from response
            code = self._extract_code_from_response(response, "python")
            
            self.logger.info("Cloud Function code generated", node_id=node.id)
            
            return code
            
        except Exception as e:
            self.logger.error(
                "Failed to generate Cloud Function code",
                node_id=node.id,
                error=str(e)
            )
            raise
    
    async def generate_cloud_run_dockerfile(self, node: WorkflowNode) -> str:
        """Generate Dockerfile for Cloud Run service."""
        if node.type != WorkflowNodeType.CLOUD_RUN:
            raise ValueError("Node must be of type CLOUD_RUN")
        
        try:
            prompt = self._build_dockerfile_prompt(node)
            
            self.logger.info("Generating Dockerfile", node_id=node.id)
            
            response = await self._generate_content(prompt)
            
            # Extract Dockerfile content from response
            dockerfile = self._extract_code_from_response(response, "dockerfile")
            
            self.logger.info("Dockerfile generated", node_id=node.id)
            
            return dockerfile
            
        except Exception as e:
            self.logger.error(
                "Failed to generate Dockerfile",
                node_id=node.id,
                error=str(e)
            )
            raise
    
    async def enhance_node_configuration(self, node: WorkflowNode) -> Dict[str, Any]:
        """Use AI to enhance node configuration based on description and prompt."""
        try:
            prompt = self._build_enhancement_prompt(node)
            
            self.logger.info("Enhancing node configuration", node_id=node.id)
            
            response = await self._generate_content(prompt)
            
            # Extract JSON configuration from response
            enhanced_config = self._extract_json_from_response(response)
            
            self.logger.info("Node configuration enhanced", node_id=node.id)
            
            return enhanced_config
            
        except Exception as e:
            self.logger.error(
                "Failed to enhance node configuration",
                node_id=node.id,
                error=str(e)
            )
            raise
    
    async def _generate_content(self, prompt: str) -> str:
        """Generate content using Gemini API."""
        if not hasattr(self, 'model'):
            raise RuntimeError("Gemini API not configured")
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            self.logger.error("Gemini API error", error=str(e))
            raise
    
    def _build_workflow_prompt(self, workflow: Workflow) -> str:
        """Build prompt for workflow YAML generation."""
        nodes_description = []
        for node in workflow.nodes:
            node_desc = f"- {node.type.value}: {node.config.name}"
            if node.config.description:
                node_desc += f" - {node.config.description}"
            if node.config.ai_prompt:
                node_desc += f" (AI Prompt: {node.config.ai_prompt})"
            nodes_description.append(node_desc)
        
        return f"""
Generate a Google Cloud Workflow YAML definition for the following workflow:

Workflow Name: {workflow.metadata.name}
Description: {workflow.metadata.description or 'No description provided'}
Project ID: {workflow.metadata.project_id or 'your-project-id'}
Region: {workflow.metadata.region}

Nodes:
{chr(10).join(nodes_description)}

Requirements:
1. Generate valid Google Cloud Workflow YAML syntax
2. Include proper error handling and logging
3. Use appropriate Google Cloud services based on node types
4. Include timeout and retry configurations where appropriate
5. Follow Google Cloud Workflow best practices
6. Include comments explaining each step

Please provide only the YAML content without any additional explanation.
"""
    
    def _build_function_prompt(self, node: WorkflowNode) -> str:
        """Build prompt for Cloud Function code generation."""
        return f"""
Generate Python code for a Google Cloud Function with the following specifications:

Function Name: {node.config.function_name or node.config.name}
Description: {node.config.description or 'No description provided'}
AI Prompt: {node.config.ai_prompt or 'No specific requirements'}

Environment Variables: {json.dumps(node.config.env_vars or {}, indent=2)}
Memory: {node.config.memory or '256MB'}
Timeout: {node.config.timeout or '60s'}

Requirements:
1. Generate a complete Cloud Function with main.py and requirements.txt
2. Include proper error handling and logging
3. Use Google Cloud client libraries where appropriate
4. Follow Python best practices and PEP 8
5. Include input validation
6. Add comprehensive docstrings

Please provide the Python code for main.py only, without additional explanation.
"""
    
    def _build_dockerfile_prompt(self, node: WorkflowNode) -> str:
        """Build prompt for Dockerfile generation."""
        return f"""
Generate a Dockerfile for a Google Cloud Run service with the following specifications:

Service Name: {node.config.service_name or node.config.name}
Description: {node.config.description or 'No description provided'}
AI Prompt: {node.config.ai_prompt or 'No specific requirements'}

Environment Variables: {json.dumps(node.config.env_vars or {}, indent=2)}
Memory: {node.config.memory or '512Mi'}
CPU: {node.config.cpu or '1000m'}

Requirements:
1. Use an appropriate base image (Python, Node.js, etc.)
2. Include security best practices
3. Optimize for Cloud Run deployment
4. Include health check endpoint
5. Follow multi-stage build if beneficial
6. Minimize image size

Please provide only the Dockerfile content without additional explanation.
"""
    
    def _build_enhancement_prompt(self, node: WorkflowNode) -> str:
        """Build prompt for node configuration enhancement."""
        return f"""
Enhance the configuration for a workflow node based on the following information:

Node Type: {node.type.value}
Current Name: {node.config.name}
Description: {node.config.description or 'No description provided'}
AI Prompt: {node.config.ai_prompt or 'No specific requirements'}

Current Configuration: {json.dumps(node.config.dict(), indent=2)}

Please provide enhanced configuration suggestions in JSON format including:
1. Improved resource allocations (memory, CPU, timeout)
2. Recommended environment variables
3. Security considerations
4. Performance optimizations
5. Best practice configurations

Return only valid JSON without additional explanation.
"""
    
    def _extract_yaml_from_response(self, response: str) -> str:
        """Extract YAML content from AI response."""
        # Look for YAML code blocks
        if "```yaml" in response:
            start = response.find("```yaml") + 7
            end = response.find("```", start)
            return response[start:end].strip()
        elif "```" in response:
            start = response.find("```") + 3
            end = response.find("```", start)
            return response[start:end].strip()
        else:
            # Return the entire response if no code blocks found
            return response.strip()
    
    def _extract_code_from_response(self, response: str, language: str) -> str:
        """Extract code content from AI response."""
        # Look for language-specific code blocks
        code_block = f"```{language}"
        if code_block in response:
            start = response.find(code_block) + len(code_block)
            end = response.find("```", start)
            return response[start:end].strip()
        elif "```" in response:
            start = response.find("```") + 3
            end = response.find("```", start)
            return response[start:end].strip()
        else:
            # Return the entire response if no code blocks found
            return response.strip()
    
    def _extract_json_from_response(self, response: str) -> Dict[str, Any]:
        """Extract JSON content from AI response."""
        # Look for JSON code blocks
        if "```json" in response:
            start = response.find("```json") + 7
            end = response.find("```", start)
            json_str = response[start:end].strip()
        elif "```" in response:
            start = response.find("```") + 3
            end = response.find("```", start)
            json_str = response[start:end].strip()
        else:
            json_str = response.strip()
        
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            # If JSON parsing fails, return the original response as a string
            return {"raw_response": json_str}
