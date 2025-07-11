const { Anthropic } = require('@anthropic-ai/sdk');

const anthropic = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY,
});

const SYSTEM_PROMPT = `You are Maurice, a friendly and helpful AI assistant representing Maurice Rashad, a technology consultant.

Maurice Rashad is a technology consultant with 10+ years of experience. He offers:

1. Strategic Consulting ($100/month, 2x 1-hour calls)
   - Strategic planning sessions
   - Technology roadmap development
   - Problem-solving workshops
   - Growth strategy recommendations

2. Technology Services ($75/hour)
   - Custom automation solutions
   - Website development & fixes
   - App development
   - Hosting & migration services

3. Expert Workshops ($99 each)
   - AI Agents & Automation
   - Cybersecurity Fundamentals
   - Modern Web Development
   - Cloud Technologies

Contact: mauricerashad@gmail.com
Response time: Within 24 hours
Availability: Global, Remote-First

Key stats: 50+ businesses transformed, 99% client satisfaction, 24/7 support available.

Guidelines:
- Be professional, helpful, and encouraging about contacting Maurice
- Keep responses concise and conversational
- Include relevant pricing when discussing services
- Encourage users to contact Maurice for consultations
- Ask follow-up questions to keep the conversation flowing`;

exports.handler = async (event, context) => {
  // Handle CORS
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Content-Type': 'application/json',
  };

  if (event.httpMethod === 'OPTIONS') {
    return { statusCode: 200, headers, body: '' };
  }

  if (event.httpMethod !== 'POST') {
    return {
      statusCode: 405,
      headers,
      body: JSON.stringify({ error: 'Method not allowed' }),
    };
  }

  try {
    const { message } = JSON.parse(event.body);

    if (!message || typeof message !== 'string') {
      return {
        statusCode: 400,
        headers,
        body: JSON.stringify({ error: 'Message is required' }),
      };
    }

    if (!process.env.ANTHROPIC_API_KEY) {
      return {
        statusCode: 500,
        headers,
        body: JSON.stringify({ error: 'API key not configured' }),
      };
    }

    const response = await anthropic.messages.create({
      model: 'claude-3-5-sonnet-20241022',
      max_tokens: 500,
      system: SYSTEM_PROMPT,
      messages: [
        {
          role: 'user',
          content: message,
        },
      ],
    });

    const botResponse = response.content[0].text;

    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({
        response: botResponse,
        timestamp: new Date().toISOString(),
      }),
    };
  } catch (error) {
    console.error('Error:', error);
    
    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({
        error: 'Internal server error',
        message: error.message,
      }),
    };
  }
};