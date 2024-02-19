import logo from './logo.webp';
import './App.css';
import ChannelGrid from './ChannelGrid';
import AddChannel from './AddChannel';
import 'bootstrap/dist/css/bootstrap.min.css';

function App() {
  const refreshChannels = () => {
    // This function will be passed to AddChannel to trigger a refresh of the channel list
    window.location.reload();
  };

  return (
    <div>
      <h1>Channels</h1>
      <AddChannel onAdd={refreshChannels} />
      <ChannelGrid />
    </div>
  );
}

export default App;