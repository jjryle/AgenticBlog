from __future__ import annotations

import asyncio
import time
import json
import os
import datetime  # Add this import at the top of your file if not already present
from datetime import datetime # Added import
from collections.abc import Sequence

from rich.console import Console
import agents

from agents import Runner, RunResult, custom_span, gen_trace_id, trace
from .agents.tennis_agent import tennis_agent

from .agents.planner_agent import TennisSearchItem, TennisSearchPlan, planner_agent
from .agents.risk_agent import risk_agent
from .agents.search_agent import search_agent
from .agents.writer_agent import writer_agent
from .agents.verifier_agent import VerificationResult, verifier_agent
from .agents.writer_agent import TennisReportData, writer_agent
from .printer import Printer
from .html_generator import save_html_report # Import the new function

# Add custom JSON encoder
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        # Handle Pydantic BaseModel objects
        from pydantic import BaseModel
        if isinstance(obj, BaseModel):
            return obj.dict()
        # Handle objects with __dict__
        elif hasattr(obj, "__dict__"):
            return obj.__dict__
        # Convert other objects to strings
        return str(obj)

async def _summary_extractor(run_result: RunResult) -> str:
    """Custom output extractor for sub‑agents that return an AnalysisSummary."""
    # The tennis/risk analyst agents emit an AnalysisSummary with a `summary` field.
    # We want the tool call to return just that summary text so the writer can drop it inline.
    return str(run_result.final_output.summary)


class TennisResearchManager:
    """
    Orchestrates the full flow: planning, searching, sub‑analysis, writing, and verification.
    """

    def __init__(self) -> None:
        self.console = Console()
        self.printer = Printer(self.console)

# c:\Users\johnj\OneDrive\Documents\Projects\AgenticResearch\research_agent\manager.py
# ... (keep existing imports like asyncio, time, json, os, datetime, etc.)
# ... (keep CustomJSONEncoder class)
# ... (keep _summary_extractor function)

# Remove this import if not used elsewhere
# from .html_generator import save_html_report

# ... (keep TennisResearchManager class definition and __init__)
# c:\Users\johnj\OneDrive\Documents\Projects\AgenticResearch\research_agent\manager.py

# ... (keep existing imports, CustomJSONEncoder, _summary_extractor, TennisResearchManager class, __init__)

    async def run(self, query: str) -> None:
        trace_id = gen_trace_id()
        with trace("Tennis research trace", trace_id=trace_id):
            self.printer.update_item(
                "trace_id",
                f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}",
                is_done=True,
                hide_checkmark=True,
            )
            self.printer.update_item("start", "Starting tennis research...", is_done=True)

            print("query=", query)

            search_plan = await self._plan_searches(query)

            print("search_plan=", search_plan)

            search_results = await self._perform_searches(search_plan)

            # Extract tennis and risk analyses from tools during report writing
            tennis_analysis = None
            risk_analysis = None
            report = await self._write_report(query, search_results, tennis_analysis_out=lambda x: setattr(self, 'tennis_analysis', x),
                                             risk_analysis_out=lambda x: setattr(self, 'risk_analysis', x))

            verification = await self._verify_report(report)

            final_report_summary = f"Report summary\n\n{report.short_summary}" # Renamed to avoid conflict later
            self.printer.update_item("final_report", final_report_summary, is_done=True)

            # Define agents info (as before)
            agents_info = [
                {"name": "PlannerAgent", "role": "Planning", "model": "o3-mini", "description": "Plans the research by selecting appropriate search topics based on the query"},
                {"name": "SearchAgent", "role": "Research", "model": "gpt-4o-2024-08-06", "description": "Searches for and retrieves relevant information about the topics"},
                {"name": "TennisAnalystAgent", "role": "Analysis", "model": "gpt-4o", "description": "Analyzes tennis metrics, performance indicators, and player statistics"},
                {"name": "RiskAnalystAgent", "role": "Risk Assessment", "model": "gpt-4o", "description": "Evaluates potential concerns, challenges, and risk factors"},
                {"name": "WriterAgent", "role": "Report Writing", "model": "gpt-4o", "description": "Synthesizes research and analysis into a cohesive report"},
                {"name": "VerificationAgent", "role": "Verification", "model": "gpt-4o", "description": "Checks the report for accuracy, consistency, and completeness"}
            ]

            # Prepare report data dictionary (as before)
            report_data = {
                "query": query,
                "search_plan": search_plan.__dict__ if hasattr(search_plan, "__dict__") else str(search_plan),
                "search_results": search_results,
                "tennis_analysis": getattr(self, 'tennis_analysis', None),
                "risk_analysis": getattr(self, 'risk_analysis', None),
                "report_summary": report.short_summary,
                "markdown_report": report.markdown_report,
                "follow_up_questions": report.follow_up_questions,
                "verification": str(verification),
                "agents_info": agents_info
            }
            print("follow_up_questions") # Consider removing or refining these prints
            print(report_data)          # Consider removing or refining these prints            # --- Define Filenames ---
            report_filename_base = "final_report"
            report_filename_json = f"{report_filename_base}.json"
            report_filename_html = f"{report_filename_base}.html"

            # --- JSON Saving ---
            # Backup existing JSON file
            if os.path.exists(report_filename_json):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_filename_json = f"{report_filename_base}_{timestamp}.json"
                try:
                    os.rename(report_filename_json, backup_filename_json)
                    self.printer.console.print(f"Backed up existing JSON report to {backup_filename_json}")
                except OSError as e:
                    self.printer.console.print(f"Error backing up JSON file: {e}", style="bold red")

            # Save the new JSON file
            try:
                with open(report_filename_json, "w", encoding="utf-8") as json_file:
                    json.dump(report_data, json_file, indent=4, cls=CustomJSONEncoder)
                self.printer.console.print(f"JSON report data saved to {report_filename_json}")
            except Exception as e:
                self.printer.console.print(f"Error saving JSON file: {e}", style="bold red")

            # --- HTML Generation ---
            # Backup existing HTML file if it exists
            if os.path.exists(report_filename_html):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_filename_html = f"{report_filename_base}_{timestamp}.html"
                try:
                    os.rename(report_filename_html, backup_filename_html)
                    self.printer.console.print(f"Backed up existing HTML report to {backup_filename_html}")
                except OSError as e:
                    self.printer.console.print(f"Error backing up HTML file: {e}", style="bold red")            # Generate new HTML file
            try:
                save_html_report(report_data, output_file=report_filename_html)
                self.printer.console.print(f"HTML report saved to {report_filename_html}")
            except Exception as e:
                self.printer.console.print(f"Error generating HTML report: {e}", style="bold red")

            self.printer.end()

            # Print to stdout (as before)
            print("\n\n=====REPORT=====\n\n")
            print(f"Report:\n{report.markdown_report}")
# c:\Users\johnj\OneDrive\Documents\Projects\AgenticResearch\research_agent\manager.py
# ... (keep existing imports, CustomJSONEncoder, _summary_extractor, TennisResearchManager class, __init__)
# ... (keep the start of the run method, planning, searching, writing, verification)
# ... (keep agents_info and report_data dictionary preparation)

            # --- Define Filenames ---
            report_filename_base = "final_report"
            report_filename_json = f"{report_filename_base}.json"
            report_filename_html = f"{report_filename_base}.html" # Define the exact HTML filename

            # --- JSON Saving ---
            # Backup existing JSON file
            if os.path.exists(report_filename_json):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                base, ext = os.path.splitext(report_filename_json)
                backup_filename_json = f"{base}_{timestamp}{ext}"
                try:
                    os.rename(report_filename_json, backup_filename_json)
                    self.printer.console.print(f"Backed up existing JSON report to {backup_filename_json}")
                except OSError as e:
                    self.printer.console.print(f"Error backing up JSON file: {e}", style="bold red")

            # Save the new JSON file
            try:
                with open(report_filename_json, "w", encoding="utf-8") as json_file:
                    json.dump(report_data, json_file, indent=4, cls=CustomJSONEncoder)
                self.printer.console.print(f"JSON report data saved to {report_filename_json}")
            except IOError as e:
                 self.printer.console.print(f"Error saving JSON file: {e}", style="bold red")
            except Exception as e:
                 self.printer.console.print(f"An unexpected error occurred during JSON saving: {e}", style="bold red")


            # --- HTML Generation ---
            # Backup existing HTML file
            if os.path.exists(report_filename_html):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                base, ext = os.path.splitext(report_filename_html)
                backup_filename_html = f"{base}_{timestamp}{ext}"
                try:
                    os.rename(report_filename_html, backup_filename_html)
                    self.printer.console.print(f"Backed up existing HTML report to {backup_filename_html}")
                except OSError as e:
                    self.printer.console.print(f"Error backing up HTML file: {e}", style="bold red")

            # Save the new HTML file using the specific filename
            try:
                # Assuming save_html_report accepts a 'filename' argument for the full path
                # If this causes an error, the signature of save_html_report might need checking/changing
                save_html_report(report_data, filename=report_filename_html)
                self.printer.console.print(f"HTML report saved to {report_filename_html}") # Add confirmation here
            except TypeError:
                # Fallback if 'filename' argument isn't accepted, try passing it positionally
                # Or handle the case where save_html_report MUST use a prefix and timestamp
                try:
                    # This assumes save_html_report might take the filename as the second arg
                    save_html_report(report_data, report_filename_html)
                    self.printer.console.print(f"HTML report saved to {report_filename_html}") # Add confirmation here
                except Exception as e:
                    self.printer.console.print(f"Error saving HTML file (check save_html_report signature): {e}", style="bold red")
            except IOError as e:
                 self.printer.console.print(f"Error saving HTML file: {e}", style="bold red")
            except Exception as e:
                 self.printer.console.print(f"An unexpected error occurred during HTML generation: {e}", style="bold red")


            # --- Final Output ---
            # Construct the final report string for printing (as before)
            final_report_output = f"Report summary\n\n{report.short_summary}\n\nVerification:\n{verification}" # Already defined earlier

            self.printer.end()

            # Print to stdout (as before)
            print("\n\n=====REPORT=====\n\n")
            print(f"Report:\n{report.markdown_report}")
            print("\n\n=====FOLLOW UP QUESTIONS=====\n\n")
            print("\n".join(report.follow_up_questions))
            print("\n\n=====VERIFICATION=====\n\n")
            print(verification)

    # ... (keep the rest of the methods: _plan_searches, _perform_searches, _search, _write_report, _verify_report)

            print("\n\n=====FOLLOW UP QUESTIONS=====\n\n")
            print("\n".join(report.follow_up_questions))
            print("\n\n=====VERIFICATION=====\n\n")
            print(verification)

    # ... (keep the rest of the methods: _plan_searches, _perform_searches, _search, _write_report, _verify_report)
    # Make sure the indentation matches the rest of your class methods

    # ... (keep the rest of the methods: _plan_searches, _perform_searches, _search, _write_report, _verify_report)
    # Make sure the indentation matches the rest of your class methods

    async def _plan_searches(self, query: str) -> TennisSearchPlan:
        self.printer.update_item("planning", "Planning searches...")
        result = await Runner.run(planner_agent, f"Query: {query}")
        self.printer.update_item(
            "planning",
            f"Will perform {len(result.final_output.searches)} searches",
            is_done=True,
        )
        return result.final_output_as(TennisSearchPlan)

# ...existing code...
    async def _perform_searches(self, search_plan: TennisSearchPlan) -> Sequence[str]: # Changed return type hint
        with custom_span("Search the web"):
            self.printer.update_item("searching", "Searching...")
            tasks = [asyncio.create_task(self._search(item)) for item in search_plan.searches]
            results: list[str] = []
            num_completed = 0
            for task in asyncio.as_completed(tasks):
                result = await task
                if result is not None:
                    results.append(result) # Append the dictionary
                num_completed += 1
                self.printer.update_item(
                    "searching", f"Searching... {num_completed}/{len(tasks)} completed"
                )
            self.printer.mark_item_done("searching")
            return results


# ...existing code...
    async def _search(self, item: TennisSearchItem) -> dict[str, str] | None: # Changed return type hint
        input_data = f"Search term: {item.query}\nReason: {item.reason}"
        try:
            # Assuming Runner.run now returns a result where final_output is {"content": ..., "url": ...}
            result = await Runner.run(search_agent, input_data)
            # Ensure the output is the expected dictionary
            if isinstance(result.final_output, dict) and "content" in result.final_output and "url" in result.final_output:
                return {"content": str(result.final_output["content"]), "url": str(result.final_output["url"])}
            else:
                # Log unexpected format details
                self.printer.console.print(
                    f"Warning: Search for '{item.query}' did not return expected format. Received: {result.final_output}",
                    style="yellow"
                )
                # Optionally return content only if available, without URL
                if isinstance(result.final_output, dict) and "content" in result.final_output:
                    return {"content": str(result.final_output["content"]), "url": ""}
                return None
        except Exception as e:
            # Use self.console directly, not self.printer.console
            self.console.print(f"Error during search for '{item.query}': {e}", style="bold red")
            return None
# ...existing code...

    async def _write_report(self, query: str, search_results: Sequence[str], 
                     tennis_analysis_out=None, risk_analysis_out=None) -> TennisReportData:        # Custom extractors that both return the summary text and save the full object to our callbacks
        def tennis_extractor(run_result: RunResult) -> str:
            # Return the string summary for the tool to use in the report
            summary = str(run_result.final_output.summary)
            # Save the full AnalysisSummary object for JSON export
            if tennis_analysis_out:
                tennis_analysis_out(run_result.final_output)
            return summary
            
        def risk_extractor(run_result: RunResult) -> str:
            # Return the string summary for the tool to use in the report
            summary = str(run_result.final_output.summary)
            # Save the full AnalysisSummary object for JSON export
            if risk_analysis_out:
                risk_analysis_out(run_result.final_output)
            return summary
            
        # Expose the specialist analysts as tools so the writer can invoke them inline
        # and still produce the final TennisReportData output.
        fundamentals_tool = tennis_agent.as_tool(
            tool_name="fundamentals_analysis",
            tool_description="Use to get a short write‑up of key tennis metrics and performance indicators",
            custom_output_extractor=tennis_extractor,
        )
        risk_tool = risk_agent.as_tool(
            tool_name="risk_analysis",
            tool_description="Use to get a short write‑up of potential concerns or issues",
            custom_output_extractor=risk_extractor,
        )
        writer_with_tools = writer_agent.clone(tools=[fundamentals_tool, risk_tool])
        self.printer.update_item("writing", "Thinking about report...")
        input_data = f"Original query: {query}\nSummarized search results: {search_results}"
        result = Runner.run_streamed(writer_with_tools, input_data)
        update_messages = [
            "Planning report structure...",
            "Writing sections...",
            "Finalizing report...",
        ]
        last_update = time.time()
        next_message = 0
        async for _ in result.stream_events():
            if time.time() - last_update > 5 and next_message < len(update_messages):
                self.printer.update_item("writing", update_messages[next_message])
                next_message += 1
                last_update = time.time()
        self.printer.mark_item_done("writing")
        return result.final_output_as(TennisReportData)

    async def _verify_report(self, report: TennisReportData) -> VerificationResult:
        self.printer.update_item("verifying", "Verifying report...")
        result = await Runner.run(verifier_agent, report.markdown_report)
        self.printer.mark_item_done("verifying")
        return result.final_output_as(VerificationResult)