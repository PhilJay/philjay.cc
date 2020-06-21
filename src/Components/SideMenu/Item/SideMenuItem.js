import React from 'react';
import './SideMenuItem.css'


function SideMenuItem(props) {
    return <div className="side-menu-item" onClick={ () => { props.item.action() } }>
        <img src={props.item.image}></img>
        <p className="side-menu-item-title">{props.item.title}</p>
    </div>
}

export default SideMenuItem;