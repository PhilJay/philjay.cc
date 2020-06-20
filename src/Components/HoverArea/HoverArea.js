import React from 'react';
import './HoverArea.css'


function HoverArea(props) {
    return <div className="hover-area" {...props}>
            {props.children}
        </div>
}

export default HoverArea;