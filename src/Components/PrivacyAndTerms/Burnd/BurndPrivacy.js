
import React from 'react';
import './BurndPrivacy.css';

function BurndPrivacy(props) {
    return <div className="burnd-privacy-policy">
        <div className="burnd-privacy-policy-container">
            <h1>Burnd | Privacy Policy</h1>

            <h3><strong>In short words</strong></h3>
            <p>Your privacy is important to us.</p>
            <p>This policy applies to all information collected or submitted on the Burnd application (“Burnd”, the “App”).</p>
            
            <h3><strong>Data Storage</strong></h3>
            <p>The app is using the Apple framework Core Data to store your data locally on your device. To synchronise data between devices Burnd is using Apple’s CloudKit service. If you have iCloud services enabled Burnd will store your data in your private CloudKit container. Data saved to iCloud can not be accessed by us. Apple’s Privacy Policy can be&nbsp;<a href="https://www.apple.com/legal/privacy/en-ww/">found here</a>.</p>
            
            <h3><strong>Payment Data</strong></h3>
            <p>Burnd uses RevenueCat to manage auto-renewable subscriptions and trial versions. RevenueCat’s Privacy Policy can be&nbsp;<a href="https://www.revenuecat.com/privacy">found here</a>.</p>
            <p>Burnd uses a randomly generated identifier to identify devices and users anonymously. Your anonymous user identifier is derived from your iCloud service (if enabled) and is associated with data sent to RevenueCat. This makes sharing subscriptions between devices more seamless.</p>
            
            <h3><strong>California Online Privacy Protection Act Compliance</strong></h3>
            <p>We comply with the California Online Privacy Protection Act. We therefore will not distribute your personal information to outside parties without your consent.</p>

            <h3><strong>International Transfers of Information</strong></h3>
            <p>Information may be processed, stored, and used outside of the country in which you are located. Data privacy laws vary across jurisdictions, and different laws may be applicable to your data depending on where it is processed, stored, or used.</p>

            <h3><strong>Your Consent</strong></h3>
            <p>By using our site or apps, you consent to our privacy policy.</p>

            <h3><strong>Contact Information</strong></h3>
            <p>If you have questions regarding this privacy policy, you may email gregorpich@gmail.com.</p>

            <h3><strong>Changes to this policy</strong></h3>
            <p>We reserve the right to update our privacy policy in the future. Visit our privacy policy frequently to always be aware of the policy you are agreeing to by using our services. We will post changes made to the privacy policy on this page. Summary of changes so far:</p>

            <p>– May 26, 2020: First published.</p>
        </div>
    </div>
}

export default BurndPrivacy;