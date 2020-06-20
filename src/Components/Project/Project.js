import React from 'react';
import './Project.css'

const click = (project) => {
    window.open(project.url, "_blank");
}

function Project(props) {
    return <div className="project" onClick={() => { click(props.project) }}>
        <div className="project-content">
            <img className="project-image" src={props.project.image} />
            <h2>{props.project.name}</h2>
            <p className="project-desc">{props.project.description}</p>
        </div>
    </div>
}

export default Project;