import React, { useState } from 'react';
import axios from 'axios';

const AddChannel = ({ onAdd }) => {
  const [channelName, setChannelName] = useState('');

  const handleSubmit = async (event) => {
    event.preventDefault();
    try {
      await axios.post('http://localhost:5000/channels', { channelName });
      onAdd();
      setChannelName(''); // Reset input field after submission
    } catch (error) {
      console.error('Error adding channel:', error);
    }
  };

  return (
	<form onSubmit={handleSubmit} className="flex justify-center mb-4">
	  <input
		type="text"
		value={channelName}
		onChange={(e) => setChannelName(e.target.value)}
		placeholder="Enter channel name"
		className="px-4 py-2 mr-2 border rounded shadow"
		required
	  />
	  <button type="submit" className="px-4 py-2 bg-blue-500 text-white rounded shadow">
		Add Channel
	  </button>
	</form>
  );
};

export default AddChannel;
