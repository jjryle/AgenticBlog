"""
Test script for the HTML generator module.
This script creates a sample report data structure and generates an HTML report from it.
"""
import json
import webbrowser
import os
from research_agent.html_generator import generate_html_report, save_html_report

# Sample report data structure for testing
sample_report_data = {
    "query": "What are the latest advancements in AI research?",
    "report_summary": "This report provides an overview of recent developments in artificial intelligence research, focusing on large language models, reinforcement learning, and multimodal AI systems.",
    "follow_up_questions": [
        "How are large language models being applied in healthcare?",
        "What ethical considerations are important in AI development?",
        "How is AI being used to address climate change?"
    ],
    "verification": "This report has been verified by cross-referencing multiple academic sources and industry publications.",
    "markdown_report": """
# Latest Advancements in AI Research

## Large Language Models
Large Language Models (LLMs) have seen significant improvements in capabilities and efficiency. Recent models like GPT-4, Claude 3, and Gemini have demonstrated enhanced reasoning abilities and knowledge retention.

### Key Developments
- **Sparse Mixture of Experts**: Models using sparse activation patterns to scale efficiently
- **Multimodal Capabilities**: Integration of text, image, and audio understanding
- **Alignment Techniques**: Methods like RLHF and DPO for aligning AI with human values

## Reinforcement Learning
Reinforcement Learning continues to advance with applications in robotics and decision-making systems.

| Approach | Key Advantage | Notable Implementation |
|----------|--------------|------------------------|
| Model-based RL | Sample efficiency | MuZero |
| Multi-agent RL | Complex behaviors | AlphaStar |
| Offline RL | Learning from static datasets | Decision Transformer |

## Multimodal AI
Systems that can process and generate multiple types of data (text, images, audio) have seen breakthroughs.

![Multimodal AI Diagram](https://example.com/multimodal_ai.png)

### Applications
1. **Visual Question Answering**
2. **Text-to-Image Generation** with models like DALL-E 3 and Midjourney
3. **Video Understanding and Generation**
    """,
    "agents_info": [
        {
            "name": "ResearchAgent",
            "role": "Lead Researcher",
            "model": "gpt-4-turbo",
            "description": "Conducts primary research and coordinates other agents"
        },
        {
            "name": "VerifierAgent",
            "role": "Fact Checker",
            "model": "o3-mini-research",
            "description": "Validates information and checks sources"
        },
        {
            "name": "WriterAgent", 
            "role": "Content Creator",
            "model": "gpt-4",
            "description": "Compiles and formats the final report"
        }
    ]
}

def test_html_generator():
    """Run a test of the HTML generator with data from final_report.json."""
    print("Testing HTML generator with final_report.json...")
    
    # Generate and save HTML report using default final_report.json
    html_filename = save_html_report(filename_prefix="test_report")
    
    if html_filename:
        # Get the full path to the file
        full_path = os.path.abspath(html_filename)
        print(f"HTML report generated at: {full_path}")
        
        # Open the generated HTML file in the default browser
        print("Opening report in browser...")
        webbrowser.open(f"file:///{full_path}")
        
        # Also save the sample data to a JSON file for reference
        with open("sample_report_data.json", "w", encoding="utf-8") as f:
            json.dump(sample_report_data, indent=2, ensure_ascii=False, fp=f)
        print(f"Sample data saved to: {os.path.abspath('sample_report_data.json')}")
    else:
        print("Failed to generate HTML report")

if __name__ == "__main__":
    test_html_generator()
