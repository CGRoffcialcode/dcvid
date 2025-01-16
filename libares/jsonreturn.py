"""
* Copyright (C) 2025 CGRofficialcode
 *
 * This code is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * Thiscode is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this code.  If not, see <https://www.gnu.org/licenses/>.
 *//
 """

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


