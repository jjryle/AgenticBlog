import json
from datetime import datetime
import markdown  # Assuming 'markdown' library is installed

def generate_html_report(report_data):
    """Generates an HTML report from the provided report data."""

    # Safely get data, providing defaults for missing keys
    query = report_data.get("query", "N/A")
    report_summary = report_data.get("report_summary", "Summary not available.")
    follow_up_questions = report_data.get("follow_up_questions", [])
    verification = report_data.get("verification", "Verification details not available.")
    markdown_report_content = report_data.get("markdown_report", "Report content not available.")
    agents_info = report_data.get("agents_info", [])

    # Convert Markdown to HTML using the 'markdown' library
    try:
        html_report_content = markdown.markdown(markdown_report_content, extensions=['extra', 'tables'])
    except Exception as e:
        html_report_content = f"<p>Error converting Markdown: {e}</p><pre>{markdown_report_content}</pre>"

    # Generate list items for follow-up questions
    follow_up_items_html = "".join([f"<li>{q}</li>" for q in follow_up_questions])

    # Generate table rows for agents info
    agents_rows_html = ""
    for agent in agents_info:
        agents_rows_html += f'''
            <tr>
                <td>{agent.get("name", "N/A")}</td>
                <td>{agent.get("role", "N/A")}</td>
                <td><span class="model-badge" data-model="{agent.get("model", "")}">{agent.get("model", "N/A")}</span></td>
                <td>{agent.get("description", "N/A")}</td>
            </tr>
        '''

    # Prepare the full JSON data for display
    json_string = json.dumps(report_data, indent=2)

    html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Research Report: {query}</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/default.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
    <style>
        body {{ font-family: sans-serif; margin: 0; padding: 0; background-color: #f4f4f4; color: #333; }}
        .container {{ max-width: 1000px; margin: 20px auto; background: #fff; padding: 20px; box-shadow: 0 0 10px rgba(0,0,0,0.1); border-radius: 8px; }}
        h1, h2, h3 {{ color: #444; }}
        h1 {{ border-bottom: 2px solid #eee; padding-bottom: 10px; }}
        .section {{ margin-bottom: 20px; padding: 15px; background-color: #fafafa; border: 1px solid #e0e0e0; border-radius: 5px; }}
        .section h2 {{ margin-top: 0; border-bottom: 1px solid #ddd; padding-bottom: 5px; }}
        #reportContentBody img {{ max-width: 100%; height: auto; border-radius: 4px; }}
        #reportContentBody table {{ border-collapse: collapse; width: 100%; margin-bottom: 1em; }}
        #reportContentBody th, #reportContentBody td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        #reportContentBody th {{ background-color: #f2f2f2; }}
        #jsonViewer {{ background-color: #282c34; color: #abb2bf; padding: 15px; border-radius: 5px; overflow-x: auto; font-family: monospace; font-size: 0.9em; }}
        #followUpList li {{ cursor: pointer; color: #007bff; text-decoration: underline; margin-bottom: 5px; }}
        #followUpList li:hover {{ color: #0056b3; }}
        #backToTop {{ position: fixed; bottom: 20px; right: 20px; background-color: #007bff; color: white; padding: 10px 15px; border-radius: 5px; cursor: pointer; display: none; z-index: 1000; }}
        #backToTop.visible {{ display: block; }}
        table#agentsTable {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
        table#agentsTable th, table#agentsTable td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        table#agentsTable th {{ background-color: #f2f2f2; }}
        .model-badge {{ background-color: #f0f0f0; border-radius: 4px; padding: 4px 8px; font-family: monospace; font-size: 0.9em; color: #333; display: inline-block; }}
        .model-badge[data-model*="gpt-4"] {{ background-color: #e6f7ff; color: #0078d4; }}
        .model-badge[data-model*="o3-mini"] {{ background-color: #e6ffe6; color: #007a00; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Research Report</h1>
        <p><strong>Query:</strong> {query}</p>

        <div class="section" id="summary">
            <h2>Summary</h2>
            <p id="summaryContent">{report_summary}</p>
        </div>

        <div class="section" id="reportContent">
            <h2>Detailed Report</h2>
            <div id="reportContentBody">
                {html_report_content}
            </div>
        </div>

        <div class="section" id="followUp">
            <h2>Follow-up Questions</h2>
            <ul id="followUpList">
                {follow_up_items_html}
            </ul>
        </div>

        <div class="section" id="verification">
            <h2>Verification</h2>
            <p id="verificationContent">{verification}</p>
        </div>
        
        <div class="section" id="agentsInfo">
            <h2>Agents Information</h2>
            <table id="agentsTable">
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Role</th>
                        <th>Model</th>
                        <th>Description</th>
                    </tr>
                </thead>
                <tbody id="agentsTableBody">
                    {agents_rows_html}
                </tbody>
            </table>
        </div>

        <div class="section" id="rawData">
            <h2>Raw JSON Data</h2>
            <pre><code class="language-json" id="jsonViewer">{json_string}</code></pre>
        </div>
    </div>

    <button id="backToTop" title="Go to top">Top</button>

    <script>
        hljs.highlightAll();        const backToTop = document.getElementById('backToTop');
        if (backToTop) {{
            window.addEventListener('scroll', function() {{
                if (window.scrollY > 300) {{
                    backToTop.classList.add('visible');
                }} else {{
                    backToTop.classList.remove('visible');
                }}
            }});
            
            backToTop.addEventListener('click', function(e) {{
                e.preventDefault();
                window.scrollTo({{ top: 0, behavior: 'smooth' }});
            }});
        }}

        const followUpItems = document.querySelectorAll('#followUpList li');
        followUpItems.forEach(item => {{
            item.addEventListener("click", () => {{
                if (confirm('Would you like to search for this follow-up question? \\n\\n' + item.textContent)) {{
                    console.log('User wants to search for:', item.textContent); 
                    alert('Search functionality for follow-up questions is not yet implemented.');
                }}
            }});
        }});
    </script>
</body>
</html>
"""
    return html_template

def save_html_report(report_data=None, filename_prefix="report", output_file=None):
    """Generates and saves the HTML report.
    
    Args:
        report_data (dict, optional): Report data to use. If None, loads from final_report.json
        filename_prefix (str, optional): Prefix for the output filename if output_file is not specified
        output_file (str, optional): Exact filename to use. If provided, filename_prefix is ignored
    """
    if report_data is None:
        try:
            with open('final_report.json', 'r', encoding='utf-8') as f:
                report_data = json.load(f)
        except FileNotFoundError:
            print("Error: final_report.json not found in the current directory")
            return None
        except json.JSONDecodeError:
            print("Error: Could not decode JSON from final_report.json")
            return None

    html_content = generate_html_report(report_data)
    
    if output_file:
        html_filename = output_file
    else:
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        html_filename = f"{filename_prefix}_{timestamp_str}.html"
    try:
        with open(html_filename, "w", encoding="utf-8") as html_file:
            html_file.write(html_content)
        print(f"HTML report generated successfully at {html_filename}")
        return html_filename
    except IOError as e:
        print(f"Error writing HTML file {html_filename}: {e}")
        return None

if __name__ == '__main__':
    save_html_report(filename_prefix="test_report")

