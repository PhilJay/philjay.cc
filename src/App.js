import React from 'react';
import { BrowserRouter as Router, Route, Switch, Link } from "react-router-dom";
import './App.css';
import About from './Components/About/About';
import FooterItem from './Components/FooterItem/FooterItem';
import Home from './Components/Home/Home';
import Privacy from './Components/Privacy/Privacy';
import Imprint from './Components/Imprint/Imprint';

function App(props) {

  return (

    <div className="App">
      <header className="App-header">
      </header>
      <Router>
        <Switch>
          <Route path="/about">
            <About />
          </Route>

          <Route path="/privacy-policy">
            <Privacy />
          </Route>

          <Route path="/imprint">
            <Imprint />
          </Route>

          {/* If none of the previous routes render anything,
            this route acts as a fallback.

            Important: A route with path="/" will *always* match
            the URL because all URLs begin with a /. So that's
            why we put this one last of all */}
          <Route path="/">
            <Home />
          </Route>
        </Switch>
      </Router>
     
    </div>
  );
}

export default App;
