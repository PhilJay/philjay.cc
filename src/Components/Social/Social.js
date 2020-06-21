import React from 'react';
import './Social.css'
import { withRouter } from "react-router-dom";

function Social(props) {

    const click = (item) => {
        if (item.route) {
            props.history.push(item.url);
        } else {
            window.open(item.url, "_blank");
        }
    }

    return <div className="social" onClick={() => { click(props.social) }}>
            <img className="social-image" src={props.social.image} />
            <p className="social-title">{props.social.name}</p>
        </div>
}

export default withRouter(Social);