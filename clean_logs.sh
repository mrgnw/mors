#!/bin/bash
log_file="/tmp/gymcalendar.log"
err_file="/tmp/gymcalendar.err"

n_lines=100

tail -n "$n_lines" "$log_file" > "$log_file.tmp" && mv "$log_file.tmp" "$log_file"
tail -n "$n_lines" "$err_file" > "$err_file.tmp" && mv "$err_file.tmp" "$err_file"

echo "Logs trimmed to last $n_lines lines at $(date)"
