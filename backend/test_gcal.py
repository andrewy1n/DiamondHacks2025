from datetime import datetime, timedelta
import json
from typing import Any, Dict
from urllib.parse import quote
from dotenv import load_dotenv
from fastapi import HTTPException
from google import genai
import os
from dateutil.parser import parse
import asyncio

load_dotenv()

gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def parse_gemini_response(response) -> Dict[str, Any]:
    try:
        # 1. Extract the text content from the response
        response_text = response.candidates[0].content.parts[0].text
        
        # 2. Clean the response text
        # Remove markdown code block markers if present
        if response_text.startswith('```json'):
            json_str = response_text[7:-3].strip()  # Remove ```json and trailing ```
        elif response_text.startswith('```'):
            json_str = response_text[3:-3].strip()  # Remove ``` and trailing ```
        else:
            json_str = response_text.strip()
        
        # 3. Parse the JSON
        return json.loads(json_str)
        
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format: {str(e)}. Content: {json_str}")
    except AttributeError as e:
        raise ValueError(f"Unexpected response format: {str(e)}")
    except Exception as e:
        raise ValueError(f"Failed to parse Gemini response: {str(e)}")

async def generate_summary(text: str) -> dict:
    try:
        prompt = f"""
        Analyze this doctor-patient conversation and:
        1. Extract ALL date/time information with these rules:
        - Default to Pacific Time (America/Los_Angeles) if no timezone specified
        - For medication times:
            * First dose between 7AM-9AM local time
            * Subsequent doses at reasonable hours (7AM-9PM)
        - For appointments:
            * Normal clinic hours (8AM-6PM)
        - Never suggest times between 10PM-6AM
        - Base all times on the given date from the conversation, if "tomorrow" is mentioned, it will the day
        after the specified conversation date
        2. Return structured JSON with:
        {{
        "summary": "formatted markdown",
        "calendar_events": [
            {{
            "title": "event name",
            "start": "ISO8601 datetime",  // MUST be reasonable hour
            "end": "ISO8601 datetime",    // Start + duration
            "recurrence": "RRULE string", // For repeating events
            "timezone": "America/Los_Angeles", // Enforced default
            "description": "full details",
            "time_constraints": {{        // Added field
                "earliest": "07:00",       // 7AM
                "latest": "21:00"          // 9PM
            }},
            "medication_details": {{      // ONLY for medications
                "dose": "500mg",
                "frequency": "every 8 hours",
                "duration": "7 days",
                "preferred_times": ["07:00", "15:00", "23:00"] // Adjusted to reasonable hours
            }}
            }}
        ]
        }}
        Conversation: {text}

        IMPORTANT RULES:
        1. NEVER suggest times between 10PM-6AM for any event
        2. First medication dose between 7-9AM
        3. Appointments only between 8AM-6PM
        4. All times MUST be in ISO8601 with timezone
        """
        
        response = gemini_client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        
        result = parse_gemini_response(response)        
        print(result)

        # Generate Google Calendar links
        events_with_links = []
        for event in result.get("calendar_events", []):
            gcal_link = create_gcal_link(event)
            event["gcal_link"] = gcal_link
            events_with_links.append(event)
        
        # Embed links in summary text
        summary_with_links = result["summary"]
        for event in events_with_links:
            summary_with_links += f"\n\n[Add to Calendar]({event['gcal_link']})"
        
        return {
            "text": summary_with_links,
            "events": events_with_links
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini API error: {str(e)}")
    
def create_gcal_link(event: dict) -> str:
    base_url = "https://calendar.google.com/calendar/u/0/r/eventedit"
    
    start = parse(event["start"]).strftime('%Y%m%dT%H%M%S')
    end = parse(event["end"]).strftime('%Y%m%dT%H%M%S')

    description = event['description']
    
    if "medication_details" in event and event['medication_details'] is not None:
        med = event.get("medication_details", {})
        description = (
            f"MEDICATION:\n"
            f"• Dose: {med.get('dose', '')}\n"
            f"• Frequency: {med.get('frequency', '')}\n"
            f"• Duration: {med.get('duration', '')}\n\n"
        )
    
    params = {
        'text': event["title"],
        'dates': f"{start}/{end}",
        'details': description,
        'location': event.get("location", ""),
        'ctz': event.get("timezone", "UTC"),
        'recur': event.get("recurrence", "")
    }
    
    # Filter empty params and create URL
    query = '&'.join(f"{k}={quote(v)}" for k,v in params.items() if v)
    return f"{base_url}?{query}"

async def main():
    test_conversation = f"""
    Today's Date: {datetime.now().isoformat}
    Doctor: Your next follow-up appointment will be on April 25th at 2:30 PM to 3:30 PM.
    Patient: Should I start taking the medication today?
    Doctor: Yes, begin the antibiotics tomorrow morning, and remember to take once a week for a month.
    We'll need to schedule a blood test for July 1st in the morning at 9:00 am.
    """
    
    print("=== Testing generate_summary() ===")
    try:
        summary = await generate_summary(test_conversation)
        print("Generated Summary:")
        print(summary["text"])
        print("\nCalendar Events:")
        for event in summary["events"]:
            print(f"- {event['title']} at {event['start']}")
            print(f"  Link: {event['gcal_link']}")
    except Exception as e:
        print(f"Error in generate_summary: {e}")

    # print("\n=== Testing create_gcal_link() ===")
    # try:
    #     medication = {
    #         "title": "Take Antibiotics (Amoxicillin 500mg)",
    #         "start": "2024-04-05T08:00:00",  # First dose
    #         "end": "2024-04-05T08:05:00",    # 5 minute duration
    #         "details": "Take with food. Complete full 7-day course.",
    #         "timezone": "America/New_York",
    #         "medication": {
    #             "dose": "500mg",
    #             "frequency": "every 1 day",
    #             "duration": "7 days"
    #         }
    #     }

    #     start_time = parse(medication["start"])
    #     end_time = start_time + timedelta(days=7)
        
    #     rule = rrule.rrule(
    #         freq=rrule.HOURLY,
    #         interval=8,
    #         dtstart=start_time,
    #         until=end_time
    #     )
    #     medication["recurrence"] = f"RRULE:{str(rule).split('RRULE:')[1]}"

    #     print(medication)

    #     test_link = create_gcal_link(medication)
    #     print(f"Generated Google Calendar link:\n{test_link}")
    # except Exception as e:
    #     print(f"Error in create_gcal_link: {e}")

if __name__ == "__main__":
    asyncio.run(main())