// Netlify serverless function to proxy OpenAI API requests
const fetch = require('node-fetch');

exports.handler = async function(event, context) {
  // Only allow POST requests
  if (event.httpMethod !== 'POST') {
    return {
      statusCode: 405,
      body: JSON.stringify({ error: 'Method Not Allowed' }),
      headers: {
        'Allow': 'POST',
        'Content-Type': 'application/json'
      }
    };
  }

  try {
    // Get the OpenAI API key from environment variables or request headers
    let apiKey = process.env.OPENAI_API_KEY;
    
    // Check if the API key is in the request headers (for local testing)
    const authHeader = event.headers['authorization'] || event.headers['Authorization'];
    if (!apiKey && authHeader && authHeader.startsWith('Bearer ')) {
      apiKey = authHeader.substring(7);
    }
    
    if (!apiKey) {
      return {
        statusCode: 500,
        body: JSON.stringify({ error: 'API key not configured' }),
        headers: { 
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Headers': 'Content-Type, Authorization'
        }
      };
    }

    // Parse the request body
    const requestBody = JSON.parse(event.body);
    
    // Forward the request to OpenAI API
    const response = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiKey}`
      },
      body: JSON.stringify(requestBody)
    });

    // Get the response from OpenAI
    const data = await response.json();

    // Return the response
    return {
      statusCode: 200,
      body: JSON.stringify(data),
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*', // Allow requests from any origin
        'Access-Control-Allow-Headers': 'Content-Type, Authorization'
      }
    };
  } catch (error) {
    console.error('Error proxying to OpenAI:', error);
    
    return {
      statusCode: 500,
      body: JSON.stringify({ error: 'Failed to proxy request to OpenAI' }),
      headers: { 'Content-Type': 'application/json' }
    };
  }
};
