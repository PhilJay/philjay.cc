import React from 'react';
import './FooterItem.css'

function FooterItem(props) {
    return <div className="footer-item" {...props}>
            <p className="footer-item-title">{props.title}</p>
        </div>
}

export default FooterItem;