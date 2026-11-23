"""OpsPilot AI — Intelligent DevOps Log Explainer

Streamlit application for local CI/CD log analysis using the Ollama runtime.
"""

from __future__ import annotations

import json
import streamlit as st
from io import StringIO

from opspilot.model_client import OllamaClient, ModelGenerationError, ModelFailureCode
from opspilot.versions import (
    APPLICATION_VERSION,
    MAX_INPUT_BYTES,
    MAX_CONTROL_CHARACTER_PERCENT,
    OLLAMA_MODEL,
)


def _validate_input(log_text: str) -> tuple[bool, str]:
    """Validate log text against input constraints.
    
    Returns (is_valid, error_message) tuple.
    """
    if not log_text or not log_text.strip():
        return False, "Log input cannot be empty."
    
    byte_length = len(log_text.encode("utf-8"))
    if byte_length > MAX_INPUT_BYTES:
        return False, f"Log input exceeds {MAX_INPUT_BYTES} bytes ({byte_length} bytes provided)."
    
    control_chars = sum(
        1 for c in log_text
        if ord(c) < 32 and c not in "\t\n\r"
    )
    control_percent = control_chars / len(log_text) if log_text else 0.0
    if control_percent > MAX_CONTROL_CHARACTER_PERCENT:
        return False, f"Log contains too many control characters ({control_percent:.1%}; max {MAX_CONTROL_CHARACTER_PERCENT:.1%})."
    
    return True, ""


def _display_response(response: dict) -> None:
    """Display a successful model response in a structured format."""
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Status", response.get("status", "N/A"))
        st.metric("Category", response.get("category", "N/A"))
        st.metric("Confidence", f"{response.get('confidence', 0):.0%}")
    
    with col2:
        st.metric("Needs More Info", "Yes" if response.get("needs_more_information") else "No")
    
    st.subheader("Summary")
    st.write(response.get("summary", "No summary provided."))
    
    st.subheader("Root Cause")
    st.write(response.get("root_cause", "No root cause provided."))
    
    st.subheader("Evidence")
    evidence = response.get("evidence", [])
    if evidence:
        for i, item in enumerate(evidence, 1):
            st.write(f"{i}. {item}")
    else:
        st.write("No evidence provided.")
    
    st.subheader("Suggested Actions")
    actions = response.get("suggested_actions", [])
    if actions:
        for i, action in enumerate(actions, 1):
            st.write(f"{i}. {action}")
    else:
        st.write("No suggested actions provided.")


def _display_failure(failure) -> None:
    """Display a structured model failure without exposing the input log."""
    st.error(f"**Model Generation Failed**")
    
    failure_dict = failure.to_dict()
    st.write(f"**Error Code**: `{failure_dict['code']}`")
    st.write(f"**Message**: {failure_dict['message']}")
    
    if failure_dict.get("retryable"):
        st.info("⚠️ This error is retryable. Please try again.")
    else:
        st.warning("This error is not retryable. Please check the configuration or model status.")
    
    if failure_dict.get("http_status"):
        st.write(f"**HTTP Status**: {failure_dict['http_status']}")
    
    if failure_dict.get("response_sha256"):
        st.write(f"**Response Hash**: `{failure_dict['response_sha256']}`")
    
    if failure_dict.get("provenance"):
        with st.expander("Provenance Details"):
            prov = failure_dict["provenance"]
            st.json(prov)


def main() -> None:
    """Main Streamlit application entry point."""
    st.set_page_config(
        page_title="OpsPilot AI",
        page_icon="🔍",
        layout="wide",
    )
    
    st.title("🔍 OpsPilot AI — Intelligent DevOps Log Explainer")
    st.write(f"*Application v{APPLICATION_VERSION}* | *Model: {OLLAMA_MODEL}* | *Endpoint: 127.0.0.1:11434*")
    
    st.markdown("""
    **Analyze CI/CD logs** to identify failure causes, categorize issues, and get actionable recommendations.
    
    - Paste your CI/CD log output below
    - Click **Analyze** to generate an explanation
    - View detailed analysis results
    """)
    
    st.markdown("---")
    
    with st.form("log_analysis_form", clear_on_submit=False):
        log_input = st.text_area(
            "CI/CD Log Input",
            height=250,
            placeholder="Paste your CI/CD log here...",
            help=f"Maximum {MAX_INPUT_BYTES // 1024}KiB of text.",
        )
        
        analyze_button = st.form_submit_button(
            "🚀 Analyze",
            use_container_width=True,
            type="primary",
        )
    
    if analyze_button:
        is_valid, error_msg = _validate_input(log_input)
        if not is_valid:
            st.error(f"Input validation failed: {error_msg}")
        else:
            st.markdown("---")
            with st.spinner("Contacting local Ollama model..."):
                try:
                    client = OllamaClient(timeout_seconds=60.0)
                    result = client.generate(log_input)
                    
                    st.success("✅ Analysis complete.")
                    _display_response(result.response)
                    
                    with st.expander("Provenance & Hashes"):
                        prov = {
                            "provider": result.provenance.provider,
                            "requested_model": result.provenance.requested_model,
                            "actual_model": result.provenance.actual_model,
                            "model_digest": result.provenance.model_digest,
                            "runtime_version": result.provenance.runtime_version,
                            "endpoint": result.provenance.endpoint,
                            "temperature": result.provenance.temperature,
                            "seed_policy": result.provenance.seed_policy,
                            "context_tokens": result.provenance.context_tokens,
                            "max_output_tokens": result.provenance.max_output_tokens,
                        }
                        st.json(prov)
                        st.write(f"**Response SHA256**: `{result.response_sha256}`")
                
                except ModelGenerationError as e:
                    _display_failure(e.failure)


if __name__ == "__main__":
    main()
