"""
Groq API client wrapper — centralized AI API access with error handling.
"""
import os
from groq import Groq
from django.conf import settings


def get_client():
    """Get configured Groq client."""
    api_key = settings.GROQ_API_KEY or os.getenv('GROQ_API_KEY', '')
    if not api_key or api_key == 'your-groq-api-key-here':
        raise ValueError("GROQ_API_KEY not configured. Add it to your .env file.")
    return Groq(api_key=api_key)


def chat_completion(messages, model=None, temperature=0.7, max_tokens=1024):
    """Send a chat completion request to Groq."""
    client = get_client()
    model = model or settings.GROQ_TEXT_MODEL

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content


def vision_completion(image_base64, prompt, model=None, max_tokens=1024):
    """Send a vision completion request to Groq."""
    client = get_client()
    model = model or settings.GROQ_VISION_MODEL

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}"
                        },
                    },
                ],
            }
        ],
        temperature=0.3,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content
