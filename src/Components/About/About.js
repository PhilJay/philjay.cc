
import React from 'react';
import './About.css';

function About(props) {
    return <div className="about">
        <div className="about-container">
            <h1>Philipp Jahoda</h1>
            <p>I am an avid software developer and entrepreneur. Off work I enjoy spending time with family and friends and an doing cycling or calisthenics workouts.</p>

            <h3>Favourite Tech Stack / Languages</h3>
            <ul>
                <li>
                    <p>Kotlin</p>
                    <p>Using it for Android and backend development (Spring)</p>
                </li>
                <li>
                    <p>Swift</p>
                    <p>Created my first Swift app in 2014 and couldn't stop since. Also used it for creating my first macOS app.</p>
                </li>
                <li>
                    <p>Java</p>
                    <p>Worked with Java for the last 10+ years. Projects included Android, Swing and backend (Spring).</p>
                </li>
                <li>
                    <p>Angular</p>
                    <p>Ceated my first application using Angular in 2020 - it's awesome. In the process I also worked with JavaScript & TypeScript.</p>
                </li>
                <li>
                    <p>React</p>
                    <p>One of my favourite frameworks for creating web UI.</p>
                </li>
                <li>
                    <p>MongoDB</p>
                    <p>I am an avid fan of NoSQL databases, working with MongoDB since 2014 for all projects requiring databases.</p>
                </li>
                <li>
                    <p>Docker</p>
                    <p>Using Docker ever since it became popular for all sorts of deployment processes.</p>
                </li>
                <li>
                    <p>C++</p>
                    <p>Occasionally used (created a C++ server application in 2013, for transferring data between game clients).</p>
                </li>
                <li>
                    <p>C#</p>
                    <p>Even though not my favourite anymore, I gained my first coding experience back in 2007 using C#.</p>
                </li>
            </ul>

            <h3>Off Coding</h3>
            <p>When not actively coding, I also enjoy these.</p>
            <ul>
                <li>
                    <p>Lecturing</p>
                    <p>Held multiple university lectures about software development, version control and project management.</p>
                </li>
                <li>
                    <p>Entrepreneurship</p>
                    <p>Co-Founded international startups in Austria & Denmark.</p>
                </li>
                <li>
                    <p>Leadership</p>
                    <p>Managed an agile team of multiple developers as CTO, Sprint planning, JIRA issue tracking.</p>
                </li>
            </ul>
        </div>


    </div>
}

export default About;