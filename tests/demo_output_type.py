#!/usr/bin/env python3
"""
Demo script to showcase the new output_type parameter.

This script demonstrates how to use the makeup_prompt API with both
Markdown (default) and XML output formats.
"""

import requests
import json

API_URL = "http://localhost:8000/makeup_prompt"

def demo_xml_output():
    """Test XML output format."""
    print("=" * 60)
    print("Demo 1: XML Output Format")
    print("=" * 60)

    payload = {
        "input_prompt": "帮我写一篇关于人工智能发展的深度文章",
        "output_type": "xml"
    }

    print(f"\nRequest:")
    print(json.dumps(payload, indent=2, ensure_ascii=False))

    print("\n" + "-" * 60)
    print("Response (XML format):")
    print("-" * 60)

    try:
        response = requests.post(API_URL, json=payload)
        if response.status_code == 200:
            data = response.json()
            print(f"\nSkill used: {data['skill_used']}")
            print(f"\nOptimized prompt:\n{data['output_prompt']}")
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
    except requests.exceptions.ConnectionError:
        print("\n⚠️  Server not running. Start the server with:")
        print("   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")


def demo_markdown_output():
    """Test default Markdown output format."""
    print("\n\n" + "=" * 60)
    print("Demo 2: Markdown Output Format (default)")
    print("=" * 60)

    # Explicit markdown
    payload_explicit = {
        "input_prompt": "帮我写一篇关于人工智能发展的深度文章",
        "output_type": "markdown"
    }

    print(f"\nRequest (explicit markdown):")
    print(json.dumps(payload_explicit, indent=2, ensure_ascii=False))

    print("\n" + "-" * 60)
    print("Response (Markdown format):")
    print("-" * 60)

    try:
        response = requests.post(API_URL, json=payload_explicit)
        if response.status_code == 200:
            data = response.json()
            print(f"\nSkill used: {data['skill_used']}")
            print(f"\nOptimized prompt:\n{data['output_prompt']}")
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
    except requests.exceptions.ConnectionError:
        print("\n⚠️  Server not running. Start the server with:")
        print("   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")


def demo_default_behavior():
    """Test default behavior (no output_type specified)."""
    print("\n\n" + "=" * 60)
    print("Demo 3: Default Behavior (backward compatible)")
    print("=" * 60)

    payload_default = {
        "input_prompt": "帮我写一篇关于人工智能发展的深度文章"
        # No output_type specified - should default to markdown
    }

    print(f"\nRequest (no output_type - defaults to markdown):")
    print(json.dumps(payload_default, indent=2, ensure_ascii=False))

    print("\n" + "-" * 60)
    print("Response (Markdown format by default):")
    print("-" * 60)

    try:
        response = requests.post(API_URL, json=payload_default)
        if response.status_code == 200:
            data = response.json()
            print(f"\nSkill used: {data['skill_used']}")
            print(f"\nOptimized prompt:\n{data['output_prompt']}")
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
    except requests.exceptions.ConnectionError:
        print("\n⚠️  Server not running. Start the server with:")
        print("   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")


def demo_invalid_output_type():
    """Test invalid output_type (should be rejected)."""
    print("\n\n" + "=" * 60)
    print("Demo 4: Invalid Output Type (validation)")
    print("=" * 60)

    payload_invalid = {
        "input_prompt": "test",
        "output_type": "invalid_format"
    }

    print(f"\nRequest (invalid output_type):")
    print(json.dumps(payload_invalid, indent=2, ensure_ascii=False))

    print("\n" + "-" * 60)
    print("Response (422 Validation Error):")
    print("-" * 60)

    try:
        response = requests.post(API_URL, json=payload_invalid)
        print(f"\nStatus code: {response.status_code}")
        if response.status_code == 422:
            print("✓ Correctly rejected invalid output_type")
        else:
            print(f"Unexpected response: {response.text}")
    except requests.exceptions.ConnectionError:
        print("\n⚠️  Server not running. Start the server with:")
        print("   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")


if __name__ == "__main__":
    print("\n" + "🎨" * 30)
    print("Prompt Makeuper - Output Type Feature Demo")
    print("🎨" * 30)

    demo_xml_output()
    demo_markdown_output()
    demo_default_behavior()
    demo_invalid_output_type()

    print("\n\n" + "=" * 60)
    print("Demo Complete!")
    print("=" * 60)
    print("\nTo start the server:")
    print("  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
    print("\nTo run this demo:")
    print("  python demo_output_type.py")
    print("=" * 60 + "\n")
