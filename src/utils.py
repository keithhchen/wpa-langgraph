def remove_json_markers(text):
    # Define the markers
    start_marker = "```json"
    end_marker = "```"

    # Remove the start marker if it exists
    if text.startswith(start_marker):
        text = text[len(start_marker):]

    # Remove the end marker if it exists
    if text.endswith(end_marker):
        text = text[:-len(end_marker)]

    # Strip any extra whitespace that might remain
    return text.strip()