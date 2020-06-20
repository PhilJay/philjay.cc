import React from 'react';
import './Social.css'

const click = (url) => {
    window.open(url, "_blank");
}

function Social(props) {
    return <div className="social" onClick={() => { click(props.social.url) }}>
            <img className="social-image" src={props.social.image} />
            <p className="social-title">{props.social.name}</p>
        </div>
}

export default Social;