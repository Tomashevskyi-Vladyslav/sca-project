// pages/cats/index.js
import { useState, useEffect } from 'react';

export default function SpyCatsDashboard() {
  const [cats, setCats] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [formData, setFormData] = useState({
    name: '',
    years_of_experience: 0,
    breed: '',
    salary: 0
  });
  const [editingCat, setEditingCat] = useState(null);
  const [editSalary, setEditSalary] = useState('');

  useEffect(() => {
    fetchCats();
  }, []);

  const fetchCats = async () => {
    try {
      const response = await fetch('/api/cats');
      if (!response.ok) throw new Error('Failed to fetch cats');
      const data = await response.json();
      setCats(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'years_of_experience' || name === 'salary' 
        ? Number(value) : value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    
    try {
      const response = await fetch('/api/cats', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to create cat');
      }
      
      const newCat = await response.json();
      setCats(prev => [...prev, newCat]);
      setFormData({
        name: '',
        years_of_experience: 0,
        breed: '',
        salary: 0
      });
    } catch (err) {
      setError(err.message);
    }
  };

  const handleEdit = (cat) => {
    setEditingCat(cat);
    setEditSalary(cat.salary);
  };

  const handleSaveEdit = async () => {
    if (!editingCat) return;
    
    try {
      const response = await fetch(`/api/cats/${editingCat.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ salary: parseFloat(editSalary) })
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to update cat');
      }
      
      setCats(prev => prev.map(cat => 
        cat.id === editingCat.id ? { ...cat, salary: parseFloat(editSalary) } : cat
      ));
      setEditingCat(null);
      setEditSalary('');
    } catch (err) {
      setError(err.message);
    }
  };

  const handleDelete = async (catId) => {
    if (!window.confirm('Are you sure you want to delete this spy cat?')) return;
    
    try {
      const response = await fetch(`/api/cats/${catId}`, {
        method: 'DELETE'
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to delete cat');
      }
      
      setCats(prev => prev.filter(cat => cat.id !== catId));
    } catch (err) {
      setError(err.message);
    }
  };

  if (loading) return <p>Loading spy cats...</p>;

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">Spy Cat Agency Dashboard</h1>
      
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}
      
      <div className="mb-12">
        <h2 className="text-2xl font-semibold mb-4">Add New Spy Cat</h2>
        <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block mb-2">Name</label>
            <input
              type="text"
              name="name"
              value={formData.name}
              onChange={handleInputChange}
              className="w-full p-2 border rounded"
              required
            />
          </div>
          <div>
            <label className="block mb-2">Years of Experience</label>
            <input
              type="number"
              name="years_of_experience"
              value={formData.years_of_experience}
              onChange={handleInputChange}
              className="w-full p-2 border rounded"
              min="0"
              required
            />
          </div>
          <div>
            <label className="block mb-2">Breed</label>
            <input
              type="text"
              name="breed"
              value={formData.breed}
              onChange={handleInputChange}
              className="w-full p-2 border rounded"
              required
            />
          </div>
          <div>
            <label className="block mb-2">Salary ($)</label>
            <input
              type="number"
              name="salary"
              value={formData.salary}
              onChange={handleInputChange}
              className="w-full p-2 border rounded"
              min="0"
              step="0.01"
              required
            />
          </div>
          <div className="md:col-span-2">
            <button
              type="submit"
              className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
            >
              Add Spy Cat
            </button>
          </div>
        </form>
      </div>
      
      <div>
        <h2 className="text-2xl font-semibold mb-4">Spy Cats</h2>
        <div className="overflow-x-auto">
          <table className="min-w-full bg-white border">
            <thead>
              <tr>
                <th className="py-2 px-4 border-b">Name</th>
                <th className="py-2 px-4 border-b">Experience</th>
                <th className="py-2 px-4 border-b">Breed</th>
                <th className="py-2 px-4 border-b">Salary</th>
                <th className="py-2 px-4 border-b">Actions</th>
              </tr>
            </thead>
            <tbody>
              {cats.length === 0 ? (
                <tr>
                  <td colSpan="5" className="py-4 px-4 border-b text-center">
                    No spy cats found
                  </td>
                </tr>
              ) : (
                cats.map(cat => (
                  <tr key={cat.id}>
                    <td className="py-2 px-4 border-b">{cat.name}</td>
                    <td className="py-2 px-4 border-b">{cat.years_of_experience} years</td>
                    <td className="py-2 px-4 border-b">{cat.breed}</td>
                    <td className="py-2 px-4 border-b">
                      {editingCat?.id === cat.id ? (
                        <input
                          type="number"
                          value={editSalary}
                          onChange={(e) => setEditSalary(e.target.value)}
                          className="w-full p-1 border rounded"
                          min="0"
                          step="0.01"
                        />
                      ) : (
                        `$${cat.salary.toFixed(2)}`
                      )}
                    </td>
                    <td className="py-2 px-4 border-b">
                      {editingCat?.id === cat.id ? (
                        <div className="flex space-x-2">
                          <button
                            onClick={handleSaveEdit}
                            className="bg-green-500 text-white px-2 py-1 rounded text-sm"
                          >
                            Save
                          </button>
                          <button
                            onClick={() => setEditingCat(null)}
                            className="bg-gray-500 text-white px-2 py-1 rounded text-sm"
                          >
                            Cancel
                          </button>
                        </div>
                      ) : (
                        <div className="flex space-x-2">
                          <button
                            onClick={() => handleEdit(cat)}
                            className="bg-yellow-500 text-white px-2 py-1 rounded text-sm"
                          >
                            Edit Salary
                          </button>
                          <button
                            onClick={() => handleDelete(cat.id)}
                            className="bg-red-500 text-white px-2 py-1 rounded text-sm"
                          >
                            Delete
                          </button>
                        </div>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}