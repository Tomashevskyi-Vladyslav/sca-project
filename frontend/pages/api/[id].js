import axios from 'axios';

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

export default async function handler(req, res) {
  const { id } = req.query;

  try {
    switch (req.method) {
      case 'PUT':
        // Update cat's salary
        const updateResponse = await axios.put(
          `${BACKEND_URL}/cats/${id}`,
          req.body
        );
        res.status(200).json(updateResponse.data);
        break;

      case 'DELETE':
        // Delete a cat
        await axios.delete(`${BACKEND_URL}/cats/${id}`);
        res.status(200).json({ message: 'Cat deleted successfully' });
        break;

      default:
        res.setHeader('Allow', ['PUT', 'DELETE']);
        res.status(405).end(`Method ${req.method} Not Allowed`);
    }
  } catch (error) {
    // Handle specific error cases
    if (error.response?.status === 400 && error.response.data?.detail?.includes('assigned to a mission')) {
      res.status(400).json({ 
        error: "Cannot delete cat assigned to a mission. Unassign them first." 
      });
    } else {
      const status = error.response?.status || 500;
      const data = error.response?.data || { error: 'Internal Server Error' };
      res.status(status).json(data);
    }
  }
}