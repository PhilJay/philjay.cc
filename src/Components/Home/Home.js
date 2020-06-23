import React from 'react';
import './Home.css'
import ProjectGrid from '../ProjectGrid/ProjectGrid';
import Social from '../Social/Social';
import { Link } from 'react-router-dom';

function Home(props) {

  const projects = [
    { name: "Butleroy", image: require('./../../images/butleroy.png'), description: "Butleroy combines Calendar & To-Dos 🗓️ with smart scheduling 💡.", url: "https://butleroy.com" },
    { name: "Burnd", image: require('./../../images/burnd.png'), description: "Burnd is an app for HIIT (High Intensity Interval Training) 🔥.", url: "https://philjay.github.io/burnd-app/" },
    { name: "MPAndroidChart", image: require('./../../images/mpandroidchart.png'), description: "A powerful 🚀 Android chart view / graph view library.", url: "https://github.com/PhilJay/MPAndroidChart" },
    { name: "JWT", image: require('./../../images/jwt.png'), description: "Json Web Token 🔑 library for APNs (Apple Push) or Sign in with Apple.", url: "https://github.com/PhilJay/JWT" },
    { name: "Spring Angular", image: require('./../../images/spring_angular.png'), description: "Spring 🍃 | Angular 🅰️ | MongoDB with Material UI, OAuth2 and Docker 🐳.", url: "https://github.com/PhilJay/SpringAngular" },
  ]

  const socials = [
    { name: "About", image: require('./../../images/about.png'), url: "/about", route: true },
    { name: "Twitter", image: require('./../../images/twitter.png'), url: "https://twitter.com/philippjahoda" },
    { name: "GitHub", image: require('./../../images/github.png'), url: "https://github.com/PhilJay" },
    { name: "LinkedIn", image: require('./../../images/linkedin.png'), url: "https://www.linkedin.com/in/philippjahoda/" }
  ]

  return (

    <div className="home">

      <div className="home-header">
        <h1 className="name-h1">Philipp Jahoda</h1>
        <p>Software Developer & Entrepreneur</p>
        
      </div>

      <div className="socials">
        {socials.map((social) => (
          <div key={social.name}>
            <Social social={social} />
          </div>
        ))}
      </div>


      <div className="section-divider"></div>
      <h1 className="projects-h1">Projects</h1>
      <p>Exciting things I'm currently working on 😅</p>
      <ProjectGrid projects={projects} />

      <div className="section-divider"></div>

      <div className="home-footer">
        <Link className="router-link" to="/privacy-policy">Privacy Policy</Link>
        <Link className="router-link" to="/imprint">Imprint</Link>
      </div>
    </div>
  );
}

export default Home;