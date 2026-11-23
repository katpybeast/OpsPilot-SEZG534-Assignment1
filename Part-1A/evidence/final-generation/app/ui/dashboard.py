from __future__ import annotations

import streamlit as st

from app.limits import MAX_FILE_SIZE_BYTES
from app.services.validation_service import validate_source
from app.storage.sqlite_repo import SqliteRepo


def render_dashboard() -> None:
    st.title("OpsPilot Core")
    st.caption("Local validation for CI/CD logs, Dockerfiles, and Kubernetes manifests")

    uploaded = st.file_uploader(
        "Upload a log, Dockerfile, or YAML manifest",
        type=["log", "dockerfile", "yaml", "yml"],
        max_upload_size=MAX_FILE_SIZE_BYTES // (1024 * 1024),
    )
    st.caption("Maximum file size: 1 MiB")
    repo = SqliteRepo()

    if uploaded is not None:
        try:
            raw = uploaded.read()
            result = validate_source(uploaded.name, raw, user_context="streamlit")
            st.success(
                f"Validation status: {result['summary_status']}"
            )
            st.json(result)
            st.write("Recent history:")
            history = repo.get_history()
            for item in history[:5]:
                st.write(
                    f"{item['source_file_name']} | {item['summary_status']} | "
                    f"{item['created_at']}"
                )
        except ValueError as exc:
            st.error(str(exc))

    else:
        st.write("Upload a supported file to validate it locally.")


if __name__ == "__main__":
    render_dashboard()
