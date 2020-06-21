import React from 'react';
import { BrowserRouter as Router, Route, Switch } from "react-router-dom";
import './App.css';
import About from './Components/About/About';
import Home from './Components/Home/Home';
import Imprint from './Components/Imprint/Imprint';
import Privacy from './Components/PrivacyAndTerms/Privacy';

function App(props) {

  document.title = "Philipp Jahoda | PhilJay";

  return (
    <div className="App">
      <header className="App-header">
      </header>

      <Router>
        {/* <SideMenu /> */}
        <Switch>
          <Route path="/about" component={About} />
          <Route path="/privacy-policy" component={Privacy} />
          <Route path="/imprint" component={Imprint} />
          <Route exact path="/" component={Home} />
        </Switch>
      </Router>

    </div>
  );
}

export default App;
