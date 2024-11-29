import json

def extract_url_from_discord_json(json_data):
    """
    Extracts the URL from a Discord webhook JSON response.

    Args:
        json_data: A dictionary representing the JSON response.

    Returns:
        The URL string if found, otherwise None.  Handles potential errors gracefully.
        
    Made By:
        CGR
    
    """
    try:
        attachments = json_data.get('attachments')
        if attachments and isinstance(attachments, list) and len(attachments) > 0:
            first_attachment = attachments[0]  # Assume the URL is in the first attachment
            return first_attachment.get('url')
        else:
            return None  # No attachments found
    except (KeyError, AttributeError, IndexError, TypeError) as e:
        print(f"Error processing JSON: {e}")
        return None #Handle potential errors in the JSON structure

# Example usage:


