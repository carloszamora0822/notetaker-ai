#!/usr/bin/env bash
set -euo pipefail

QUEUE_DIR="queue"
OUTPUT_DIR="output"
TEMPLATES_DIR="templates"
LOGS_DIR="../logs"

# Ensure directories exist
mkdir -p "$QUEUE_DIR" "$OUTPUT_DIR" "$TEMPLATES_DIR" "$LOGS_DIR"

process_queue() {
  for input in "$QUEUE_DIR"/*_input.json; do
    [ -f "$input" ] || continue

    echo "[LaTeX] Processing: $input"

    # Extract output name
    output_name=$(python3 -c "import json, sys; print(json.load(open('$input'))['output_name'])" 2>/dev/null || echo "unknown")

    if [ "$output_name" = "unknown" ]; then
      echo "[LaTeX] ERROR: Could not parse output_name from $input"
      continue
    fi

    # Call renderer
    if python3 scripts/render.py "$input"; then
      echo "[LaTeX] Rendered ${output_name}.tex"
    else
      echo "[LaTeX] ERROR: Render failed for $input"
      # Write error result
      result_file="${input/_input.json/_result.json}"
      cat > "$result_file" << EOF
{
  "success": false,
  "pdf_path": null,
  "error": "Render failed",
  "compile_time_sec": 0
}
EOF
      mv "$input" "${QUEUE_DIR}/failed_$(basename "$input")"
      continue
    fi

    # Compile
    start_time=$(date +%s)
    cd "$TEMPLATES_DIR"
    if latexmk -xelatex -halt-on-error -interaction=nonstopmode "${output_name}.tex" >/dev/null 2>&1; then
      end_time=$(date +%s)
      compile_time=$((end_time - start_time))

      # Move PDF to output directory
      if [ -f "${output_name}.pdf" ]; then
        mv "${output_name}.pdf" "../${OUTPUT_DIR}/"
        echo "[LaTeX] Compiled: ${OUTPUT_DIR}/${output_name}.pdf"

        # Write success result
        result_file="${input/_input.json/_result.json}"
        cd ..
        cat > "$result_file" << EOF
{
  "success": true,
  "pdf_path": "latex/output/${output_name}.pdf",
  "error": null,
  "compile_time_sec": ${compile_time}
}
EOF

        # Archive processed input
        mv "$input" "${QUEUE_DIR}/processed_$(basename "$input")"
      else
        cd ..
        echo "[LaTeX] ERROR: PDF not generated for ${output_name}"
      fi
    else
      cd ..
      end_time=$(date +%s)
      compile_time=$((end_time - start_time))

      # Write error result
      result_file="${input/_input.json/_result.json}"
      cat > "$result_file" << EOF
{
  "success": false,
  "pdf_path": null,
  "error": "Compilation failed",
  "compile_time_sec": ${compile_time}
}
EOF
      echo "[LaTeX] ERROR: Compilation failed for ${output_name}.tex"

      # Archive failed input
      mv "$input" "${QUEUE_DIR}/failed_$(basename "$input")"
    fi
  done
}

echo "[LaTeX] Watcher started. Monitoring ${QUEUE_DIR}/ for input files..."

while true; do
  process_queue

  # Update status file
  queue_size=$(ls "$QUEUE_DIR"/*_input.json 2>/dev/null | wc -l | tr -d ' ')
  timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
  last_pdf=$(ls -t "$OUTPUT_DIR"/*.pdf 2>/dev/null | head -1 | xargs basename 2>/dev/null || echo "none")

  cat > "${LOGS_DIR}/latex_status.json" << EOF
{
  "timestamp": "${timestamp}",
  "watcher_running": true,
  "queue_size": ${queue_size},
  "last_compile": {"file": "${last_pdf}", "success": true}
}
EOF

  sleep 2
done
