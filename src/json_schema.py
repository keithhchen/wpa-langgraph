def json_schema():
    return {
        "title": "Article Outline",
        "type": "object",
        "required": ["node_id", "title", "children"],
        "properties": {
            "node_id": {
            "type": "string",
            "description": "Unique identifier for the node."
            },
            "title": {
            "type": "string",
            "description": "Title of the discussion or main topic."
            },
            "content": {
            "type": "string",
            "description": "Content or description of the node."
            },
            "children": {
            "type": "array",
            "description": "List of child nodes under the current node.",
            "items": {
                "type": "object",
                "required": ["node_id", "title", "content"],
                "properties": {
                "node_id": {
                    "type": "string",
                    "description": "Unique identifier for the child node."
                },
                "title": {
                    "type": "string",
                    "description": "Title of the child node."
                },
                "content": {
                    "type": "string",
                    "description": "Content or description of the child node."
                },
                }
            }
            }
        }
    }