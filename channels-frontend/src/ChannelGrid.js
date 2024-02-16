import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Card from 'react-bootstrap/Card';
import Button from 'react-bootstrap/Button';

const ChannelGrid = () => {
  const [channels, setChannels] = useState([]);

  const fetchChannels = async () => {
    try {
      const response = await axios.get('http://localhost:5000/channels');
      setChannels(response.data);
    } catch (error) {
      console.error('Error fetching channels:', error);
    }
  };

  const deleteChannel = async (channelName) => {
    try {
      await axios.delete(`http://localhost:5000/channels?channelName=${channelName}`);
      fetchChannels(); // Refresh the list after deletion
    } catch (error) {
      console.error('Error deleting channel:', error);
    }
  };

  useEffect(() => {
    fetchChannels();
  }, []);

  return (
    <div className="d-flex flex-wrap">
      {channels.map((channel, index) => (
        <Card key={index} style={{ width: '18rem', margin: '10px' }}>
          <Card.Body>
            <Card.Title>{channel.channelName}</Card.Title>
            <Card.Text>
              <a href={channel.channelUrl} target="_blank" rel="noopener noreferrer">Visit Channel</a>
			  <p>{channel.channelOutputDirectory}</p>
            </Card.Text>
            <Button variant="danger" onClick={() => deleteChannel(channel.channelName)}>Delete</Button>
          </Card.Body>
        </Card>
      ))}
    </div>
  );
};

export default ChannelGrid;
