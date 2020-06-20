import React from 'react';
import Project from '../Project/Project';
import './ProjectGrid.css'

const ProjectGrid = (props) => (
    <div className="project-grid">
      {props.projects.map((project) => (
        <div>
          <Project project={project}/>
        </div>
      ))}
    </div>
 )

 export default ProjectGrid;