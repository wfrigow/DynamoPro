const express = require('express');
const fetch = require('node-fetch');
const cors = require('cors');

const app = express();
app.use(cors());
app.use(express.json());

require('dotenv').config();
const OPENAI_API_KEY = process.env.OPENAI_API_KEY;
if (!OPENAI_API_KEY) {
  console.error('[ProxySimple] ERREUR: La clé OPENAI_API_KEY n\'est pas définie dans .env');
  process.exit(1);
}

app.post('/api/openai/v1/chat/completions', async (req, res) => {
  try {
    const headers = {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${OPENAI_API_KEY}`,
    };
    const response = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: headers,
      body: JSON.stringify(req.body),
    });
    const text = await response.text();
    try {
      const data = JSON.parse(text);
      res.status(response.status).json(data);
    } catch (err) {
      res.status(response.status).send(text);
    }
  } catch (error) {
    console.error('[ProxySimple] Erreur proxy:', error);
    res.status(500).json({ error: 'Erreur proxy vers OpenAI' });
  }
});

const PORT = 3001;
app.listen(PORT, () => {
  console.log(`Proxy Express ultra simple sur le port ${PORT}`);
});
