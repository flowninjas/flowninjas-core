#!/usr/bin/env python3
"""
Demo script to test FlowNinjas Core API functionality.
"""

import asyncio
import json
import uuid
from datetime import datetime

from app.models.workflow import (
    Workflow,
    WorkflowMetadata,
    WorkflowNode,
    WorkflowNodeConfig,
    WorkflowNodePosition,
    WorkflowNodeType,
    WorkflowConnection,
    WorkflowGenerationRequest,
)
from app.services.workflow_service import WorkflowService


async def create_sample_workflow() -> Workflow:
    """Create a sample workflow for testing."""
    workflow_id = str(uuid.uuid4())
    
    # Create workflow metadata
    metadata = WorkflowMetadata(
        name="demo-workflow",
        description="A demo workflow for testing FlowNinjas Core",
        project_id="demo-project",
        region="us-central1",
        author="FlowNinjas Demo"
    )
    
    # Create workflow nodes
    nodes = [
        WorkflowNode(
            id="start-1",
            type=WorkflowNodeType.START,
            position=WorkflowNodePosition(x=100, y=100),
            config=WorkflowNodeConfig(name="Start"),
            outputs=["http-1"]
        ),
        WorkflowNode(
            id="http-1",
            type=WorkflowNodeType.HTTP_REQUEST,
            position=WorkflowNodePosition(x=300, y=100),
            config=WorkflowNodeConfig(
                name="Fetch Data",
                description="Fetch data from external API",
                url="https://jsonplaceholder.typicode.com/posts/1",
                method="GET"
            ),
            inputs=["start-1"],
            outputs=["func-1"]
        ),
        WorkflowNode(
            id="func-1",
            type=WorkflowNodeType.CLOUD_FUNCTION,
            position=WorkflowNodePosition(x=500, y=100),
            config=WorkflowNodeConfig(
                name="Process Data",
                description="Process the fetched data",
                function_name="process-data",
                ai_prompt="Create a function that processes JSON data and extracts key information"
            ),
            inputs=["http-1"],
            outputs=["end-1"]
        ),
        WorkflowNode(
            id="end-1",
            type=WorkflowNodeType.END,
            position=WorkflowNodePosition(x=700, y=100),
            config=WorkflowNodeConfig(name="End"),
            inputs=["func-1"]
        )
    ]
    
    # Create connections
    connections = [
        WorkflowConnection(
            id="conn-1",
            source_node_id="start-1",
            target_node_id="http-1"
        ),
        WorkflowConnection(
            id="conn-2",
            source_node_id="http-1",
            target_node_id="func-1"
        ),
        WorkflowConnection(
            id="conn-3",
            source_node_id="func-1",
            target_node_id="end-1"
        )
    ]
    
    return Workflow(
        id=workflow_id,
        metadata=metadata,
        nodes=nodes,
        connections=connections
    )


async def demo_workflow_generation():
    """Demonstrate workflow code generation."""
    print("🚀 FlowNinjas Core Demo")
    print("=" * 50)
    
    # Create workflow service
    workflow_service = WorkflowService()
    
    # Create sample workflow
    print("📝 Creating sample workflow...")
    workflow = await create_sample_workflow()
    print(f"✅ Created workflow: {workflow.metadata.name}")
    print(f"   - ID: {workflow.id}")
    print(f"   - Nodes: {len(workflow.nodes)}")
    print(f"   - Connections: {len(workflow.connections)}")
    
    # Validate workflow
    print("\n🔍 Validating workflow...")
    validation_issues = workflow_service.validate_workflow(workflow)
    if validation_issues:
        print("❌ Validation issues found:")
        for issue in validation_issues:
            print(f"   - {issue}")
        return
    else:
        print("✅ Workflow validation passed")
    
    # Generate workflow code (without AI for demo)
    print("\n⚙️ Generating workflow code...")
    request = WorkflowGenerationRequest(
        workflow=workflow,
        target_format="yaml",
        include_deployment=True,
        ai_enhance=False  # Set to False for demo without API key
    )
    
    try:
        response = await workflow_service.generate_workflow_code(request)
        print("✅ Code generation completed!")
        print(f"   - Generation time: {response.generation_time:.2f}s")
        print(f"   - Generated files: {len(response.generated_files)}")
        
        # Display generated files
        print("\n📁 Generated files:")
        for filename in response.generated_files.keys():
            print(f"   - {filename}")
        
        # Show workflow YAML preview
        if "workflow.yaml" in response.generated_files:
            print("\n📄 Workflow YAML Preview:")
            print("-" * 30)
            yaml_content = response.generated_files["workflow.yaml"]
            # Show first 20 lines
            lines = yaml_content.split('\n')[:20]
            for line in lines:
                print(f"   {line}")
            if len(yaml_content.split('\n')) > 20:
                print("   ... (truncated)")
        
        # Save files to local directory
        print("\n💾 Saving files to local directory...")
        output_path = await workflow_service.save_workflow_files(
            workflow_id=workflow.id,
            files=response.generated_files
        )
        print(f"✅ Files saved to: {output_path}")
        
        # Show deployment configs if available
        if response.deployment_configs:
            print("\n🚀 Deployment configurations:")
            for config_name in response.deployment_configs.keys():
                print(f"   - {config_name}")
        
        print("\n🎉 Demo completed successfully!")
        print(f"📂 Check the generated files in: {output_path}")
        
    except Exception as e:
        print(f"❌ Error during code generation: {str(e)}")
        print("💡 Note: AI features require GEMINI_API_KEY to be configured")


async def demo_basic_functionality():
    """Demonstrate basic functionality without AI."""
    print("\n🔧 Testing basic functionality...")
    
    workflow_service = WorkflowService()
    workflow = await create_sample_workflow()
    
    # Test YAML generation without AI
    print("📝 Generating basic YAML...")
    yaml_content = workflow_service._generate_basic_workflow_yaml(workflow)
    print("✅ Basic YAML generated")
    
    # Test node validation
    print("🔍 Testing node validation...")
    for node in workflow.nodes:
        issues = workflow_service._validate_node_config(node)
        if issues:
            print(f"   - {node.config.name}: {len(issues)} issues")
        else:
            print(f"   - {node.config.name}: ✅ Valid")


if __name__ == "__main__":
    print("Starting FlowNinjas Core Demo...")
    asyncio.run(demo_workflow_generation())
    asyncio.run(demo_basic_functionality())
