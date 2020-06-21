import React from 'react';
import './SideMenu.css'
import SideMenuItem from './Item/SideMenuItem';
import { withRouter } from "react-router-dom";


function SideMenu(props) {

    const items = [
        {title: "About", image: require('./../../images/about.png'), action: () => { props.history.push("/about"); }},
        {title: "Contact", image: require('./../../images/contact.png'), action: () => { window.location.href = "mailto:philjay.librarysup@gmail.com"; }}
    ]

    return <div className="side-menu">
        {items.map((item) => (
        <div>
          <SideMenuItem item={item}/>
        </div>
      ))}
    </div>
}

export default withRouter(SideMenu);