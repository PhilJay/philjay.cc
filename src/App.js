import React from 'react';
import { BrowserRouter as Router, Route, Switch } from "react-router-dom";
import './App.css';
import About from './Components/About/About';
import Home from './Components/Home/Home';
import Imprint from './Components/Imprint/Imprint';
import BurndPrivacy from './Components/PrivacyAndTerms/Burnd/BurndPrivacy';
import BurndTerms from './Components/PrivacyAndTerms/Burnd/BurndTerms';
import Privacy from './Components/PrivacyAndTerms/Privacy';

function App(props) {

  document.title = "Philipp Jahoda | PhilJay";

  return (

    <div className="App">
      <header className="App-header">
      </header>

      <Router >
        {/* <SideMenu /> */}
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
          <Route path="/burnd-privacy-policy">
            <BurndPrivacy />
          </Route>
          <Route path="/terms-and-conditions-burnd">
            <BurndTerms />
          </Route>

          {/* If none of the previous routes render anything,
            this route acts as a fallback.

            Important: A route with path="/" will *always* match
            the URL because all URLs begin with a /. So that's
            why we put this one last of all */}
          <Route exact path="/">
            <Home />
          </Route>
        </Switch>
      </Router>

    </div>
  );
}

export default App;
