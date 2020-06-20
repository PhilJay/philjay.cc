import React from 'react';
import './App.css';
import ProjectGrid from './Components/ProjectGrid/ProjectGrid'
import Social from './Components/Social/Social';
import FooterItem from './Components/FooterItem/FooterItem';

function App() {

  const projects = [
    { name: "Butleroy", image: require('./images/butleroy.png'), description: "Butleroy combines Calendar & To-Dos with smart scheduling.", url: "https://butleroy.com" },
    { name: "Burnd", image: require('./images/burnd.png'), description: "Burnd is an app for HIIT (High Intensity Interval Training).", url: "" },
    { name: "MPAndroidChart", image: require('./images/mpandroidchart.png'), description: "A powerful 🚀 Android chart view / graph view library.", url: "https://github.com/PhilJay/MPAndroidChart" },
    { name: "JWT", image: require('./images/jwt.png'), description: "Json Web Token 🔑 library for APNs (Apple Push) or Sign in with Apple.", url: "https://github.com/PhilJay/JWT" }
  ]

  const socials = [
    { name: "Twitter", image: require('./images/twitter.png'), url: "https://twitter.com/philippjahoda" },
    { name: "GitHub", image: require('./images/github.png'), url: "https://github.com/PhilJay" }
  ]

  return (

    <div className="App">
      <header className="App-header">
      </header>
      <h1 className="name-h1">Philipp Jahoda</h1>
      <p>Software Developer & Entrepreneur</p>
      <div className="socials">
      {socials.map((social) => (
        <div>
          <Social social={social} />
        </div>
      ))}
      </div>
      

      <div className="section-divider"></div>
      <h1 className="projects-h1">Projects</h1>
      <p>Exciting things im currently working on 😅</p>
      <ProjectGrid projects={projects} />

      <div className="section-divider"></div>
      <div className="App-footer">
          <FooterItem title="Privacy Policy"/>
          <FooterItem title="Imprint"/>
      </div>
    </div>
  );
}

export default App;
