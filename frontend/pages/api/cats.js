import axios from 'axios';

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

export default async function handler(req, res) {
  try {
    switch (req.method) {
      case 'GET':
        // Get all cats
        const response = await axios.get(`${BACKEND_URL}/cats/`);
        res.status(200).json(response.data);
        break;

      case 'POST':
        // Create new cat
        const createResponse = await axios.post(`${BACKEND_URL}/cats/`, req.body);
        res.status(201).json(createResponse.data);
        break;

      default:
        res.setHeader('Allow', ['GET', 'POST']);
        res.status(405).end(`Method ${req.method} Not Allowed`);
    }
  } catch (error) {
    // Forward the error from backend
    const status = error.response?.status || 500;
    const data = error.response?.data || { error: 'Internal Server Error' };
    res.status(status).json(data);
  }
}